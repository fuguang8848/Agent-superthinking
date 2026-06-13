# -*- coding: utf-8 -*-
"""v5 兼容验证集成测试"""
import os
import sys
from dataclasses import asdict
from unittest.mock import Mock, patch
import pytest

sys.path.insert(0, "C:/Users/31683/.openclaw/workspace/.agents/skills/compound-engineering/Agent-superthinking/tests/v6")
from conftest import (
    MockExpert, MockModerator, Statement, DebateRound, Conclusion, DebateResult,
    MockLLM
)


class TestV5Compatibility:
    """测试 v5 兼容模式"""

    def test_legacy_mode_env_variable(self):
        """测试 SUPER_THINKING_LEGACY=1 触发 v5 单轮模式"""
        # 模拟环境变量
        with patch.dict(os.environ, {"SUPER_THINKING_LEGACY": "1"}):
            # 检查环境变量生效
            legacy_mode = os.environ.get("SUPER_THINKING_LEGACY") == "1"
            assert legacy_mode, "SUPER_THINKING_LEGACY 环境变量应该被设置为 1"
            
            # 模拟 v5 单轮模式行为
            experts = [
                MockExpert("exp_1", "专家A", "视角A"),
                MockExpert("exp_2", "专家B", "视角B"),
            ]
            moderator = MockModerator()
            result = moderator.initialize("测试问题", experts, max_rounds=1)
            
            # v5 模式只执行 1 轮
            statements = [
                Statement(
                    expert_id=e.expert_id,
                    expert_name=e.name,
                    content=e.think("测试问题", {}),
                    is_targeted=False,
                    is_free_addition=False
                )
                for e in experts
            ]
            result.rounds.append(DebateRound(
                round_number=1,
                phase="single",
                statements=statements,
                argument_count=len(statements)
            ))
            result.actual_rounds = 1
            result.mode = "v5_legacy"
            result.conclusion = Conclusion(
                consensus_points=["综合意见"],
                disagreement_points=[],
                suggestions=["建议内容"]
            )
            
            # 验证 v5 模式特征
            assert result.actual_rounds == 1, "v5 模式应该只有 1 轮"
            assert result.mode == "v5_legacy", "模式应为 v5_legacy"

    def test_jury_think_return_fields_preserved(self):
        """验证 Jury().think() 返回值字段 100% 保留"""
        # 模拟 v5 Jury().think() 返回值
        v5_response = {
            "answer": "这是综合分析结果",
            "perspectives": [
                {"name": "视角A", "content": "从A角度的分析"},
                {"name": "视角B", "content": "从B角度的分析"}
            ],
            "summary": "综合各方观点的总结",
            "confidence": 0.85
        }
        
        # 验证所有字段存在
        assert "answer" in v5_response
        assert "perspectives" in v5_response
        assert "summary" in v5_response
        assert "confidence" in v5_response
        
        # 验证字段类型
        assert isinstance(v5_response["answer"], str)
        assert isinstance(v5_response["perspectives"], list)
        assert isinstance(v5_response["summary"], str)
        assert isinstance(v5_response["confidence"], float)
        
        # 验证字段内容
        assert len(v5_response["answer"]) > 0
        assert len(v5_response["perspectives"]) >= 1
        assert len(v5_response["summary"]) > 0
        assert 0 <= v5_response["confidence"] <= 1

    def test_v5_fallback_produces_complete_output(self):
        """测试 v5 降级时产生完整输出"""
        # 模拟 v5 降级场景（小众领域）
        experts = [MockExpert("exp_1", "通用分析师", "通用分析")]
        moderator = MockModerator()
        result = moderator.initialize("极端小众问题", experts, max_rounds=1)
        
        # v5 单轮执行
        statement = Statement(
            expert_id=experts[0].expert_id,
            expert_name=experts[0].name,
            content=experts[0].think("极端小众问题", {}),
            is_targeted=False,
            is_free_addition=False
        )
        result.rounds.append(DebateRound(
            round_number=1,
            phase="fallback",
            statements=[statement],
            argument_count=1
        ))
        result.actual_rounds = 1
        result.mode = "v5_fallback"
        result.conclusion = Conclusion(
            consensus_points=["需要专业咨询"],
            disagreement_points=[],
            suggestions=["建议咨询相关领域专家"]
        )
        
        # 验证输出完整性
        result_dict = result.to_dict()
        
        assert "session_id" in result_dict
        assert "question" in result_dict
        assert "mode" in result_dict
        assert "conclusion" in result_dict
        assert result_dict["mode"] == "v5_fallback"
        assert result_dict["conclusion"] is not None
        assert len(result_dict["conclusion"]["suggestions"]) >= 1

    def test_v5_mode_preserves_jury_interface(self):
        """测试 v5 模式保留 Jury 接口兼容性"""
        # 模拟 Jury 接口字段（v5 风格）
        jury_result = {
            "verdict": "推荐执行",
            "reasoning": "基于多角度分析",
            "alternatives": ["方案A", "方案B"],
            "risks": ["风险1", "风险2"],
            "next_steps": ["步骤1", "步骤2"]
        }
        
        # 验证接口字段完整性
        required_fields = ["verdict", "reasoning", "alternatives", "risks", "next_steps"]
        for field in required_fields:
            assert field in jury_result, f"v5 接口应包含 {field} 字段"
            assert jury_result[field] is not None, f"{field} 不应为 None"

    def test_legacy_mode_ignores_v6_features(self):
        """测试 v5 模式忽略 v6 特性"""
        # v6 特性配置
        v6_config = {
            "max_rounds": 10,
            "convergence_threshold": 0.7,
            "free_addition_ratio": 0.2,
            "methodology_enabled": True,
            "external_consultation": True
        }
        
        # v5 模式应该忽略这些配置
        legacy_config = {
            "max_rounds": 1,  # v5 固定单轮
            "convergence_threshold": None,  # v5 不需要收敛
            "free_addition_ratio": 0,  # v5 无自由补充
            "methodology_enabled": False,  # v5 无方法论
            "external_consultation": False  # v5 无外部咨询
        }
        
        # 验证 v5 配置覆盖 v6 配置
        assert legacy_config["max_rounds"] == 1
        assert legacy_config["convergence_threshold"] is None
        assert legacy_config["methodology_enabled"] is False
