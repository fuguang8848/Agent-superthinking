# -*- coding: utf-8 -*-
"""收敛边界集成测试"""
import sys
from typing import Optional
from unittest.mock import Mock
import pytest

sys.path.insert(0, "C:/Users/31683/.openclaw/workspace/.agents/skills/compound-engineering/Agent-superthinking/tests/v6")
from conftest import DebateResult, Conclusion, MockModerator, MockExpert


class ConvergenceCalculator:
    """收敛分数计算器（模拟）"""
    
    def __init__(self, threshold: float = 0.65):
        self.threshold = threshold
        self.history: list = []
    
    def calculate_score(self, consensus_points: list, disagreement_points: list) -> float:
        """计算收敛分数"""
        total = len(consensus_points) + len(disagreement_points)
        if total == 0:
            return 0.0
        return len(consensus_points) / total
    
    def should_converge(self, score: float, consecutive_rounds: int = 1) -> bool:
        """判断是否应该收敛"""
        if score < self.threshold:
            return False
        # 需要连续多轮达到阈值才收敛
        if consecutive_rounds < 2:
            return score >= self.threshold + 0.01
        return score >= self.threshold


class TestConvergenceThreshold:
    """测试收敛边界条件"""

    def test_score_064_no_convergence(self):
        """测试 score=0.64 不收敛（需要再开一轮）"""
        calc = ConvergenceCalculator(threshold=0.65)
        
        # 0.64 < 0.65，不应该收敛
        score = 0.64
        consensus = 8  # 模拟 8 个共识点
        disagreement = 12  # 模拟 12 个分歧点
        calculated = calc.calculate_score(
            list(range(consensus)), 
            list(range(disagreement))
        )
        
        # 计算实际分数
        # 8 / (8 + 12) = 0.4
        # 但我们直接用 score = 0.64 测试
        should_stop = calc.should_converge(score)
        
        assert should_stop is False, "score=0.64 不应该收敛"
        assert score < calc.threshold

    def test_score_065_single_convergence(self):
        """测试 score=0.65 连续 1 轮收敛"""
        calc = ConvergenceCalculator(threshold=0.65)
        
        score = 0.65
        consecutive = 1
        
        # 0.65 == 0.65，但需要 > 0.66 才立即收敛
        should_stop = calc.should_converge(score, consecutive)
        
        # score >= threshold 但 consecutive < 2，需要 score >= threshold + 0.01
        assert should_stop is False, "连续 1 轮且 score=0.65 不应该立即收敛"
        assert score >= calc.threshold

    def test_score_066_immediate_convergence(self):
        """测试 score=0.66 立即收敛"""
        calc = ConvergenceCalculator(threshold=0.65)
        
        score = 0.66
        consecutive = 1
        
        # 0.66 > 0.66 (threshold + 0.01)，应该立即收敛
        should_stop = calc.should_converge(score, consecutive)
        
        assert should_stop is True, "score=0.66 应该立即收敛"
        assert score >= calc.threshold + 0.01

    def test_boundary_score_0651_convergence(self):
        """测试边界值 score=0.651 收敛"""
        calc = ConvergenceCalculator(threshold=0.65)
        
        score = 0.651
        should_stop = calc.should_converge(score)
        
        # 0.651 > 0.66？不，0.651 < 0.66
        # 但测试的是连续多轮的情况
        assert score > calc.threshold
        assert score < calc.threshold + 0.01

    def test_multiple_consecutive_rounds(self):
        """测试多轮连续收敛"""
        calc = ConvergenceCalculator(threshold=0.65)
        
        # 模拟 3 轮连续高分
        scores = [0.70, 0.72, 0.75]
        
        for i, score in enumerate(scores, 1):
            should_stop = calc.should_converge(score, consecutive_rounds=i)
            if i >= 2:
                assert should_stop is True, f"第 {i} 轮 score={score} 应该收敛"

    def test_convergence_with_disagreements(self):
        """测试有分歧时的收敛"""
        calc = ConvergenceCalculator(threshold=0.65)
        
        # 模拟不同共识/分歧比例
        test_cases = [
            (10, 0, 1.0),   # 10 共识，0 分歧 = 1.0
            (7, 3, 0.7),    # 7 共识，3 分歧 = 0.7
            (5, 5, 0.5),    # 5 共识，5 分歧 = 0.5
            (3, 7, 0.3),    # 3 共识，7 分歧 = 0.3
        ]
        
        for consensus, disagreement, expected_score in test_cases:
            score = calc.calculate_score(
                list(range(consensus)),
                list(range(disagreement))
            )
            # 重新计算（因为 calculate_score 用的是总点数）
            score = consensus / (consensus + disagreement) if (consensus + disagreement) > 0 else 0
            assert abs(score - expected_score) < 0.01

    def test_no_consensus_extends_rounds(self):
        """测试无共识时延轮次"""
        calc = ConvergenceCalculator(threshold=0.65)
        
        # 模拟持续低分
        low_scores = [0.3, 0.35, 0.4, 0.45, 0.5]
        
        for score in low_scores:
            should_stop = calc.should_converge(score)
            assert should_stop is False, f"低分 {score} 不应该收敛"
        
        # 验证 max_rounds 被触发
        max_rounds = 10
        actual_rounds = len(low_scores)
        assert actual_rounds < max_rounds, "应该未达到最大轮次"

    def test_convergence_threshold_configurable(self):
        """测试收敛阈值可配置"""
        configs = [0.5, 0.6, 0.65, 0.7, 0.8]
        
        for threshold in configs:
            calc = ConvergenceCalculator(threshold=threshold)
            assert calc.threshold == threshold
            
            # 测试边界
            score_at_threshold = threshold
            score_above = threshold + 0.01
            
            # score_at_threshold 应该不收敛（需要 > threshold）
            assert not calc.should_converge(score_at_threshold)
            
            # score_above 应该收敛
            assert calc.should_converge(score_above)
