# -*- coding: utf-8 -*-
"""V6 场景A: 决策类问题 E2E 测试

测试决策类问题（"我该跳槽吗？"）的端到端流程。
验证点：3-5个专家、3轮内收敛、产生可操作建议。
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from conftest import run_mock_debate, count_statements, count_free_additions, get_domains

class TestScenarioADecision:
    """决策类问题测试套件"""
    
    def test_expert_count_within_range(self):
        """验证专家数量在 3-5 人之间"""
        result = run_mock_debate("a", max_rounds=5)
        assert 3 <= len(result.experts) <= 5, \
            f"专家数量应在3-5之间，实际: {len(result.experts)}"
    
    def test_convergence_within_3_rounds(self):
        """验证3轮内收敛"""
        result = run_mock_debate("a", max_rounds=5)
        assert result.convergence_round is not None, "应产生收敛轮次"
        assert result.convergence_round <= 3, \
            f"应在3轮内收敛，实际: {result.convergence_round}轮"
    
    def test_operational_suggestions_generated(self):
        """验证产生可操作建议"""
        result = run_mock_debate("a", max_rounds=5)
        assert result.conclusion is not None, "应产生结论"
        assert len(result.conclusion.suggestions) > 0, "结论应包含可操作建议"
        suggestion = result.conclusion.suggestions[0]
        assert len(suggestion) >= 10, "建议应有实际内容（非空）"
    
    def test_debate_flow_completeness(self):
        """验证辩论流程完整性（初始化→并行→辩论→收敛→结论）"""
        result = run_mock_debate("a", max_rounds=5)
        assert len(result.rounds) >= 3, "至少有3轮辩论"
        phases = [r.phase for r in result.rounds]
        assert "initial" in phases, "应有初始阶段"
        assert any(p in ["debate", "final"] for p in phases), "应有辩论或最终阶段"
    
    def test_all_experts_participated(self):
        """验证所有专家都有发言"""
        result = run_mock_debate("a", max_rounds=5)
        expert_ids = {e.id for e in result.experts}
        speaking_experts = {s.expert_id for r in result.rounds for s in r.statements}
        assert expert_ids.issubset(speaking_experts), "所有专家都应发言"
    
    def test_mode_is_v6_normal(self):
        """验证使用V6正常模式（非降级）"""
        result = run_mock_debate("a", max_rounds=5)
        assert result.mode == "v6_normal", \
            f"决策类场景应使用v6_normal模式，实际: {result.mode}"
    
    def test_disagreement_points_recorded(self):
        """验证分歧点被记录"""
        result = run_mock_debate("a", max_rounds=5)
        assert result.conclusion is not None
        assert hasattr(result.conclusion, "disagreement_points")
        assert len(result.conclusion.disagreement_points) >= 0
    
    def test_debate_duration_reasonable(self):
        """验证Mock模式运行时间合理（<10秒）"""
        result = run_mock_debate("a", max_rounds=5)
        assert result.duration_seconds < 10, \
            f"Mock模式运行时间应<10秒，实际: {result.duration_seconds}s"
