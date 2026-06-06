"""
主持人模块测试

测试主持人 (Moderator) 的核心功能：
- 初始化辩论会话
- 选择专家组合
- 整理论点菜单
- 收敛判断
- 调整专家阵容
- 生成会议结论
"""

import pytest
import sys
import os
from typing import List

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from debate_conftest import MockModerator, MockExpert, ExpertStatement, ArgumentMenu, DebateRound, DebateSession


class TestModeratorInitialization:
    """主持人初始化测试"""
    
    def test_initialize_debate_creates_session(self, mock_moderator, sample_question, mock_experts):
        """测试初始化辩论创建会话"""
        session = mock_moderator.initialize_debate(
            question=sample_question,
            experts=mock_experts
        )
        
        assert session is not None
        assert isinstance(session, DebateSession)
        assert session.question == sample_question
        assert len(session.experts) == len(mock_experts)
    
    def test_initialize_debate_with_max_rounds(self, mock_moderator, sample_question, mock_experts):
        """测试自定义最大轮次"""
        custom_max_rounds = 10
        session = mock_moderator.initialize_debate(
            question=sample_question,
            experts=mock_experts,
            max_rounds=custom_max_rounds
        )
        
        assert session.max_rounds == custom_max_rounds
    
    def test_session_id_is_unique(self, mock_moderator, sample_question, mock_experts):
        """测试会话ID唯一性"""
        session1 = mock_moderator.initialize_debate(
            question="问题1",
            experts=mock_experts
        )
        session2 = mock_moderator.initialize_debate(
            question="问题2",
            experts=mock_experts
        )
        
        assert session1.session_id != session2.session_id


class TestExpertSelection:
    """专家选择测试"""
    
    def test_expert_list_populated(self, sample_debate_session, mock_experts):
        """测试专家列表正确填充"""
        assert len(sample_debate_session.experts) == len(mock_experts)
        
        for i, expert_dict in enumerate(sample_debate_session.experts):
            assert "id" in expert_dict
            assert "name" in expert_dict
            assert "perspective" in expert_dict
            assert expert_dict["id"] == mock_experts[i].expert_id
    
    def test_minimum_experts_required(self, mock_moderator, sample_question):
        """测试至少需要3位专家"""
        experts = [
            MockExpert("e1", "专家1", "视角1"),
            MockExpert("e2", "专家2", "视角2"),
            MockExpert("e3", "专家3", "视角3"),
        ]
        
        session = mock_moderator.initialize_debate(
            question=sample_question,
            experts=experts
        )
        
        assert len(session.experts) >= 3


class TestArgumentMenuExtraction:
    """论点菜单提取测试"""
    
    def test_extract_from_round(self, mock_moderator, mock_experts):
        """测试从一轮发言中提取论点菜单"""
        round = DebateRound(
            round_number=1,
            phase="initial",
            expert_statements=[
                ExpertStatement(
                    expert_id="e1",
                    expert_name="苏格拉底",
                    expert_perspective="哲学",
                    content="我认为应该先问为什么"
                ),
                ExpertStatement(
                    expert_id="e2",
                    expert_name="马斯克",
                    expert_perspective="商业",
                    content="不接会错过市场窗口"
                ),
            ]
        )
        
        menu = mock_moderator.extract_argument_menu(round)
        
        assert menu.round_number == 1
        assert len(menu.core_arguments) == 2
        assert menu.core_arguments[0]["expert_name"] == "苏格拉底"
        assert menu.core_arguments[1]["expert_name"] == "马斯克"
    
    def test_empty_round_returns_empty_menu(self, mock_moderator):
        """测试空轮次返回空菜单"""
        round = DebateRound(
            round_number=1,
            phase="initial",
            expert_statements=[]
        )
        
        menu = mock_moderator.extract_argument_menu(round)
        
        assert menu.round_number == 1
        assert len(menu.core_arguments) == 0


class TestConvergenceDetection:
    """收敛检测测试"""
    
    def test_not_converged_early_rounds(self, mock_moderator, mock_experts):
        """测试早期轮次未收敛"""
        mock_moderator.initialize_debate(
            question="测试问题",
            experts=mock_experts,
            max_rounds=5
        )
        
        rounds = [
            DebateRound(round_number=1, phase="initial", expert_statements=[
                ExpertStatement("e1", "E1", "P1", "内容1"),
            ]),
        ]
        
        is_converged, reason = mock_moderator.check_convergence(rounds)
        
        assert is_converged == False
    
    def test_converged_after_max_rounds(self, mock_moderator, mock_experts):
        """测试达到最大轮次后收敛"""
        mock_moderator.initialize_debate(
            question="测试问题",
            experts=mock_experts,
            max_rounds=3
        )
        
        rounds = [
            DebateRound(round_number=i, phase="debate", expert_statements=[
                ExpertStatement("e1", "E1", "P1", f"内容{i}")
            ])
            for i in range(1, 4)
        ]
        
        is_converged, reason = mock_moderator.check_convergence(rounds)
        
        assert is_converged == True
        assert "最大轮次" in reason
    
    def test_convergence_with_decreasing_arguments(self, mock_moderator, mock_experts):
        """测试论点密度下降时的收敛"""
        mock_moderator.initialize_debate(
            question="测试问题",
            experts=mock_experts,
            max_rounds=5
        )
        
        rounds = [
            DebateRound(round_number=i, phase="debate", expert_statements=[
                ExpertStatement("e1", "E1", "P1", f"内容{i}")
            ])
            for i in range(1, 5)
        ]
        # 最后一轮论点少于前一轮
        rounds.append(DebateRound(
            round_number=5, 
            phase="debate", 
            expert_statements=[ExpertStatement("e1", "E1", "P1", "内容5")]
        ))
        
        is_converged, reason = mock_moderator.check_convergence(rounds)
        
        assert is_converged == True


class TestConclusionGeneration:
    """结论生成测试"""
    
    def test_generate_conclusion_structure(self, sample_debate_session):
        """测试结论结构"""
        from debate_conftest import MockModerator
        
        moderator = MockModerator()
        moderator.session = sample_debate_session
        
        conclusion = moderator.generate_conclusion(sample_debate_session)
        
        assert "共识点" in conclusion
        assert "分歧点" in conclusion
        assert "未解决的根本矛盾" in conclusion
        assert "建议" in conclusion
    
    def test_conclusion_has_recommendations(self, sample_debate_session):
        """测试结论包含建议"""
        from debate_conftest import MockModerator
        
        moderator = MockModerator()
        moderator.session = sample_debate_session
        
        conclusion = moderator.generate_conclusion(sample_debate_session)
        
        assert isinstance(conclusion["建议"], list)
        assert len(conclusion["建议"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
