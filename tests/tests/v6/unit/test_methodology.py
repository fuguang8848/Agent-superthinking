"""
test_methodology.py — MethodologyProvider 单元测试（TDD 红端）

测试覆盖：
- 18 个方法论都能注册
- apply(claim, context) -> Verdict 返回值符合协议
- "我用 X 方法论检验" 声明解析正确

Expected: backend2 实现 MethodologyProvider 后，这些测试应通过（变绿）
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any, List
from enum import Enum


# ============================================================================
# Mock Verdict 类（测试替身）
# ============================================================================

class VerdictResult(Enum):
    """Verdict result types."""
    SUPPORT = "support"
    REFUTE = "refute"
    NEUTRAL = "neutral"
    INCONCLUSIVE = "inconclusive"


class MockVerdict:
    """Mock Verdict object matching the protocol."""
    
    def __init__(
        self,
        result: VerdictResult,
        reasoning: str,
        method: str,
        confidence: float = 0.8
    ):
        self.result = result
        self.reasoning = reasoning
        self.method = method
        self.confidence = confidence
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "result": self.result.value,
            "reasoning": self.reasoning,
            "method": self.method,
            "confidence": self.confidence
        }


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def methodology_module():
    """Import MethodologyProvider from src.v6.support.methodology."""
    try:
        from src.v6.support.methodology import MethodologyProvider
        return MethodologyProvider
    except ImportError:
        pytest.skip("MethodologyProvider module not yet implemented")


@pytest.fixture
def methodology_provider(methodology_module):
    """Create a fresh MethodologyProvider instance."""
    return methodology_module()


@pytest.fixture
def sample_claim():
    """Sample claim for testing."""
    return {
        "content": "我们应该采用微服务架构来提高系统可扩展性",
        "expert_id": "tech_architect",
        "round": 1
    }


@pytest.fixture
def sample_context():
    """Sample context for method application."""
    return {
        "question": "是否应该采用微服务架构？",
        "arguments": [
            {"content": "微服务可以独立部署", "expert_id": "expert1"},
            {"content": "运维复杂度会增加", "expert_id": "expert2"}
        ],
        "history": []
    }


# ============================================================================
# 18 个方法论列表
# ============================================================================

METHODOLOGY_LIST = [
    "逻辑谬误检测",
    "因果关系分析",
    "利弊分析",
    "成本效益分析",
    "风险评估",
    "历史案例分析",
    "对比分析",
    "假设验证",
    "专家意见引用",
    "数据驱动分析",
    "利益相关者分析",
    "情景分析",
    "逆向思维",
    "第一性原理",
    "系统思考",
    "博弈论分析",
    "价值链分析",
    "SWOT分析"
]


# ============================================================================
# Test Cases
# ============================================================================

class TestMethodologyRegistration:
    """Test that all 18 methodologies are registered."""
    
    def test_register_all_18_methods(self, methodology_provider):
        """验证所有 18 个方法论都已注册"""
        registered = methodology_provider.list_methods()
        
        assert len(registered) >= 18, f"Expected >=18 methods, got {len(registered)}"
        
        # Check that key methods exist
        for method_name in METHODOLOGY_LIST:
            assert method_name in registered, f"Missing method: {method_name}"
    
    def test_register_specific_methods(self, methodology_provider):
        """验证关键方法论都能被查询到"""
        critical_methods = [
            "第一性原理",
            "因果关系分析",
            "成本效益分析",
            "风险评估",
            "SWOT分析"
        ]
        
        for method in critical_methods:
            assert method in methodology_provider.list_methods()
    
    def test_method_metadata_available(self, methodology_provider):
        """验证方法论元数据（描述、参数）可用"""
        methods = methodology_provider.list_methods()
        
        for method_name in methods[:5]:  # Check first 5
            metadata = methodology_provider.get_method_metadata(method_name)
            assert metadata is not None
            assert "description" in metadata or "name" in metadata


class TestApplyMethod:
    """Test apply method returns correct Verdict."""
    
    def test_apply_returns_verdict(self, methodology_provider, sample_claim, sample_context):
        """验证 apply() 返回 Verdict 类型"""
        verdict = methodology_provider.apply(
            claim=sample_claim["content"],
            method="因果关系分析",
            context=sample_context
        )
        
        assert verdict is not None
        assert hasattr(verdict, "result")
        assert hasattr(verdict, "reasoning")
        assert hasattr(verdict, "method")
    
    def test_apply_verdict_has_valid_result(self, methodology_provider, sample_claim, sample_context):
        """验证 Verdict.result 是有效的枚举值"""
        verdict = methodology_provider.apply(
            claim=sample_claim["content"],
            method="利弊分析",
            context=sample_context
        )
        
        valid_results = [r.value for r in VerdictResult]
        assert verdict.result in valid_results
    
    def test_apply_verdict_has_reasoning(self, methodology_provider, sample_claim, sample_context):
        """验证 Verdict.reasoning 是非空字符串"""
        verdict = methodology_provider.apply(
            claim=sample_claim["content"],
            method="逻辑谬误检测",
            context=sample_context
        )
        
        assert isinstance(verdict.reasoning, str)
        assert len(verdict.reasoning) > 0
    
    def test_apply_verdict_has_confidence(self, methodology_provider, sample_claim, sample_context):
        """验证 Verdict 包含置信度分数（0-1之间）"""
        verdict = methodology_provider.apply(
            claim=sample_claim["content"],
            method="数据驱动分析",
            context=sample_context
        )
        
        assert hasattr(verdict, "confidence")
        assert 0.0 <= verdict.confidence <= 1.0
    
    def test_apply_different_methods_different_results(self, methodology_provider, sample_claim, sample_context):
        """验证不同方法论对同一 claim 产生不同推理"""
        method1 = "第一性原理"
        method2 = "博弈论分析"
        
        verdict1 = methodology_provider.apply(sample_claim["content"], method1, sample_context)
        verdict2 = methodology_provider.apply(sample_claim["content"], method2, sample_context)
        
        # Different methods should produce different reasoning
        assert verdict1.reasoning != verdict2.reasoning


class TestMethodDeclarationParsing:
    """Test parsing of method declaration patterns."""
    
    def test_parse_method_declaration_full_pattern(self, methodology_provider):
        """验证完整声明解析：'我用 X 方法论检验'"""
        text = "我用因果关系分析检验这个结论"
        
        parsed = methodology_provider.parse_declaration(text)
        
        assert parsed is not None
        assert parsed["method"] == "因果关系分析"
        assert parsed["found"] is True
    
    def test_parse_method_declaration_partial(self, methodology_provider):
        """验证部分声明解析：'通过 X 分析'"""
        text = "通过成本效益分析，我认为..."
        
        parsed = methodology_provider.parse_declaration(text)
        
        assert parsed is not None
        assert "cost" in parsed["method"].lower() or "成本" in parsed["method"]
    
    def test_parse_no_method_declaration(self, methodology_provider):
        """验证无方法论声明时返回 None 或 not found"""
        text = "我认为这个方案很好"
        
        parsed = methodology_provider.parse_declaration(text)
        
        assert parsed is None or parsed.get("found") is False
    
    def test_parse_invalid_method_returns_none(self, methodology_provider):
        """验证无效方法名返回 None"""
        text = "我用不存在的某方法检验"
        
        parsed = methodology_provider.parse_declaration(text)
        
        assert parsed is None or parsed.get("found") is False


class TestSpecificMethodologyCoverage:
    """Test that each of the 18 methodologies produces a valid verdict."""

    @pytest.mark.parametrize("method_name", METHODOLOGY_LIST)
    def test_each_method_returns_valid_verdict(self, methodology_provider, sample_claim, sample_context, method_name):
        """验证每个方法论都能返回有效判决"""
        verdict = methodology_provider.apply(
            claim=sample_claim["content"],
            method=method_name,
            context=sample_context
        )

        assert verdict is not None
        assert hasattr(verdict, "result")
        assert hasattr(verdict, "reasoning")
        assert hasattr(verdict, "method")
        assert verdict.method == method_name
        assert 0.0 <= verdict.confidence <= 1.0

    @pytest.mark.parametrize("method_name", METHODOLOGY_LIST)
    def test_each_method_in_list(self, methodology_provider, method_name):
        """验证每个方法论都在注册列表中"""
        methods = methodology_provider.list_methods()
        assert method_name in methods, f"方法论 {method_name} 未在列表中找到"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
