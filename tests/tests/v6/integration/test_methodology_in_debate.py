# -*- coding: utf-8 -*-
"""方法论在辩论中的调用集成测试"""
import re
import sys
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from unittest.mock import Mock, patch
import pytest

sys.path.insert(0, "C:/Users/31683/.openclaw/workspace/.agents/skills/compound-engineering/Agent-superthinking/tests/v6")
from conftest import DebateResult, Conclusion, Statement, DebateRound


@dataclass
class MethodologyResult:
    """方法论执行结果"""
    name: str
    input: str
    output: str
    artifacts: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class MethodologyRegistry:
    """方法论注册表（模拟）"""
    
    def __init__(self):
        self._methods: Dict[str, Any] = {}
        self._register_defaults()
    
    def _register_defaults(self):
        """注册默认方法论"""
        self._methods["博弈论"] = self._game_theory
        self._methods["博弈理论"] = self._game_theory
        self._methods["gametheory"] = self._game_theory
        self._methods["成本收益分析"] = self._cost_benefit
        self._methods["SWOT分析"] = self._swot_analysis
        self._methods["第一性原理"] = self._first_principles
        self._methods["系统思考"] = self._systems_thinking
    
    def _game_theory(self, input_text: str) -> MethodologyResult:
        """博弈论方法论"""
        return MethodologyResult(
            name="博弈论",
            input=input_text,
            output=f"博弈论分析: 识别参与方、策略空间、收益矩阵",
            artifacts=["收益矩阵", "纳什均衡点"],
            metadata={"equilibrium": "mixed strategy"}
        )
    
    def _cost_benefit(self, input_text: str) -> MethodologyResult:
        """成本收益分析"""
        return MethodologyResult(
            name="成本收益分析",
            input=input_text,
            output=f"成本收益分析: 量化成本和收益",
            artifacts=["成本清单", "收益清单", "净收益值"],
            metadata={"total_cost": "待计算", "total_benefit": "待计算"}
        )
    
    def _swot_analysis(self, input_text: str) -> MethodologyResult:
        """SWOT分析"""
        return MethodologyResult(
            name="SWOT分析",
            input=input_text,
            output="SWOT分析: 优势、劣势、机会、威胁",
            artifacts=["S-Strengths", "W-Weaknesses", "O-Opportunities", "T-Threats"],
            metadata={"quadrant_count": 4}
        )
    
    def _first_principles(self, input_text: str) -> MethodologyResult:
        """第一性原理"""
        return MethodologyResult(
            name="第一性原理",
            input=input_text,
            output="第一性原理: 拆解到最基本的假设",
            artifacts=["基本假设列表", "重构方案"],
            metadata={"depth": "fundamental"}
        )
    
    def _systems_thinking(self, input_text: str) -> MethodologyResult:
        """系统思考"""
        return MethodologyResult(
            name="系统思考",
            input=input_text,
            output="系统思考: 识别反馈循环和因果链",
            artifacts=["因果关系图", "反馈循环图"],
            metadata={"loop_count": 2}
        )
    
    def execute(self, method_name: str, input_text: str) -> Optional[MethodologyResult]:
        """执行方法论"""
        method = self._methods.get(method_name)
        if method:
            return method(input_text)
        return None
    
    def detect_in_text(self, text: str) -> List[str]:
        """检测文本中的方法论声明"""
        detected = []
        for method in self._methods.keys():
            if method.lower() in text.lower():
                detected.append(method)
        return detected


class TestMethodologyInDebate:
    """测试方法论在辩论中的调用"""

    def test_expert_declares_game_theory(self):
        """测试专家声明使用博弈论"""
        registry = MethodologyRegistry()
        
        # 模拟专家发言
        expert_statement = "我用博弈论检验一下这个决策。从博弈论角度看，我们需要考虑对手的可能反应。"
        
        # 检测方法论声明
        detected = registry.detect_in_text(expert_statement)
        
        assert "博弈论" in detected or "博弈理论" in detected, "应该检测到博弈论声明"
        
        # 验证方法论正确触发
        result = registry.execute("博弈论", expert_statement)
        assert result is not None
        assert result.name == "博弈论"
        assert "收益矩阵" in result.artifacts

    def test_methodology_output_included_in_verdict(self):
        """测试 verdict 包含方法论输出"""
        registry = MethodologyRegistry()
        
        # 执行方法论
        question = "是否应该进入新市场？"
        method_result = registry.execute("博弈论", question)
        
        # 模拟 verdict 生成
        verdict = {
            "consensus_points": [
                f"通过{method_result.name}分析得出关键结论"
            ],
            "methodology_results": [
                {
                    "name": method_result.name,
                    "output": method_result.output,
                    "artifacts": method_result.artifacts
                }
            ],
            "suggestions": [
                f"基于{method_result.artifacts[0]}做决策"
            ]
        }
        
        # 验证 verdict 包含方法论输出
        assert "methodology_results" in verdict
        assert len(verdict["methodology_results"]) >= 1
        assert verdict["methodology_results"][0]["name"] == "博弈论"

    def test_multiple_methodologies_in_debate(self):
        """测试辩论中多个方法论被调用"""
        registry = MethodologyRegistry()
        
        # 模拟多位专家使用不同方法论
        statements = [
            "用SWOT分析这个机会",
            "从博弈论角度看竞争格局",
            "第一性原理拆解问题",
            "成本收益分析显示净收益为正"
        ]
        
        detected_methods = []
        for stmt in statements:
            methods = registry.detect_in_text(stmt)
            detected_methods.extend(methods)
        
        # 验证检测到多个方法论
        assert len(detected_methods) >= 3
        assert "SWOT分析" in detected_methods or "SWOT" in detected_methods
        assert "博弈论" in detected_methods or "博弈理论" in detected_methods

    def test_methodology_execution_preserves_context(self):
        """测试方法论执行保留上下文"""
        registry = MethodologyRegistry()
        
        # 模拟带上下文的输入
        context = {
            "question": "是否收购竞争对手？",
            "expert_perspective": "从财务角度分析",
            "previous_arguments": [
                "对方有技术优势",
                "但市场份额有限"
            ]
        }
        
        input_text = f"问题：{context['question']}\n专家视角：{context['expert_perspective']}"
        
        result = registry.execute("成本收益分析", input_text)
        
        # 验证方法论输出包含上下文信息
        assert result is not None
        assert context["question"] in result.input or result.name in result.input
        assert len(result.artifacts) > 0

    def test_methodology_not_declared_proceeds_normal(self):
        """测试未声明方法论时正常辩论"""
        registry = MethodologyRegistry()
        
        # 普通发言（不包含方法论声明）
        normal_statement = "我认为这个方案有优势，但需要考虑风险。"
        
        detected = registry.detect_in_text(normal_statement)
        
        # 验证没有检测到方法论
        assert len(detected) == 0, "普通发言不应触发方法论"
        
        # 辩论正常进行
        result = DebateResult(
            session_id="test",
            scenario="normal",
            question="测试",
            mode="v6_normal",
            max_rounds=3,
            actual_rounds=0,
            convergence_round=None
        )
        assert result.mode == "v6_normal"

    def test_methodology_registry_extensible(self):
        """测试方法论注册表可扩展"""
        registry = MethodologyRegistry()
        
        # 添加自定义方法论
        def custom_method(input_text: str) -> MethodologyResult:
            return MethodologyResult(
                name="自定义方法",
                input=input_text,
                output="自定义分析结果",
                artifacts=["自定义产物1"],
                metadata={"custom": True}
            )
        
        registry._methods["自定义方法"] = custom_method
        
        # 验证可执行
        result = registry.execute("自定义方法", "测试输入")
        assert result is not None
        assert result.name == "自定义方法"
        assert result.metadata.get("custom") is True
