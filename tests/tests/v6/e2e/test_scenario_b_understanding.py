# -*- coding: utf-8 -*-
"""V6 场景B: 理解类问题 E2E 测试

测试理解类问题（"如何理解'熵增'？"）的端到端流程。
验证点：跨学科视角融合、共识点明确。
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from conftest import run_mock_debate, count_statements, get_domains

class TestScenarioBUnderstanding:
    """理解类问题测试套件"""
    
    def test_cross_domain_perspectives(self):
        """验证跨学科视角（至少3个不同领域）"""
        result = run_mock_debate("b", max_rounds=5)
        domains = get_domains(result)
        assert len(domains) >= 3, \
            f"理解类问题应有>=3个不同领域专家，实际: {len(domains)}个"
    
    def test_consensus_points_defined(self):
        """验证共识点明确"""
        result = run_mock_debate("b", max_rounds=5)
        assert result.conclusion is not None, "应产生结论"
        assert len(result.conclusion.consensus_points) >= 1, \
            "理解类问题应有明确的共识点"
    
    def test_multi_perspective_conclusion(self):
        """验证多学科融合的结论"""
        result = run_mock_debate("b", max_rounds=5)
        assert result.conclusion is not None
        conclusion_text = " ".join(result.conclusion.consensus_points) + " ".join(result.conclusion.suggestions)
        assert len(conclusion_text) >= 10, "结论应有实质内容"
    
    def test_expert_diversity(self):
        """验证专家多样性"""
        result = run_mock_debate("b", max_rounds=5)
        perspectives = [e.perspective for e in result.experts]
        assert len(set(perspectives)) >= 3, \
            f"专家应有不同视角，实际: {len(set(perspectives))}种"
    
    def test_rounds_completed(self):
        """验证理解类场景完成足够轮次"""
        result = run_mock_debate("b", max_rounds=5)
        assert result.actual_rounds >= 4, \
            f"理解类问题应至少4轮，实际: {result.actual_rounds}轮"
    
    def test_mode_v6_normal(self):
        """验证使用V6正常模式"""
        result = run_mock_debate("b", max_rounds=5)
        assert result.mode == "v6_normal", \
            f"理解类场景应使用v6_normal模式，实际: {result.mode}"
