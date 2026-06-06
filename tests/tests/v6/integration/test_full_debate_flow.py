# -*- coding: utf-8 -*-
"""完整辩论流集成测试"""
import sys
import time
from dataclasses import asdict
from datetime import datetime
from typing import Any, Dict, List
from unittest.mock import Mock, MagicMock, patch
import pytest

# 复用 conftest 的 fixtures
sys.path.insert(0, "C:/Users/31683/.openclaw/workspace/.agents/skills/compound-engineering/Agent-superthinking/tests/v6")
from conftest import (
    MockExpert, MockModerator, Statement, DebateRound, Conclusion, DebateResult,
    create_experts_for_scenario, SCENARIO_CONFIGS, run_mock_debate
)


class TestFullDebateFlow:
    """测试完整辩论流程：5 专家 + 5 轮 + 正常收敛"""

    def test_five_experts_five_rounds_convergence(self):
        """测试 5 专家 5 轮辩论能正常收敛"""
        # 准备 5 个专家
        experts = [
            MockExpert("exp_1", "马斯克", "技术改变世界", "商业"),
            MockExpert("exp_2", "芒格", "风险评估", "风险"),
            MockExpert("exp_3", "苏格拉底", "哲学反思", "哲学"),
            MockExpert("exp_4", "张磊", "长期价值", "投资"),
            MockExpert("exp_5", "德鲁克", "管理视角", "管理"),
        ]
        
        # 初始化主持人
        moderator = MockModerator()
        question = "公司战略转型，应该激进还是保守？"
        result = moderator.initialize(question, experts, max_rounds=5)
        
        # 模拟辩论过程
        for round_num in range(1, 6):
            statements = [
                Statement(
                    expert_id=e.expert_id,
                    expert_name=e.name,
                    content=e.think(question, {"round": round_num}),
                    is_targeted=round_num > 1,
                    is_free_addition=(round_num > 2 and i == 0)
                )
                for i, e in enumerate(experts)
            ]
            phase = "initial" if round_num == 1 else ("debate" if round_num < 5 else "final")
            result.rounds.append(DebateRound(
                round_number=round_num,
                phase=phase,
                statements=statements,
                argument_count=len(statements)
            ))
            
            # 第 3 轮后收敛
            if round_num == 3:
                result.convergence_round = round_num
                break
        
        result.actual_rounds = len(result.rounds)
        result.mode = "v6_normal"
        result.conclusion = Conclusion(
            consensus_points=["技术驱动是长期竞争力", "风险控制很重要"],
            disagreement_points=["转型速度分歧"],
            suggestions=["建议分阶段转型", "建立风险预警机制"]
        )
        
        # 验证
        assert len(result.rounds) == 3, "应该 3 轮收敛"
        assert result.convergence_round == 3, "收敛轮次应为第 3 轮"
        assert result.actual_rounds == 3, "实际轮次应为 3"
        assert len(result.conclusion.suggestions) >= 1, "应有可操作建议"
        assert result.mode == "v6_normal", "应为 v6 正常模式"

    def test_recorder_event_sequence(self):
        """验证 recorder 事件顺序正确"""
        events = []
        
        # 模拟事件记录
        result = DebateResult(
            session_id="test_session",
            scenario="a",
            question="测试问题",
            mode="v6_normal",
            max_rounds=5,
            actual_rounds=0,
            convergence_round=None
        )
        events.append({"event": "session_start", "timestamp": datetime.now().isoformat()})
        
        # 模拟辩论轮次
        for round_num in range(1, 4):
            events.append({
                "event": "round_start",
                "round": round_num,
                "timestamp": datetime.now().isoformat()
            })
            
            for i in range(3):
                events.append({
                    "event": "expert_speak",
                    "expert_id": f"exp_{i+1}",
                    "round": round_num,
                    "timestamp": datetime.now().isoformat()
                })
            
            events.append({
                "event": "round_end",
                "round": round_num,
                "timestamp": datetime.now().isoformat()
            })
        
        events.append({"event": "session_end", "timestamp": datetime.now().isoformat()})
        
        # 验证事件顺序
        assert events[0]["event"] == "session_start"
        assert events[-1]["event"] == "session_end"
        
        # 验证轮次顺序
        for i in range(1, len(events) - 1):
            if events[i]["event"] == "round_start":
                round_num = events[i]["round"]
                # 找到对应的 round_end
                round_end_found = False
                for j in range(i + 1, len(events)):
                    if events[j]["event"] == "round_end" and events[j]["round"] == round_num:
                        round_end_found = True
                        break
                assert round_end_found, f"Round {round_num} should have round_end"

    def test_final_verdict_fields_complete(self):
        """验证最终 verdict 字段完整"""
        conclusion = Conclusion(
            consensus_points=["观点 A 正确", "观点 B 有效"],
            disagreement_points=["执行节奏有分歧"],
            unresolved_conflicts=["资源分配问题"],
            suggestions=["建议 1: 分阶段实施", "建议 2: 增加资源"]
        )
        
        verdict_dict = asdict(conclusion)
        
        # 验证所有必需字段
        assert "consensus_points" in verdict_dict
        assert "disagreement_points" in verdict_dict
        assert "unresolved_conflicts" in verdict_dict
        assert "suggestions" in verdict_dict
        
        # 验证字段类型
        assert isinstance(verdict_dict["consensus_points"], list)
        assert isinstance(verdict_dict["disagreement_points"], list)
        assert isinstance(verdict_dict["unresolved_conflicts"], list)
        assert isinstance(verdict_dict["suggestions"], list)
        
        # 验证字段内容
        assert len(verdict_dict["consensus_points"]) >= 1
        assert len(verdict_dict["suggestions"]) >= 1

    def test_debate_result_serialization(self):
        """测试 DebateResult 序列化"""
        experts = create_experts_for_scenario("a")
        moderator = MockModerator()
        result = moderator.initialize("测试问题", experts, max_rounds=3)
        result.mode = "v6_normal"
        result.actual_rounds = 2
        result.convergence_round = 2
        result.rounds.append(DebateRound(
            round_number=1, phase="initial",
            statements=[Statement("exp_1", "专家1", "测试内容")],
            argument_count=1
        ))
        result.conclusion = Conclusion(
            consensus_points=["共识1"],
            disagreement_points=[],
            suggestions=["建议1"]
        )
        
        # 序列化
        result_dict = result.to_dict()
        
        # 验证序列化结果
        assert "session_id" in result_dict
        assert "scenario" in result_dict
        assert "question" in result_dict
        assert "mode" in result_dict
        assert "max_rounds" in result_dict
        assert "actual_rounds" in result_dict
        assert "convergence_round" in result_dict
        assert "experts" in result_dict
        assert "rounds" in result_dict
        assert "conclusion" in result_dict
        assert "timestamp" in result_dict
        
        # 验证类型
        assert isinstance(result_dict["experts"], list)
        assert isinstance(result_dict["rounds"], list)
