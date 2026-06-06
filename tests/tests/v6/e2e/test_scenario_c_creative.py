# -*- coding: utf-8 -*-
"""V6 场景C: 创意类问题 E2E 测试

测试创意类问题（"产品定位"）的端到端流程。
验证点：自由补充占比>=20%、最终陈述差异化。
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from conftest import run_mock_debate, count_statements, count_free_additions

class TestScenarioCCreative:
    """创意类问题测试套件"""
    
    def test_free_addition_ratio_above_20_percent(self):
        """验证自由补充占比 >= 20%"""
        result = run_mock_debate("c", max_rounds=5)
        total = count_statements(result)
        free_count = count_free_additions(result)
        assert total > 0, "应有总发言数"
        ratio = free_count / total
        assert ratio >= 0.2, \
            f"自由补充占比应>=20%，实际: {ratio:.1%}"
    
    def test_final_statements_differentiated(self):
        """验证最终陈述差异化（至少2个不同观点）"""
        result = run_mock_debate("c", max_rounds=5)
        assert len(result.rounds) > 0, "应有辩论轮次"
        final_round = result.rounds[-1]
        contents = [s.content for s in final_round.statements]
        unique_contents = len(set(contents))
        assert unique_contents >= 2, \
            f"最终陈述应有差异化，至少2个不同观点，实际: {unique_contents}个"
    
    def test_expert_creative_perspectives(self):
        """验证创意类专家来自不同领域"""
        result = run_mock_debate("c", max_rounds=5)
        domains = set(e.domain for e in result.experts)
        assert len(domains) >= 2, \
            f"创意类问题应有>=2个不同领域，实际: {len(domains)}个"
    
    def test_creative_suggestions_generated(self):
        """验证产生创意建议"""
        result = run_mock_debate("c", max_rounds=5)
        assert result.conclusion is not None, "应产生结论"
        assert len(result.conclusion.suggestions) >= 1, \
            "创意类问题应产生建议"
    
    def test_mode_v6_normal(self):
        """验证使用V6正常模式"""
        result = run_mock_debate("c", max_rounds=5)
        assert result.mode == "v6_normal", \
            f"创意类场景应使用v6_normal模式，实际: {result.mode}"
    
    def test_rounds_conducted(self):
        """验证至少进行3轮辩论"""
        result = run_mock_debate("c", max_rounds=5)
        assert result.actual_rounds >= 3, \
            f"创意类问题应至少3轮，实际: {result.actual_rounds}轮"
