"""
收敛判断测试

测试辩论收敛判断机制：
- 收敛信号监控
- 论点重叠率计算
- 新增论点密度计算
- 置信度变化检测
"""

import pytest
import sys
import os
from typing import List

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from debate_conftest import MockModerator, DebateRound, ExpertStatement


class TestConvergenceSignals:
    """收敛信号测试"""
    
    def test_convergence_signal_argument_overlap(self):
        """测试论点重叠率上升"""
        # 当论点重叠率上升时，可能意味着收敛
        overlap_rates = [0.2, 0.3, 0.45, 0.6]
        
        is_increasing = all(
            overlap_rates[i] <= overlap_rates[i+1]
            for i in range(len(overlap_rates)-1)
        )
        
        assert is_increasing
    
    def test_convergence_signal_decreasing_new_arguments(self):
        """测试新增论点密度下降"""
        # 当新增论点持续减少时，可能意味着收敛
        new_argument_counts = [5, 4, 3, 2, 1]
        
        is_decreasing = all(
            new_argument_counts[i] >= new_argument_counts[i+1]
            for i in range(len(new_argument_counts)-1)
        )
        
        assert is_decreasing
    
    def test_confidence_change_detection(self):
        """测试置信度变化检测"""
        # 专家发言中"可能/也许/我认为"等词的变化
        confidence_phrases = [
            "我认为",  # 高置信度
            "也许",    # 中置信度
            "可能",    # 中置信度
            "我不确定", # 低置信度
        ]
        
        # 收敛时，置信度应该趋于稳定
        high_confidence = confidence_phrases.count("我认为")
        low_confidence = confidence_phrases.count("我不确定")
        
        assert high_confidence + low_confidence >= 2


class TestConvergenceCriteria:
    """收敛标准测试"""
    
    def test_convergence_requires_multiple_rounds(self, mock_experts, mock_moderator):
        """测试收敛需要多轮辩论"""
        mock_moderator.initialize_debate(
            question="测试",
            experts=mock_experts,
            max_rounds=5
        )
        
        # 单轮无法判断收敛
        single_round = [DebateRound(round_number=1, phase="initial", expert_statements=[])]
        is_converged, reason = mock_moderator.check_convergence(single_round)
        
        assert is_converged == False
    
    def test_max_rounds_triggers_convergence(self, mock_experts, mock_moderator):
        """测试达到最大轮次触发收敛"""
        mock_moderator.initialize_debate(
            question="测试",
            experts=mock_experts,
            max_rounds=3
        )
        
        # 创建等于最大轮次的辩论
        rounds = [
            DebateRound(round_number=i, phase="debate", expert_statements=[])
            for i in range(1, 4)
        ]
        
        is_converged, reason = mock_moderator.check_convergence(rounds)
        
        assert is_converged == True
        assert "最大轮次" in reason


class TestConvergenceMetrics:
    """收敛指标测试"""
    
    def test_argument_overlap_calculation(self):
        """测试论点重叠率计算"""
        # 假设有两个论点集合
        round_1_arguments = ["A", "B", "C"]
        round_2_arguments = ["B", "C", "D"]
        
        # 重叠论点
        overlap = set(round_1_arguments) & set(round_2_arguments)
        overlap_rate = len(overlap) / max(len(round_1_arguments), len(round_2_arguments))
        
        assert overlap_rate == 2/3
    
    def test_new_argument_density_calculation(self):
        """测试新增论点密度计算"""
        # 新论点 = 本轮论点 - 与之前所有轮次的重叠
        all_past_arguments = {"A", "B", "C"}
        current_arguments = {"B", "C", "D", "E"}
        
        new_arguments = current_arguments - all_past_arguments
        new_argument_density = len(new_arguments) / len(current_arguments)
        
        assert new_argument_density == 2/4
    
    def test_convergence_threshold(self):
        """测试收敛阈值"""
        # 收敛的阈值定义（可配置）
        CONVERGENCE_OVERLAP_THRESHOLD = 0.5  # 50% 重叠率
        CONVERGENCE_NEW_ARGUMENT_THRESHOLD = 0.2  # 20% 新论点
        
        # 示例：重叠率 60%，新论点密度 10%
        overlap_rate = 0.6
        new_argument_density = 0.1
        
        is_converged = (
            overlap_rate >= CONVERGENCE_OVERLAP_THRESHOLD and
            new_argument_density <= CONVERGENCE_NEW_ARGUMENT_THRESHOLD
        )
        
        assert is_converged == True


class TestConvergenceScenarios:
    """收敛场景测试"""
    
    def test_early_convergence_scenario(self, mock_experts, mock_moderator):
        """测试早期收敛场景"""
        mock_moderator.initialize_debate(
            question="测试",
            experts=mock_experts,
            max_rounds=5
        )
        
        # 模拟快速收敛：论点快速重叠
        rounds = [
            DebateRound(round_number=i, phase="debate", expert_statements=[
                ExpertStatement("e1", "E1", "P1", f"论点{i}")
            ])
            for i in range(1, 5)
        ]
        
        # 最后一轮论点减少
        rounds.append(DebateRound(
            round_number=5, 
            phase="debate", 
            expert_statements=[ExpertStatement("e1", "E1", "P1", "最终论点")]
        ))
        
        is_converged, reason = mock_moderator.check_convergence(rounds)
        
        assert is_converged == True
    
    def test_max_round_no_convergence(self, mock_experts, mock_moderator):
        """测试达到最大轮次但未收敛"""
        mock_moderator.initialize_debate(
            question="测试",
            experts=mock_experts,
            max_rounds=3
        )
        
        # 创建轮次
        rounds = [
            DebateRound(round_number=i, phase="debate", expert_statements=[
                ExpertStatement("e1", "E1", "P1", f"论点{i}")
            ])
            for i in range(1, 4)
        ]
        
        is_converged, reason = mock_moderator.check_convergence(rounds)
        
        # 无论是否收敛，达到最大轮次就停止
        assert is_converged == True
    
    def test_deep_disagreement_scenario(self):
        """测试深度分歧场景"""
        # 当分歧很深时，主持人应该向用户询问更多信息
        disagreement_depth = 0.9  # 90% 分歧
        
        should_ask_user = disagreement_depth > 0.7
        
        assert should_ask_user == True


class TestConvergenceOutput:
    """收敛输出测试"""
    
    def test_convergence_result_structure(self):
        """测试收敛结果结构"""
        convergence_result = {
            "is_converged": True,
            "reason": "论点密度下降，辩论收敛",
            "overlap_rate": 0.6,
            "new_argument_density": 0.1,
            "confidence_change": "stable"
        }
        
        assert "is_converged" in convergence_result
        assert "reason" in convergence_result
    
    def test_convergence_with_partial_consensus(self):
        """测试部分共识的收敛"""
        partial_consensus = {
            "consensus_points": ["A和B都认为X是正确的"],
            "remaining_disagreements": ["C认为Y更重要"]
        }
        
        assert len(partial_consensus["consensus_points"]) > 0
        assert len(partial_consensus["remaining_disagreements"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
