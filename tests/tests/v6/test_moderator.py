"""
主持人（Moderator）测试模块

测试场景：
- MOD-001 ~ MOD-004: 初始化辩论会议
- AM-001 ~ AM-005: 论点菜单提取
- CONV-001 ~ CONV-005: 收敛判断
- UQ-001 ~ UQ-003: 用户询问
"""

import pytest
import sys
from pydantic import ValidationError
sys.path.insert(0, 'src')


class TestModeratorInitialization:
    """主持人初始化测试"""
    
    def test_normal_initialization(self, mock_moderator, sample_question):
        """MOD-001: 正常初始化"""
        result = mock_moderator.initialize(
            question=sample_question,
            expert_ids=["tech_architect", "product_manager"]
        )
        
        assert result["status"] == "initialized"
        assert result["meeting_id"] is not None
        assert len(result["experts"]) == 2
    
    def test_empty_question_validation(self, mock_moderator):
        """MOD-002: 空问题验证"""
        with pytest.raises((ValueError, ValidationError)):
            mock_moderator.initialize(question="", expert_ids=[])
    
    def test_special_characters_handling(self, mock_moderator):
        """MOD-004: 特殊字符处理"""
        special_question = "如何评价 <script>alert('xss')</script>？"
        result = mock_moderator.initialize(
            question=special_question,
            expert_ids=["test_expert"]
        )
        assert result["status"] == "initialized"


class TestArgumentMenuExtraction:
    """论点菜单提取测试"""
    
    def test_valid_argument_extraction(self, mock_moderator, sample_expert_speeches):
        """AM-001: 有效论点提取"""
        menu = mock_moderator.extract_argument_menu(sample_expert_speeches)
        assert "arguments" in menu
        assert isinstance(menu["arguments"], list)
    
    def test_filter_vague_statements(self, mock_moderator):
        """AM-002: 过滤泛泛而谈"""
        vague_speeches = [
            "我觉得这个问题挺好的",
            "需要认真考虑各个方面"
        ]
        menu = mock_moderator.extract_argument_menu(vague_speeches)
        # 泛泛而谈的发言应该被过滤
        assert len(menu["arguments"]) == 0
    
    def test_filter_non_refutable_content(self, mock_moderator):
        """AM-003: 过滤无可反驳内容"""
        non_refutable = [
            "这个问题需要更多思考",
            "未来可能会有更好的方案"
        ]
        menu = mock_moderator.extract_argument_menu(non_refutable)
        # 无明确判断的内容应被过滤
        assert len(menu["arguments"]) == 0


class TestConvergenceDetection:
    """收敛判断测试"""
    
    def test_convergence_signal(self, mock_moderator):
        """CONV-001: 收敛信号检测"""
        result = mock_moderator.check_convergence(
            round_num=3,
            arguments=[{"id": 1}, {"id": 2}]  # 论点减少
        )
        assert result in ["converging", "not_converging"]
    
    def test_max_rounds_reached(self, mock_moderator):
        """CONV-005: 达到最大轮次"""
        result = mock_moderator.check_convergence(
            round_num=5,
            arguments=[{"id": 1}, {"id": 2}, {"id": 3}]
        )
        assert result == "max_rounds_reached"


class TestUserQuestion:
    """用户询问测试"""
    
    def test_generate_valid_question(self, mock_moderator):
        """UQ-001: 生成有效问题"""
        # TODO: 实现主持人询问逻辑
        pass
    
    def test_prioritize_core_disagreements(self, mock_moderator):
        """UQ-002: 优先询问核心分歧"""
        # TODO: 实现核心分歧优先询问
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
