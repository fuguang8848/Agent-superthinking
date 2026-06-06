# -*- coding: utf-8 -*-
"""V6 场景D: 争议问题 E2E 测试

测试争议问题（"技术vs人文"）的端到端流程。
验证点：识别分歧点、用户被合理咨询。
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from conftest import run_mock_debate, count_statements

class TestScenarioDControversy:
    """争议问题测试套件"""
    
    def test_disagreement_points_identified(self):
        """验证识别分歧点"""
        result = run_mock_debate("d", max_rounds=5)
        assert result.conclusion is not None, "应产生结论"
        assert len(result.conclusion.disagreement_points) >= 1, \
            "争议问题应识别分歧点"
    
    def test_opposing_expert_perspectives(self):
        """验证存在对立立场专家"""
        result = run_mock_debate("d", max_rounds=5)
        domains = [e.domain for e in result.experts]
        tech_count = sum(1 for d in domains if d == "技术")
        human_count = sum(1 for d in domains if d == "人文")
        assert tech_count >= 1 and human_count >= 1, \
            "争议问题应有技术和人文两类专家"
    
    def test_unresolved_conflicts_recorded(self):
        """验证未解决矛盾被记录"""
        result = run_mock_debate("d", max_rounds=5)
        assert result.conclusion is not None
        assert hasattr(result.conclusion, "unresolved_conflicts"), \
            "结论应包含未解决矛盾字段"
    
    def test_debate_rounds_for_controversy(self):
        """验证争议问题有足够辩论轮次"""
        result = run_mock_debate("d", max_rounds=5)
        assert result.actual_rounds >= 4, \
            f"争议问题应至少4轮辩论，实际: {result.actual_rounds}轮"
    
    def test_mode_v6_normal(self):
        """验证使用V6正常模式"""
        result = run_mock_debate("d", max_rounds=5)
        assert result.mode == "v6_normal", \
            f"争议场景应使用v6_normal模式，实际: {result.mode}"
    
    def test_conclusion_has_substantial_content(self):
        """验证结论有实质内容"""
        result = run_mock_debate("d", max_rounds=5)
        assert result.conclusion is not None
        total_items = (len(result.conclusion.consensus_points) + 
                      len(result.conclusion.disagreement_points) +
                      len(result.conclusion.suggestions))
        assert total_items >= 2, \
            f"争议问题结论应有>=2项内容，实际: {total_items}项"
    
    def test_targeted_statements_exist(self):
        """验证存在针对他人的发言（辩论特征）"""
        result = run_mock_debate("d", max_rounds=5)
        targeted_count = sum(1 for r in result.rounds for s in r.statements if s.is_targeted)
        assert targeted_count > 0, "争议问题应有针对他人的辩论发言"
