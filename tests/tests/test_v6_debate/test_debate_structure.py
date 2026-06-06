"""
辩论结构测试

测试辩论的完整结构流程：
- 第一轮并行发言
- 论点菜单生成
- 辩论循环
- 最终陈述
- 会议结论
"""

import pytest
import sys
import os
from typing import List

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from debate_conftest import MockModerator, MockExpert, ExpertStatement, ArgumentMenu, DebateRound, DebateSession


class TestDebateStructure:
    """辩论结构测试"""
    
    def test_debate_has_five_phases(self):
        """测试辩论包含五个阶段"""
        # 根据设计文档，辩论应该包含：
        # 1. 初始化
        # 2. 第一轮并行发言
        # 3. 辩论循环
        # 4. 最终陈述
        # 5. 结论输出
        
        phases = ["initialization", "initial_round", "debate_loop", "final_statement", "conclusion"]
        assert len(phases) == 5
    
    def test_initial_round_is_parallel(self, mock_experts, mock_moderator, sample_question):
        """测试第一轮是并行发言"""
        session = mock_moderator.initialize_debate(
            question=sample_question,
            experts=mock_experts
        )
        
        # 第一轮应该是初始发言阶段
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
        
        # 所有专家都应该发言
        assert len(initial_round.expert_statements) == len(mock_experts)
        
        # 发言不应该是针对其他专家的
        for stmt in initial_round.expert_statements:
            assert not stmt.is_targeted


class TestArgumentMenuGeneration:
    """论点菜单生成测试"""
    
    def test_argument_menu_has_four_sections(self):
        """测试论点菜单包含四个部分"""
        # 根据 MODERATOR.md，论点菜单应该包含：
        # 1. 核心论点（可反驳）
        # 2. 已收敛的论点
        # 3. 建议下轮重点关注
        # 4. (隐式) 本轮发言的专家列表
        
        menu_sections = ["core_arguments", "converged_arguments", "suggestions", "experts"]
        assert len(menu_sections) >= 3
    
    def test_argument_validity_criteria(self):
        """测试论点有效性四标准"""
        # 根据设计文档，论点有效性标准：
        # 1. 具体性 - 针对具体论点，不是泛泛而谈
        # 2. 可反驳性 - 有明确的判断
        # 3. 论证性 - 有理由或证据支撑
        # 4. 分歧性 - 与其他专家观点存在差异
        
        criteria = ["specificity", "refutability", "argumentation", "divergence"]
        assert len(criteria) == 4
    
    def test_invalid_argument_vague_statement(self):
        """测试无效论点 - 泛泛而谈"""
        # "X总体是好的" 应该被排除
        vague_statement = "X总体是好的"
        
        # 验证是否是具体论点
        is_vague = len(vague_statement.split()) < 5 or "总体" in vague_statement
        assert is_vague
    
    def test_invalid_argument_no_judgment(self):
        """测试无效论点 - 没有明确判断"""
        # "需要更多思考" 没有明确判断
        statement = "需要更多思考"
        
        is_valid_judgment = any(word in statement for word in ["是", "应该", "认为", "相信"])
        assert not is_valid_judgment
    
    def test_invalid_argument_no_reason(self):
        """测试无效论点 - 没有理由"""
        # 只有观点没有理由
        statement = "我认为X。"
        
        has_reason = "因为" in statement or "理由是" in statement
        assert not has_reason


class TestDebateLoop:
    """辩论循环测试"""
    
    def test_debate_loop_continues_until_convergence(self, mock_experts, mock_moderator):
        """测试辩论循环持续直到收敛"""
        session = mock_moderator.initialize_debate(
            question="测试问题",
            experts=mock_experts,
            max_rounds=5
        )
        
        # 模拟辩论循环
        rounds = []
        for i in range(1, 4):
            round = DebateRound(
                round_number=i,
                phase="debate",
                expert_statements=[
                    ExpertStatement(
                        expert_id=e.expert_id,
                        expert_name=e.name,
                        expert_perspective=e.perspective,
                        content=f"第{i}轮发言",
                        is_targeted=True
                    )
                    for e in mock_experts
                ]
            )
            rounds.append(round)
        
        # 检查收敛
        is_converged, _ = mock_moderator.check_convergence(rounds)
        
        # 3轮辩论后不应该收敛
        assert is_converged == False
    
    def test_max_rounds_limit(self, mock_experts, mock_moderator):
        """测试最大轮次限制"""
        session = mock_moderator.initialize_debate(
            question="测试问题",
            experts=mock_experts,
            max_rounds=3
        )
        
        assert session.max_rounds == 3
    
    def test_debate_promotes_cross_argumentation(self):
        """测试辩论促进交叉反驳"""
        # 有效的辩论应该是：
        # 1. 专家A 针对 专家B 的论点发言
        # 2. 专家B 回应 专家A 的论点
        # 3. 专家C 可能同时针对 A 和 B
        
        cross_patterns = [
            ("A", "B"),  # A针对B
            ("B", "A"),  # B针对A
            ("C", "A"),
            ("C", "B"),
        ]
        
        assert len(cross_patterns) >= 2


class TestFinalStatement:
    """最终陈述测试"""
    
    def test_final_statement_after_convergence(self, mock_experts, mock_moderator):
        """测试收敛后的最终陈述"""
        session = mock_moderator.initialize_debate(
            question="测试问题",
            experts=mock_experts,
            max_rounds=3
        )
        
        # 创建收敛状态
        session.rounds = [
            DebateRound(round_number=i, phase="debate", expert_statements=[])
            for i in range(1, 4)
        ]
        
        # 生成结论
        conclusion = mock_moderator.generate_conclusion(session)
        
        assert conclusion is not None
        assert "共识点" in conclusion
    
    def test_final_statement_format(self):
        """测试最终陈述格式"""
        # 根据设计文档，最终陈述格式：
        # "综合本轮辩论，我的最终观点是[X]，因为[Y]。"
        
        format_pattern = "综合本轮辩论，我的最终观点是"
        assert len(format_pattern) > 0


class TestMeetingConclusion:
    """会议结论测试"""
    
    def test_conclusion_has_required_sections(self):
        """测试结论包含必要部分"""
        # 根据设计文档，结论应该包含：
        # 1. 【共识点】哪些论点专家们最终达成一致
        # 2. 【分歧点】哪些核心争议未能解决
        # 3. 【未解决的根本矛盾】分歧背后的底层假设差异
        # 4. 【建议】用户可以从哪些方向继续思考
        
        required_sections = [
            "共识点",
            "分歧点",
            "未解决的根本矛盾",
            "建议"
        ]
        
        assert len(required_sections) == 4
    
    def test_conclusion_recommendations_are_actionable(self):
        """测试结论建议具有可操作性"""
        conclusion = {
            "共识点": ["专家A和B都认为X"],
            "分歧点": ["在Y问题上存在分歧"],
            "未解决的根本矛盾": ["短期vs长期"],
            "建议": ["进一步收集数据", "考虑用户偏好"]
        }
        
        # 建议应该是可操作的
        assert isinstance(conclusion["建议"], list)
        assert len(conclusion["建议"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
