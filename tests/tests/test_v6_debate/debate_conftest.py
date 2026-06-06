"""
Debate test fixtures for tests/test_v6_debate/ test suite.
Renamed from conftest.py to avoid import shadowing with tests/v6/conftest.py.
"""
import pytest
import sys
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ExpertStatement:
    """专家发言数据结构"""
    expert_id: str
    expert_name: str
    expert_perspective: str
    content: str
    is_targeted: bool = False
    targets: List[str] = field(default_factory=list)
    is_free_addition: bool = False


@dataclass
class ArgumentMenu:
    """论点菜单数据结构"""
    round_number: int
    core_arguments: List[Dict[str, str]]
    converged_arguments: List[Dict[str, str]] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


@dataclass
class DebateRound:
    """辩论轮次数据结构"""
    round_number: int
    phase: str
    expert_statements: List[ExpertStatement] = field(default_factory=list)
    argument_menu: Optional[ArgumentMenu] = None
    is_converged: bool = False
    convergence_reason: str = ""


@dataclass
class DebateSession:
    """辩论会话数据结构"""
    session_id: str
    question: str
    question_background: str = ""
    max_rounds: int = 5
    experts: List[Dict[str, str]] = field(default_factory=list)
    rounds: List[DebateRound] = field(default_factory=list)
    final_conclusion: Optional[Dict[str, Any]] = None
    is_complete: bool = False


class MockExpert:
    def __init__(self, expert_id: str, name: str, perspective: str, domain: str = ""):
        self.expert_id = expert_id
        self.name = name
        self.perspective = perspective
        self.domain = domain
        self.statements: List[str] = []

    def speak_initial(self, question: str) -> str:
        return f"关于[{question}]，从[{self.perspective}]来看，我认为这个问题需要深入分析。"

    def speak_debate(self, argument_menu: ArgumentMenu, own_positions: List[str]) -> str:
        if argument_menu.core_arguments:
            target = argument_menu.core_arguments[0]
            return f"针对[{target['expert_name']}]的论点，我认为{target['argument']}，因为{self.perspective}视角。"
        return f"另外，我想补充一个观点：从{self.perspective}来看，这个问题还有另一个维度。"

    def speak_final(self, debate_summary: str) -> str:
        return f"综合本轮辩论，我认为：{self.perspective}视角仍然是最重要的考量。"


class MockModerator:
    def __init__(self):
        self.session: Optional[DebateSession] = None
        self.current_round: int = 0

    def initialize_debate(self, question: str, experts: List[MockExpert],
                         max_rounds: int = 5) -> DebateSession:
        self.session = DebateSession(
            session_id=f"session_{hash(question) % 10000}",
            question=question,
            max_rounds=max_rounds,
            experts=[
                {"id": e.expert_id, "name": e.name, "perspective": e.perspective}
                for e in experts
            ]
        )
        return self.session

    def extract_argument_menu(self, round: DebateRound) -> ArgumentMenu:
        core_args = []
        for stmt in round.expert_statements:
            if stmt.content:
                core_args.append({
                    "expert_id": stmt.expert_id,
                    "expert_name": stmt.expert_name,
                    "argument": f"核心论点（{stmt.expert_perspective}）",
                    "reason": "见发言内容"
                })
        return ArgumentMenu(
            round_number=round.round_number,
            core_arguments=core_args,
            suggestions=[f"第{len(core_args)}个论点需要进一步辩论"]
        )

    def check_convergence(self, rounds: List[DebateRound]) -> tuple[bool, str]:
        if len(rounds) < 2:
            return False, "轮次不足"
        # Check max_rounds first (higher priority)
        if len(rounds) >= self.session.max_rounds:
            return True, "达到最大轮次"
        # 收敛条件：论点密度持续下降 2 轮以上
        if len(rounds) >= 3:
            last_args = len(rounds[-1].expert_statements)
            prev_args = len(rounds[-2].expert_statements)
            prev2_args = len(rounds[-3].expert_statements)
            if last_args <= prev_args <= prev2_args and last_args < prev2_args:
                return True, "论点密度连续下降，辩论收敛"
        return False, "辩论尚未收敛"

    def generate_conclusion(self, session: DebateSession) -> Dict[str, Any]:
        return {
            "共识点": ["专家们在方法论选择上达成一致"],
            "分歧点": ["在风险评估上存在分歧"],
            "未解决的根本矛盾": ["短期收益 vs 长期价值"],
            "建议": ["建议进一步收集数据后再做决策"]
        }


@pytest.fixture
def mock_experts():
    return [
        MockExpert("expert_1", "苏格拉底", "哲学"),
        MockExpert("expert_2", "马斯克", "商业创新"),
        MockExpert("expert_3", "芒格", "风险评估"),
    ]


@pytest.fixture
def mock_moderator():
    return MockModerator()


@pytest.fixture
def sample_question():
    return "这个项目要不要接？"


@pytest.fixture
def sample_debate_session(mock_experts, mock_moderator, sample_question):
    return mock_moderator.initialize_debate(
        question=sample_question,
        experts=mock_experts,
        max_rounds=5
    )
