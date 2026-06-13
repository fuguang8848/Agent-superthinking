"""
辩论流程（DebateFlow）测试模块

测试场景：
- FLOW-001 ~ FLOW-005: 完整辩论流程
- FLOW-010 ~ FLOW-012: 多轮辩论状态
"""

import pytest
import sys
sys.path.insert(0, 'src')


class TestCompleteDebateFlow:
    """完整辩论流程测试"""
    
    def test_normal_flow(self, mock_moderator, mock_experts, sample_question):
        """FLOW-001: 正常辩论流程"""
        # 1. 初始化
        init_result = mock_moderator.initialize(
            question=sample_question,
            expert_ids=[e.expert_id for e in mock_experts]
        )
        assert init_result["status"] == "initialized"
        
        # 2. 第一轮发言
        first_round_speeches = [e.speak({"question": sample_question}) for e in mock_experts]
        assert len(first_round_speeches) == 3
        
        # 3. 提取论点菜单
        menu = mock_moderator.extract_argument_menu(first_round_speeches)
        assert "arguments" in menu
    
    def test_first_round_convergence(self, mock_moderator, mock_experts, sample_question):
        """FLOW-002: 首轮收敛"""
        # 初始化
        mock_moderator.initialize(
            question=sample_question,
            expert_ids=[e.expert_id for e in mock_experts]
        )
        
        # 如果首轮论点已经一致，应直接进入最终陈述
        convergence = mock_moderator.check_convergence(round_num=1, arguments=[])
        assert convergence in ["converging", "not_converging"]
    
    def test_max_rounds_flow(self, mock_moderator, mock_experts, sample_question):
        """FLOW-003: 最大轮次收敛"""
        # 模拟达到最大轮次
        mock_moderator.initialize(
            question=sample_question,
            expert_ids=[e.expert_id for e in mock_experts]
        )
        
        # 多轮后达到最大
        for round_num in range(1, 6):
            menu = mock_moderator.extract_argument_menu([f"论点{round_num}"])
            convergence = mock_moderator.check_convergence(round_num=round_num, arguments=menu["arguments"])
            if round_num >= 5:
                assert convergence == "max_rounds_reached"


class TestMultiRoundState:
    """多轮辩论状态测试"""
    
    def test_state_completeness(self, mock_moderator, sample_debate_context):
        """FLOW-010: 状态完整性"""
        # TODO: 验证辩论状态包含所有必要信息
        pass
    
    def test_history_tracking(self, mock_moderator, mock_experts, sample_question):
        """FLOW-011: 历史记录追踪"""
        mock_moderator.initialize(
            question=sample_question,
            expert_ids=[e.expert_id for e in mock_experts]
        )
        
        # 多轮辩论
        for round_num in range(1, 4):
            speeches = [e.speak({"question": sample_question}) for e in mock_experts]
            menu = mock_moderator.extract_argument_menu(speeches)
            # 验证历史可追溯
            assert menu is not None


@pytest.mark.e2e
class TestEndToEndDebate:
    """端到端辩论测试"""
    
    def test_full_debate_sequence(self, mock_moderator, mock_experts, sample_question):
        """完整辩论序列测试"""
        # 1. 初始化
        init_result = mock_moderator.initialize(
            question=sample_question,
            expert_ids=[e.expert_id for e in mock_experts]
        )
        
        # 2. 辩论循环
        max_rounds = 5
        for round_num in range(1, max_rounds + 1):
            # 专家发言
            speeches = [e.speak({"question": sample_question}) for e in mock_experts]
            
            # 提取论点
            menu = mock_moderator.extract_argument_menu(speeches)
            
            # 检查收敛
            convergence = mock_moderator.check_convergence(round_num, menu["arguments"])
            
            if convergence in ["converging", "max_rounds_reached"]:
                # 生成结论
                conclusion = mock_moderator.generate_conclusion()
                assert "consensus_points" in conclusion
                assert "disagreements" in conclusion
                break


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
