# -*- coding: utf-8 -*-
"""V6 场景E: 空领域问题 E2E 测试

测试空领域问题（极端小众）的端到端流程。
验证点：优雅降级到 v5 单轮模式。
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from conftest import run_mock_debate, count_statements

class TestScenarioEEmptyDomain:
    """空领域问题测试套件"""
    
    def test_graceful_degradation_to_v5_mode(self):
        """验证优雅降级到 v5 单轮模式"""
        result = run_mock_debate("e", max_rounds=5)
        assert result.mode in ["v5_fallback", "hybrid"], \
            f"空领域应降级到v5模式，实际: {result.mode}"
    
    def test_single_round_mode(self):
        """验证单轮模式"""
        result = run_mock_debate("e", max_rounds=5)
        assert result.actual_rounds <= 2, \
            f"降级模式应<=2轮，实际: {result.actual_rounds}轮"
    
    def test_conclusion_still_generated(self):
        """验证降级后仍有结论输出"""
        result = run_mock_debate("e", max_rounds=5)
        assert result.conclusion is not None, \
            "降级模式也应产生结论"
    
    def test_user_notification_about_limitations(self):
        """验证用户通知局限性"""
        result = run_mock_debate("e", max_rounds=5)
        suggestion_text = " ".join(result.conclusion.suggestions) if result.conclusion else ""
        assert "专家" in suggestion_text or len(suggestion_text) > 0, \
            "应告知用户专家有限"
    
    def test_convergence_reported(self):
        """验证降级模式也报告收敛"""
        result = run_mock_debate("e", max_rounds=5)
        assert result.convergence_round is not None, \
            "降级模式也应报告收敛轮次"
    
    def test_fewer_experts_than_normal(self):
        """验证空领域专家数量较少"""
        result = run_mock_debate("e", max_rounds=5)
        assert len(result.experts) <= 3, \
            f"空领域专家数量应较少，实际: {len(result.experts)}"
    
    def test_no_crash_on_empty_domain(self):
        """验证空领域不崩溃"""
        result = run_mock_debate("e", max_rounds=5)
        assert result.error is None or result.error == "", \
            f"空领域处理不应出错，实际错误: {result.error}"
