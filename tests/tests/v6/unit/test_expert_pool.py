"""
test_expert_pool.py — ExpertPool 单元测试（TDD 红端）

测试覆盖：
- add_expert / remove_expert 正确性
- list_active 返回当前活跃专家 ID
- consult(expert_id, prompt) 同步阻塞返回字符串
- snapshot() 导出当前状态

Expected: backend2 实现 ExpertPool 后，这些测试应通过（变绿）
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any


# ============================================================================
# Mock Expert 类（测试替身）
# ============================================================================

class MockExpertForPool:
    """Mock Expert for ExpertPool tests."""
    
    def __init__(
        self,
        expert_id: str = "test_expert",
        name: str = "Test Expert",
        perspective: str = "测试视角"
    ):
        self.expert_id = expert_id
        self.name = name
        self.perspective = perspective
        self.call_count = 0
    
    def respond(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """模拟专家响应"""
        self.call_count += 1
        return f"[{self.name}] 响应 #{self.call_count}: {prompt}"


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def expert_pool_module():
    """Import ExpertPool from src.v6.support.expert_pool."""
    try:
        from src.v6.support.expert_pool import ExpertPool
        return ExpertPool
    except ImportError:
        pytest.skip("ExpertPool module not yet implemented")


@pytest.fixture
def expert_pool(expert_pool_module):
    """Create a fresh ExpertPool instance."""
    return expert_pool_module()


@pytest.fixture
def sample_experts():
    """Factory to create sample experts."""
    def _create(count: int = 3):
        return [
            MockExpertForPool(
                expert_id=f"expert_{i}",
                name=f"专家{i}",
                perspective=f"视角{i}"
            )
            for i in range(1, count + 1)
        ]
    return _create


# ============================================================================
# Test Cases
# ============================================================================

class TestExpertPoolAddRemove:
    """Test add_expert and remove_expert operations."""
    
    def test_add_single_expert(self, expert_pool, sample_experts):
        """验证添加单个专家后可以被查询到"""
        experts = sample_experts(1)
        expert_pool.add_expert(experts[0])
        
        active = expert_pool.list_active()
        assert "expert_1" in active
        assert len(active) == 1
    
    def test_add_multiple_experts(self, expert_pool, sample_experts):
        """验证添加多个专家后都能被查询到"""
        experts = sample_experts(5)
        for expert in experts:
            expert_pool.add_expert(expert)
        
        active = expert_pool.list_active()
        assert len(active) == 5
        for i in range(1, 6):
            assert f"expert_{i}" in active
    
    def test_remove_existing_expert(self, expert_pool, sample_experts):
        """验证移除已存在的专家后不再出现在活跃列表"""
        experts = sample_experts(3)
        for expert in experts:
            expert_pool.add_expert(expert)
        
        expert_pool.remove_expert("expert_2")
        
        active = expert_pool.list_active()
        assert "expert_2" not in active
        assert len(active) == 2
    
    def test_remove_nonexistent_expert_no_error(self, expert_pool):
        """验证移除不存在的专家不抛出异常"""
        # Should not raise
        expert_pool.remove_expert("nonexistent_id")
        assert True  # Pass if no exception
    
    def test_add_duplicate_expert_replaces(self, expert_pool, sample_experts):
        """验证添加相同 ID 的专家会替换旧的"""
        experts = sample_experts(2)
        expert_pool.add_expert(experts[0])
        expert_pool.add_expert(experts[1])  # Same ID as expert_1
        
        # Should have only one, but updated
        active = expert_pool.list_active()
        assert len(active) == 1


class TestExpertPoolConsult:
    """Test consult operation."""
    
    def test_consult_returns_string(self, expert_pool, sample_experts):
        """验证 consult 返回字符串类型的响应"""
        experts = sample_experts(1)
        expert_pool.add_expert(experts[0])
        
        response = expert_pool.consult("expert_1", "测试问题")
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_consult_blocking_behavior(self, expert_pool, sample_experts):
        """验证 consult 是同步阻塞的（立即返回）"""
        experts = sample_experts(1)
        expert_pool.add_expert(experts[0])
        
        import time
        start = time.time()
        response = expert_pool.consult("expert_1", "测试问题")
        elapsed = time.time() - start
        
        assert isinstance(response, str)
        # Should return quickly (within 1 second)
        assert elapsed < 1.0
    
    def test_consult_nonexistent_raises(self, expert_pool):
        """验证咨询不存在的专家抛出 KeyError"""
        with pytest.raises(KeyError):
            expert_pool.consult("nonexistent_id", "测试问题")
    
    def test_consult_increments_call_count(self, expert_pool, sample_experts):
        """验证每次咨询都增加专家的调用计数"""
        experts = sample_experts(1)
        expert_pool.add_expert(experts[0])
        
        expert_pool.consult("expert_1", "问题1")
        expert_pool.consult("expert_1", "问题2")
        
        assert experts[0].call_count == 2


class TestExpertPoolSnapshot:
    """Test snapshot functionality."""
    
    def test_snapshot_returns_dict(self, expert_pool, sample_experts):
        """验证 snapshot 返回字典类型"""
        experts = sample_experts(2)
        for expert in experts:
            expert_pool.add_expert(expert)
        
        snapshot = expert_pool.snapshot()
        
        assert isinstance(snapshot, dict)
    
    def test_snapshot_contains_expert_ids(self, expert_pool, sample_experts):
        """验证 snapshot 包含所有活跃专家 ID"""
        experts = sample_experts(3)
        for expert in experts:
            expert_pool.add_expert(expert)
        
        snapshot = expert_pool.snapshot()
        
        assert "experts" in snapshot
        assert isinstance(snapshot["experts"], list)
        assert len(snapshot["experts"]) == 3
    
    def test_snapshot_contains_metadata(self, expert_pool, sample_experts):
        """验证 snapshot 包含时间戳等元数据"""
        experts = sample_experts(2)
        for expert in experts:
            expert_pool.add_expert(expert)
        
        snapshot = expert_pool.snapshot()
        
        assert "timestamp" in snapshot or "created_at" in snapshot
    
    def test_empty_pool_snapshot(self, expert_pool):
        """验证空池的 snapshot 正常工作"""
        snapshot = expert_pool.snapshot()
        
        assert isinstance(snapshot, dict)
        assert "experts" in snapshot
        assert len(snapshot["experts"]) == 0


class TestExpertPoolEdgeCases:
    """Test edge cases and error handling."""
    
    def test_list_active_empty(self, expert_pool):
        """验证空池的 list_active 返回空列表"""
        active = expert_pool.list_active()
        assert active == [] or active == set()
    
    def test_add_after_remove(self, expert_pool, sample_experts):
        """验证移除后可以重新添加相同 ID"""
        experts = sample_experts(2)
        expert_pool.add_expert(experts[0])
        expert_pool.remove_expert("expert_1")
        expert_pool.add_expert(experts[1])  # New instance, same ID
        
        active = expert_pool.list_active()
        assert "expert_1" in active
        assert len(active) == 1
