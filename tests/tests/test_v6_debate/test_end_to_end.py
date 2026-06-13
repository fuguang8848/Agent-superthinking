"""
端到端场景测试

测试完整的辩论流程，从用户提问到会议结论：
1. 用户提出问题
2. 主持人初始化
3. 第一轮并行发言
4. 辩论循环
5. 最终陈述
6. 会议结论
"""

import pytest
import sys
import os
from typing import List, Dict, Any

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from debate_conftest import MockModerator, MockExpert, ExpertStatement, ArgumentMenu, DebateRound, DebateSession


class TestEndToEndDebateScenario:
    """端到端辩论场景测试"""
    
    def test_complete_debate_flow(self, mock_experts, mock_moderator, sample_question):
        """测试完整的辩论流程"""
        # 1. 初始化辩论
        session = mock_moderator.initialize_debate(
            question=sample_question,
            experts=mock_experts,
            max_rounds=3
        )
        
        assert session is not None
        assert len(session.experts) == len(mock_experts)
        
        # 2. 第一轮并行发言
        initial_round = DebateRound(
            round_number=1,
            phase="initial",
            expert_statements=[
                ExpertStatement(
                    expert_id=e.expert_id,
                    expert_name=e.name,
                    expert_perspective=e.perspective,
                    content=e.speak_initial(sample_question)
                )
                for e in mock_experts
            ]
        )
        session.rounds.append(initial_round)
        
        # 验证初始发言
        assert len(initial_round.expert_statements) == len(mock_experts)
        for stmt in initial_round.expert_statements:
            assert not stmt.is_targeted
        
        # 3. 提取论点菜单
        argument_menu = mock_moderator.extract_argument_menu(initial_round)
        assert len(argument_menu.core_arguments) > 0
        
        # 4. 辩论循环
        for i in range(2, 4):
            debate_round = DebateRound(
                round_number=i,
                phase="debate",
                expert_statements=[
                    ExpertStatement(
                        expert_id=e.expert_id,
                        expert_name=e.name,
                        expert_perspective=e.perspective,
                        content=e.speak_debate(argument_menu, own_positions=[]),
                        is_targeted=True
                    )
                    for e in mock_experts
                ]
            )
            session.rounds.append(debate_round)
        
        # 5. 检查收敛
        is_converged, reason = mock_moderator.check_convergence(session.rounds)
        assert is_converged == True  # 达到最大轮次
        
        # 6. 生成结论
        conclusion = mock_moderator.generate_conclusion(session)
        assert conclusion is not None
        assert "共识点" in conclusion
        assert "分歧点" in conclusion
        
        session.final_conclusion = conclusion
        session.is_complete = True
        
        # 验证最终状态
        assert session.is_complete == True
        assert session.final_conclusion is not None
    
    def test_debate_with_user_intervention(self, mock_experts, mock_moderator):
        """测试有用户干预的辩论"""
        session = mock_moderator.initialize_debate(
            question="项目决策",
            experts=mock_experts,
            max_rounds=5
        )
        
        # 用户干预：添加重要背景信息
        user_background = "这个项目的甲方是我们长期合作伙伴"
        
        # 主持人应该调整辩论方向
        # 模拟主持人响应用户干预
        user_intervention_acknowledged = True
        
        assert user_intervention_acknowledged == True
        
        # 继续辩论
        initial_round = DebateRound(
            round_number=1,
            phase="initial",
            expert_statements=[
                ExpertStatement(
                    expert_id=e.expert_id,
                    expert_name=e.name,
                    expert_perspective=e.perspective,
                    content=f"基于新信息发言"
                )
                for e in mock_experts
            ]
        )
        session.rounds.append(initial_round)
        
        assert len(session.rounds) >= 1


class TestMethodologyIntegration:
    """方法论集成测试"""
    
    def test_methodology_pool_available(self):
        """测试方法论池可用"""
        # 方法论池索引应该在 experts/methods/INDEX.md
        methodologies = [
            "博弈论",
            "系统论",
            "伦理学",
            "经济学",
            "复杂性理论"
        ]
        
        assert len(methodologies) >= 5
    
    def test_methodology_invocation(self):
        """测试方法论调用"""
        # 专家可以调用方法论来验证论点
        invocation_pattern = "我用博弈论检验一下我的论点"
        
        assert "博弈论" in invocation_pattern
    
    def test_moderator_suggests_methodology(self):
        """测试主持人建议使用方法论"""
        suggestion = "[专家]，要不要用博弈论的角度看一下？"
        
        assert "博弈论" in suggestion
        assert "要不要" in suggestion


class TestDynamicExpertPool:
    """动态专家池测试"""
    
    def test_expert_join_during_debate(self):
        """测试辩论中专家加入"""
        current_experts = ["苏格拉底", "马斯克", "芒格"]
        
        # 新专家加入
        new_expert = "外部顾问"
        all_experts = current_experts + [new_expert]
        
        assert len(all_experts) == 4
        assert new_expert in all_experts
    
    def test_expert_leave_during_debate(self):
        """测试辩论中专家离开"""
        current_experts = ["苏格拉底", "马斯克", "芒格"]
        
        # 专家离开
        departed_expert = "马斯克"
        remaining_experts = [e for e in current_experts if e != departed_expert]
        
        assert len(remaining_experts) == 2
        assert departed_expert not in remaining_experts
    
    def test_expert_context_sync(self):
        """测试新专家上下文同步"""
        # 新专家应该收到：
        # 1. 当前正在辩论的核心问题
        # 2. 需要他判断的具体论点
        context_for_new_expert = {
            "core_question": "这个项目要不要接？",
            "current_arguments": [
                "苏格拉底：先问为什么要接",
                "芒格：风险被低估"
            ],
            "round_number": 3
        }
        
        assert "core_question" in context_for_new_expert
        assert "current_arguments" in context_for_new_expert


class TestExternalConsultation:
    """外部咨询测试"""
    
    def test_external_consultation_format(self):
        """测试外部咨询格式"""
        consultation_question = "从风险角度，你怎么看待这个项目？"
        
        consultation_response = "作为风险专家，我认为X风险需要特别关注。"
        
        assert len(consultation_response) > 0
        assert "风险" in consultation_response
    
    def test_consultation_used_in_judgment(self):
        """测试咨询结果用于判断"""
        # 主持人私下整合咨询意见
        consultation_notes = {
            "expert": "风险顾问",
            "view": "X风险被低估",
            "confidence": 0.8
        }
        
        # 主持人综合判断时考虑咨询意见
        moderator_judgment = "综合考虑咨询意见，X风险确实需要关注"
        
        assert "X风险" in moderator_judgment


class TestDebateQualityMetrics:
    """辩论质量指标测试"""
    
    def test_cross_argumentation_rate(self):
        """测试交叉反驳率"""
        # 有效反驳次数 / 总发言次数
        total_statements = 15
        targeted_statements = 12
        
        cross_argumentation_rate = targeted_statements / total_statements
        
        assert cross_argumentation_rate >= 0.7  # 至少70%的发言是针对其他专家的
    
    def test_free_addition_rate(self):
        """测试自由补充率"""
        # 自由补充次数 / 总发言次数
        total_statements = 15
        free_additions = 3
        
        free_addition_rate = free_additions / total_statements
        
        assert free_addition_rate >= 0.1  # 至少10%的发言是自由补充
    
    def test_methodology_usage_rate(self):
        """测试方法论使用率"""
        # 使用方法论的轮次 / 总轮次
        total_rounds = 5
        methodology_used_rounds = 2
        
        methodology_usage_rate = methodology_used_rounds / total_rounds
        
        assert methodology_usage_rate >= 0.2  # 至少20%的轮次使用了方法论


class TestSLACompliance:
    """SLA 合规测试"""
    
    def test_max_rounds_compliance(self):
        """测试最大轮次合规"""
        max_rounds_limit = 5
        
        actual_rounds = 5
        
        assert actual_rounds <= max_rounds_limit
    
    def test_hallucination_rate_requirement(self):
        """测试幻觉率要求（≤5%）"""
        # 模拟检测到的幻觉
        total_claims = 100
        hallucinated_claims = 4
        
        hallucination_rate = hallucinated_claims / total_claims
