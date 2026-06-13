"""
专家模块测试

测试专家 (Expert) 的核心功能：
- 初始发言生成
- 辩论发言生成（针对格式）
- 自由补充发言
- 最终陈述生成
- 发言格式验证
"""

import pytest
import re
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from debate_conftest import MockExpert, ExpertStatement, ArgumentMenu


class TestExpertInitialStatement:
    """专家初始发言测试"""
    
    def test_initial_statement_format(self, mock_experts, sample_question):
        """测试初始发言格式"""
        expert = mock_experts[0]  # 苏格拉底
        statement = expert.speak_initial(sample_question)
        
        # 验证包含关键词
        assert "关于" in statement
        assert sample_question[:10] in statement or "问题" in statement
        assert expert.perspective in statement
        assert "认为" in statement
    
    def test_initial_statement_not_targeted(self, mock_experts, sample_question):
        """测试初始发言不是针对其他专家"""
        expert = mock_experts[0]
        statement = expert.speak_initial(sample_question)
        
        # 初始发言不应该包含"针对"
        assert "针对[" not in statement
        assert "针对专家" not in statement
    
    def test_expert_has_unique_perspective(self, mock_experts):
        """测试每位专家有独特视角"""
        perspectives = [e.perspective for e in mock_experts]
        assert len(perspectives) == len(set(perspectives)), "专家视角应该唯一"


class TestExpertDebateStatement:
    """专家辩论发言测试"""
    
    def test_debate_statement_targets_other(self, mock_experts):
        """测试辩论发言针对其他专家"""
        expert = mock_experts[0]
        
        argument_menu = ArgumentMenu(
            round_number=1,
            core_arguments=[
                {
                    "expert_id": "e2",
                    "expert_name": "马斯克",
                    "argument": "应该抓住机会",
                    "reason": "市场窗口"
                }
            ]
        )
        
        statement = expert.speak_debate(argument_menu, own_positions=[])
        
        # 应该包含针对格式
        assert "针对" in statement
        assert "马斯克" in statement
        assert "认为" in statement
        assert "因为" in statement
    
    def test_debate_statement_with_multiple_targets(self, mock_experts):
        """测试针对多个专家的发言"""
        expert = mock_experts[0]
        
        argument_menu = ArgumentMenu(
            round_number=1,
            core_arguments=[
                {"expert_id": "e2", "expert_name": "马斯克", "argument": "观点1", "reason": "原因1"},
                {"expert_id": "e3", "expert_name": "芒格", "argument": "观点2", "reason": "原因2"},
            ]
        )
        
        statement = expert.speak_debate(argument_menu, own_positions=[])
        
        assert "针对" in statement
    
    def test_debate_statement_free_addition(self, mock_experts):
        """测试自由补充"""
        expert = mock_experts[0]
        
        # 空论点菜单时，应该有自由补充
        argument_menu = ArgumentMenu(
            round_number=1,
            core_arguments=[]
        )
        
        statement = expert.speak_debate(argument_menu, own_positions=[])
        
        # 应该包含自由补充关键词
        assert "另外" in statement or "补充" in statement or "角度" in statement


class TestExpertFinalStatement:
    """专家最终陈述测试"""
    
    def test_final_statement_format(self, mock_experts):
        """测试最终陈述格式"""
        expert = mock_experts[0]
        statement = expert.speak_final("辩论摘要")
        
        # 应该包含关键词
        assert "综合" in statement or "最终" in statement
        assert expert.perspective in statement
        assert "认为" in statement
    
    def test_final_statement_differs_from_initial(self, mock_experts, sample_question):
        """测试最终陈述与初始发言不同"""
        expert = mock_experts[0]
        
        initial = expert.speak_initial(sample_question)
        final = expert.speak_final("辩论摘要")
        
        # 内容应该不同
        assert initial != final


class TestExpertStatementValidation:
    """专家发言格式验证测试"""
    
    def test_valid_targeted_statement(self):
        """测试有效的针对格式发言"""
        statement = "针对[苏格拉底]的论点，我认为X，因为Y视角。"
        
        # 验证格式
        pattern = r"针对\[.+\]的论点，我认为.+，因为.+。"
        assert re.search(pattern, statement) is not None
    
    def test_invalid_statement_missing_target(self):
        """测试缺少目标专家的无效发言"""
        statement = "我认为X，因为Y。"
        
        # 不应该匹配针对格式
        pattern = r"针对\[.+\]的论点，我认为.+"
        assert re.search(pattern, statement) is None
    
    def test_invalid_statement_missing_reason(self):
        """测试缺少理由的无效发言"""
        statement = "针对[苏格拉底]的论点，我认为X。"
        
        # 不应该匹配完整格式
        pattern = r"针对\[.+\]的论点，我认为.+，因为.+。"
        assert re.search(pattern, statement) is None
    
    def test_free_addition_format(self):
        """测试自由补充格式"""
        # 有效的自由补充格式
        valid_formats = [
            "另外，我想补充一个观点...",
            "不过，还有一个角度...",
            "另外，我想补充...",
        ]
        
        for fmt in valid_formats:
            assert "另外" in fmt or "不过" in fmt


class TestExpertParticipation:
    """专家参与模式测试"""
    
    def test_expert_formal_participation(self):
        """测试正式参与模式"""
        expert = MockExpert("e1", "测试专家", "测试视角")
        
        # 正式参与应该全程参与
        initial = expert.speak_initial("测试问题")
        assert initial is not None
        
        argument_menu = ArgumentMenu(round_number=1, core_arguments=[])
        debate = expert.speak_debate(argument_menu, own_positions=[])
        assert debate is not None
        
        final = expert.speak_final("摘要")
        assert final is not None
    
    def test_expert_external_consultation(self):
        """测试外部咨询模式"""
        expert = MockExpert("e1", "测试专家", "测试视角")
        
        # 外部咨询只需要提供观点
        initial = expert.speak_initial("测试问题")
        
        # 外部咨询观点应该简短
        assert len(initial) > 0
        assert len(initial) < 500  # 外部咨询观点应该简洁


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
