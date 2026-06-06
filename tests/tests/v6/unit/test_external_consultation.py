"""
test_external_consultation.py — 同步外部咨询单元测试（TDD 红端）

测试覆盖：
- 正常返回：30s 内拿到结果
- 超时降级：超过 30s 返回 None
- 每轮上限 2 次：第 3 次调用抛错
- 失败历史：who/when/why/response 完整记录

Expected: backend2 实现外部咨询模块后，这些测试应通过（变绿）
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime


# ============================================================================
# Mock 数据结构
# ============================================================================

@dataclass
class MockConsultationResult:
    """Mock result from external consultation."""
    expert_id: str
    response: str
    timestamp: datetime
    success: bool


@dataclass  
class MockConsultationFailure:
    """Mock failure record."""
    who: str
    when: datetime
    why: str
    response: Optional[str]


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def external_consult_module():
    """Import external consultation module."""
    try:
        from src.v6.support.external_consultation import (
            ExternalConsultation,
            ConsultationManager,
            get_consultation_manager
        )
        return ExternalConsultation, ConsultationManager, get_consultation_manager
    except ImportError:
        pytest.skip("ExternalConsultation module not yet implemented")


@pytest.fixture
def consultation_manager(external_consult_module):
    """Create a fresh consultation manager."""
    _, _, get_manager = external_consult_module
    return get_consultation_manager()


@pytest.fixture
def mock_llm_response():
    """Factory for mock LLM responses."""
    def _create(response: str = "这是一条模拟回复", delay: float = 0.0):
        mock = Mock()
        mock.generate = Mock(return_value=response)
        return mock
    return _create


@pytest.fixture
def sample_question():
    """Sample question for consultation."""
    return "是否应该采用微服务架构？"


# ============================================================================
# Test Cases
# ============================================================================

class TestNormalResponse:
    """Test normal consultation response within timeout."""
    
    def test_response_within_30_seconds(self, external_consult_module, mock_llm_response):
        """验证正常响应在 30 秒内返回"""
        ExternalConsultation, _, _ = external_consult_module
        
        llm = mock_llm_response("快速响应")
        consultation = ExternalConsultation(llm=llm)
        
        start = time.time()
        result = consultation.ask(
            expert_id="oracle",
            prompt="测试问题"
        )
        elapsed = time.time() - start
        
        assert result is not None
        assert elapsed < 30.0, f"Response took {elapsed:.2f}s, expected < 30s"
    
    def test_response_contains_text(self, external_consult_module, mock_llm_response):
        """验证返回结果包含文本内容"""
        ExternalConsultation, _, _ = external_consult_module
        
        expected_text = "这是专家咨询的回复"
        llm = mock_llm_response(expected_text)
        consultation = ExternalConsultation(llm=llm)
        
        result = consultation.ask(
            expert_id="oracle",
            prompt="测试问题"
        )
        
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_consultation_uses_provided_expert_id(self, external_consult_module, mock_llm_response):
        """验证咨询使用了提供的 expert_id"""
        ExternalConsultation, _, _ = external_consult_module
        
        llm = mock_llm_response("回复")
        consultation = ExternalConsultation(llm=llm)
        
        result = consultation.ask(
            expert_id="my_custom_oracle",
            prompt="测试问题"
        )
        
        assert result is not None


class TestTimeoutHandling:
    """Test timeout and degradation behavior."""
    
    def test_timeout_returns_none(self, external_consult_module):
        """验证超时后返回 None（降级）"""
        ExternalConsultation, _, _ = external_consult_module
        
        # Create a slow LLM mock
        slow_llm = Mock()
        def slow_generate(*args, **kwargs):
            time.sleep(35)  # Simulate slow LLM
            return "响应"
        slow_llm.generate = slow_generate
        
        consultation = ExternalConsultation(llm=slow_llm, timeout=30)
        
        result = consultation.ask(
            expert_id="slow_oracle",
            prompt="超时测试"
        )
        
        assert result is None
    
    def test_timeout_triggers_graceful_degradation(self, external_consult_module):
        """验证超时触发优雅降级（不抛异常）"""
        ExternalConsultation, _, _ = external_consult_module
        
        slow_llm = Mock()
        slow_llm.generate = Mock(side_effect=TimeoutError("LLM timeout"))
        
        consultation = ExternalConsultation(llm=slow_llm, timeout=30)
        
        # Should not raise, just return None
        result = consultation.ask(
            expert_id="error_oracle",
            prompt="超时测试"
        )
        
        assert result is None
    
    @patch('time.time')
    def test_timeout_respects_configured_value(self, mock_time, external_consult_module):
        """验证超时时间由配置决定"""
        ExternalConsultation, _, _ = external_consult_module
        
        # Mock time to simulate 31 seconds passing
        mock_time.side_effect = [0, 31]
        
        slow_llm = Mock()
        slow_llm.generate = Mock(return_value="响应")
        
        consultation = ExternalConsultation(llm=slow_llm, timeout=30)
        
        result = consultation.ask(
            expert_id="timeout_test",
            prompt="测试"
        )
        
        # Should timeout after 30s
        assert result is None


class TestPerRoundLimit:
    """Test per-round consultation limit (max 2 per round)."""
    
    def test_first_two_consultations_succeed(self, external_consult_module, mock_llm_response):
        """验证每轮前 2 次咨询成功"""
        ExternalConsultation, _, _ = external_consult_module
        
        llm = mock_llm_response("回复")
        consultation = ExternalConsultation(llm=llm, max_per_round=2)
        
        result1 = consultation.ask(expert_id="oracle", prompt="问题1")
        result2 = consultation.ask(expert_id="oracle", prompt="问题2")
        
        assert result1 is not None
        assert result2 is not None
    
    def test_third_consultation_raises_error(self, external_consult_module, mock_llm_response):
        """验证第 3 次咨询抛出错误"""
        ExternalConsultation, _, _ = external_consult_module
        
        llm = mock_llm_response("回复")
        consultation = ExternalConsultation(llm=llm, max_per_round=2)
        
        consultation.ask(expert_id="oracle", prompt="问题1")
        consultation.ask(expert_id="oracle", prompt="问题2")
        
        # Third call should raise
        with pytest.raises((ValueError, RuntimeError)):
            consultation.ask(expert_id="oracle", prompt="问题3")
    
    def test_limit_is_per_round(self, external_consult_module, mock_llm_response):
        """验证限制是按轮计算的"""
        ExternalConsultation, _, _ = external_consult_module
        
        llm = mock_llm_response("回复")
        consultation = ExternalConsultation(llm=llm, max_per_round=2)
        
        # Round 1: 2 calls OK
        consultation.ask(expert_id="oracle", prompt="问题1")
        consultation.ask(expert_id="oracle", prompt="问题2")
        
        # Start new round
        consultation.start_round()
        
        # Round 2: Should allow 2 more calls
        result1 = consultation.ask(expert_id="oracle", prompt="问题3")
        result2 = consultation.ask(expert_id="oracle", prompt="问题4")
        
        assert result1 is not None
        assert result2 is not None
    
    def test_limit_resets_on_new_round(self, external_consult_module, mock_llm_response):
        """验证新轮次重置限制计数"""
        ExternalC
