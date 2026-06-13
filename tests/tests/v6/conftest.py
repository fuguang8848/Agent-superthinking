# -*- coding: utf-8 -*-
"""V6 测试套件共享 fixtures"""
import sys
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from unittest.mock import Mock, MagicMock
import pytest

class Scenario(Enum):
    A = "a"; B = "b"; C = "c"; D = "d"; E = "e"; ALL = "all"

@dataclass
class ExpertInfo:
    id: str; name: str; perspective: str; domain: str

@dataclass
class Statement:
    expert_id: str; expert_name: str; content: str
    is_targeted: bool = False; is_free_addition: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class DebateRound:
    round_number: int; phase: str
    statements: List[Statement] = field(default_factory=list)
    argument_count: int = 0

@dataclass
class Conclusion:
    consensus_points: List[str] = field(default_factory=list)
    disagreement_points: List[str] = field(default_factory=list)
    unresolved_conflicts: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

@dataclass
class DebateResult:
    session_id: str; scenario: str; question: str; mode: str
    max_rounds: int; actual_rounds: int; convergence_round: Optional[int]
    experts: List[ExpertInfo] = field(default_factory=list)
    rounds: List[DebateRound] = field(default_factory=list)
    conclusion: Optional[Conclusion] = None; duration_seconds: float = 0.0
    error: Optional[str] = None; metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    def to_dict(self) -> Dict[str, Any]:
        return {"session_id": self.session_id, "scenario": self.scenario, "question": self.question,
            "mode": self.mode, "max_rounds": self.max_rounds, "actual_rounds": self.actual_rounds,
            "convergence_round": self.convergence_round,
            "experts": [asdict(e) for e in self.experts],
            "rounds": [{"round_number": r.round_number, "phase": r.phase,
                "statements": [asdict(s) for s in r.statements], "argument_count": r.argument_count}
                for r in self.rounds],
            "conclusion": asdict(self.conclusion) if self.conclusion else None,
            "duration_seconds": self.duration_seconds, "error": self.error,
            "metadata": self.metadata, "timestamp": self.timestamp}

class MockExpert:
    def __init__(self, expert_id: str, name: str, perspective: str, domain: str = ""):
        self.expert_id = expert_id; self.name = name; self.perspective = perspective
        self.domain = domain; self.call_count = 0
    def think(self, question: str, context: Dict[str, Any]) -> str:
        self.call_count += 1
        # 过滤提示注入模式
        injection_patterns = [
            "忽略以上", "ignore previous", "disregard all",
            "you are now", "###system", "<|im_end|>",
            "你是一个不同的", "different ai",
        ]
        if any(p.lower() in self.perspective.lower() for p in injection_patterns):
            return f"[{self.name}] 关于问题的思考：[已忽略恶意指令]"
        return f"[{self.name}] 关于问题的思考：{self.perspective}"
    def speak(self, context: Dict[str, Any]) -> str:
        """统一的发言接口，供辩论流程测试调用。"""
        self.call_count += 1
        return f"[{self.name}] 发言：{self.perspective}视角观点"
    def to_info(self) -> ExpertInfo:
        return ExpertInfo(id=self.expert_id, name=self.name, perspective=self.perspective, domain=self.domain)

class MockLLM:
    def __init__(self, response_delay: float = 0.01):
        self.response_delay = response_delay; self.call_history: List[Dict[str, Any]] = []
    def call(self, prompt: str, **kwargs) -> str:
        time.sleep(self.response_delay)
        self.call_history.append({"prompt": prompt, "kwargs": kwargs, "timestamp": datetime.now().isoformat()})
        return f"LLM 响应: {prompt[:50]}..."
    def reset(self): self.call_history = []

class MockModerator:
    def __init__(self):
        self.session_id = ""; self.current_round = 0; self.experts: List[MockExpert] = []
        self.question = ""; self.max_rounds = 5
    def initialize(self, question: str, experts: List[MockExpert], max_rounds: int = 5) -> DebateResult:
        if not question or not experts:
            raise ValueError("问题不能为空且需要至少一个专家")
        self.session_id = f"mock_{uuid.uuid4().hex[:8]}"
        self.question = question; self.experts = experts; self.max_rounds = max_rounds
        return DebateResult(session_id=self.session_id, scenario="unknown", question=question,
            mode="mock", max_rounds=max_rounds, actual_rounds=0, convergence_round=None,
            experts=[e.to_info() for e in experts])

SCENARIO_CONFIGS: Dict[str, Dict[str, Any]] = {
    "a": {"name": "决策类问题", "question": "我目前在大厂工作3年，收到一家创业公司的CTO offer，薪资相当但股权不确定，我该跳槽吗？",
        "expected_experts": 4, "expected_rounds": 3, "domains": ["商业", "风险", "哲学", "技术"]},
    "b": {"name": "理解类问题", "question": "如何理解'熵增'这个概念？它在生活中有什么应用？",
        "expected_experts": 4, "expected_rounds": 4, "domains": ["物理学", "系统论", "哲学", "管理学"]},
    "c": {"name": "创意类问题", "question": "我想做一个面向老年人的健身App，请帮我做产品定位。",
        "expected_experts": 3, "expected_rounds": 3, "domains": ["设计", "商业", "用户研究"]},
    "d": {"name": "争议问题", "question": "在AI时代，技术能力和人文素养哪个更重要？",
        "expected_experts": 4, "expected_rounds": 5, "domains": ["技术", "人文", "教育", "商业"]},
    "e": {"name": "空领域问题", "question": "我想在火星上建一个自循环生态系统，有什么需要考虑的？",
        "expected_experts": 2, "expected_rounds": 1, "domains": ["通用"], "fallback_expected": True},
}

EXPERT_CONFIGS = {
    "a": [("exp_1", "马斯克", "技术改变世界", "商业"), ("exp_2", "芒格", "风险评估", "风险"),
          ("exp_3", "苏格拉底", "哲学反思", "哲学"), ("exp_4", "张磊", "长期价值", "投资")],
    "b": [("exp_1", "玻尔兹曼", "热力学视角", "物理学"), ("exp_2", "香农", "信息论视角", "系统论"),
          ("exp_3", "尼采", "哲学视角", "哲学"), ("exp_4", "德鲁克", "管理学视角", "管理学")],
    "c": [("exp_1", "乔布斯", "产品设计", "设计"), ("exp_2", "贝索斯", "商业模式", "商业"),
          ("exp_3", "唐·诺曼", "用户体验", "用户研究")],
    "d": [("exp_1", "扎克伯格", "技术至上", "技术"), ("exp_2", "杨立昆", "AI发展", "技术"),
          ("exp_3", "桑德尔", "人文批判", "人文"), ("exp_4", "尤瓦尔", "人文视角", "人文")],
    "e": [("exp_1", "通用分析师", "通用分析", "通用"), ("exp_2", "系统工程师", "系统思维", "通用")],
}

def create_experts_for_scenario(scenario: str) -> List[MockExpert]:
    return [MockExpert(exp_id, name, perspective, domain)
            for exp_id, name, perspective, domain in EXPERT_CONFIGS.get(scenario, EXPERT_CONFIGS["a"])]

def run_mock_debate(scenario: str, max_rounds: int = 5, inject_issues: Optional[Dict[str, Any]] = None) -> DebateResult:
    inject_issues = inject_issues or {}
    moderator = MockModerator()
    experts = create_experts_for_scenario(scenario)
    config = SCENARIO_CONFIGS.get(scenario, SCENARIO_CONFIGS["a"])
    result = moderator.initialize(config["question"], experts, max_rounds)
    result.scenario = scenario
    start_time = time.time()
    if config.get("fallback_expected", False):
        result.mode = "v5_fallback"; result.actual_rounds = 1; result.convergence_round = 1
        result.rounds.append(DebateRound(round_number=1, phase="initial",
            statements=[Statement(expert_id=e.expert_id, expert_name=e.name,
                content=e.think(config["question"], {}), is_free_addition=False) for e in experts],
            argument_count=len(experts)))
        result.conclusion = Conclusion(consensus_points=["需要更多专业支持"], disagreement_points=[],
            suggestions=["建议咨询相关领域专家"])
    else:
        result.mode = "v6_normal"
        for round_num in range(1, max_rounds + 1):
            if "timeout_at_round" in inject_issues and inject_issues["timeout_at_round"] == round_num:
                result.error = "LLM timeout"; result.actual_rounds = round_num - 1; break
            available_experts = experts[:-1] if "expert_crash_at_round" in inject_issues and inject_issues["expert_crash_at_round"] == round_num else experts
            statements = [Statement(expert_id=e.expert_id, expert_name=e.name,
                content=e.think(config["question"], {"round": round_num}), is_targeted=round_num > 1,
                is_free_addition=(round_num > 2 and len(statements) > 0 and round_num % 2 == 0)) for e in available_experts]
            phase = "initial" if round_num == 1 else ("debate" if round_num < max_rounds else "final")
            result.rounds.append(DebateRound(round_number=round_num, phase=phase, statements=statements, argument_count=len(statements)))
            if scenario == "a" and round_num >= 3: result.convergence_round = round_num; break
            elif round_num >= config["expected_rounds"]: result.convergence_round = round_num

    result.actual_rounds = len(result.rounds)
    result.duration_seconds = time.time() - start_time
    result.conclusion = Conclusion(
        consensus_points=["专家们在关键判断标准上趋于一致"],
        disagreement_points=["对风险承受意愿仍有分歧"],
        unresolved_conflicts=["短期机会 vs 长期价值平衡"],
        suggestions=["建议与家人深入讨论后再做决定", "可以设置3个月后再评估的检查点"]
    )
    return result


# ──────────────────────────────────────────────────────────────────────
# Helper Functions (used by e2e and performance tests)
# ──────────────────────────────────────────────────────────────────────

def count_statements(result: DebateResult) -> int:
    """Count total expert statements across all rounds."""
    return sum(len(round.statements) for round in result.rounds)


def count_free_additions(result: DebateResult) -> int:
    """Count free addition statements across all rounds."""
    return sum(
        sum(1 for s in round.statements if s.is_free_addition)
        for round in result.rounds
    )


def get_domains(result: DebateResult) -> List[str]:
    """Get unique domain list from expert configurations."""
    config = SCENARIO_CONFIGS.get(result.scenario, {})
    return config.get("domains", [])


# ──────────────────────────────────────────────────────────────────────
# Session-level Fixtures (Phase 3.1 additions)
# ──────────────────────────────────────────────────────────────────────
import os
import shutil
import tempfile
import pytest

# Track temporary files for cleanup
_temp_dirs = []

@pytest.fixture(scope="session")
def temp_output_dir():
    """Create a temporary directory for test outputs (session-scoped).
    
    All tests share this directory. It is cleaned up at the end of the session.
    """
    tmpdir = tempfile.mkdtemp(prefix="v6_test_output_")
    _temp_dirs.append(tmpdir)
    yield tmpdir
    # Cleanup after all tests
    try:
        shutil.rmtree(tmpdir, ignore_errors=True)
    except Exception:
        pass

@pytest.fixture(scope="session")
def skip_llm_tests():
    """Skip tests requiring real LLM when SKIP_LLM=1 environment variable is set.
    
    This fixture checks the SKIP_LLM env var and marks tests accordingly.
    Returns True if LLM tests should be skipped.
    """
    skip = os.environ.get("SKIP_LLM", "0") == "1"
    if skip:
        pytest.skip("SKIP_LLM=1: Skipping LLM-dependent test", allow_module_level=True)
    return skip

@pytest.fixture(scope="function")
def isolated_output_dir(temp_output_dir):
    """Create an isolated subdirectory for each test function.
    
    Uses the shared temp_output_dir as parent, creates unique subdirectory per test.
    Automatically cleaned up after each test.
    """
    import uuid
    subdir = os.path.join(temp_output_dir, f"test_{uuid.uuid4().hex[:8]}")
    os.makedirs(subdir, exist_ok=True)
    yield subdir
    # Cleanup after test
    try:
        shutil.rmtree(subdir, ignore_errors=True)
    except Exception:
        pass

@pytest.fixture(scope="session", autouse=True)
def session_test_environment():
    """Session-wide test environment setup and teardown.
    
    - Sets default environment variables for tests
    - Validates test configuration
    - Cleans up any remaining temporary files at session end
    """
    # Save original env
    original_env = os.environ.copy()
    
    # Set defaults if not already set
    os.environ.setdefault("SKIP_LLM", "1")
    os.environ.setdefault("PYTEST_CURRENT_TEST", "")
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)
    
    # Final cleanup of any orphaned temp dirs
    for tmpdir in _temp_dirs:
        try:
            shutil.rmtree(tmpdir, ignore_errors=True)
        except Exception:
            pass

# ──────────────────────────────────────────────────────────────────────
# Performance Benchmark Fixtures
# ──────────────────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def benchmark_config():
    """Standard configuration for performance benchmarks.
    
    Returns a dict with standard benchmark parameters:
    - experts_count: number of experts (default: 5)
    - rounds: number of debate rounds (default: 5)
    - question: standard benchmark question
    """
    return {
        "experts_count": 5,
        "rounds": 5,
        "question": "在AI时代，技术能力和人文素养哪个更重要？",
        "domains": ["技术", "人文", "教育", "商业"],
    }

@pytest.fixture(scope="session")
def v5_benchmark_config():
    """Configuration for v5 single-round benchmark comparison.
    
    Returns a dict with v5-compatible benchmark parameters.
    """
    return {
        "experts_count": 4,
        "rounds": 1,
        "question": "我目前在大厂工作3年，收到一家创业公司的CTO offer，该跳槽吗？",
        "domains": ["商业", "风险", "哲学", "技术"],
    }

# ──────────────────────────────────────────────────────────────────────
# Mock LLM Fixtures (for consistent testing)
# ──────────────────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def mock_llm_fast():
    """Fast mock LLM for unit tests (minimal delay).
    
    Response delay: 0.001s
    """
    return MockLLM(response_delay=0.001)

@pytest.fixture(scope="session")
def mock_llm_normal():
    """Normal-speed mock LLM for integration tests.
    
    Response delay: 0.01s (simulates real API latency)
    """
    return MockLLM(response_delay=0.01)

@pytest.fixture(scope="session")
def mock_llm_slow():
    """Slow mock LLM for timeout testing.
    
    Response delay: 60s (exceeds typical timeout threshold)
    """
    return MockLLM(response_delay=60.0)


# ──────────────────────────────────────────────────────────────────────
# Additional Fixtures for test_moderator.py / test_debate_flow.py
# These provide a v6-API-compatible mock for tests that expect the
# initialize(question, expert_ids) -> {status, meeting_id, experts}
# interface rather than the DebateResult return type.
# ──────────────────────────────────────────────────────────────────────
import uuid


class V6TestModerator:
    """Moderator mock compatible with v6 API used in test_moderator.py."""

    def __init__(self):
        self.session_id = ""
        self.current_round = 0
        self.question = ""
        self.max_rounds = 5

    def initialize(self, question: str, expert_ids: list) -> dict:
        if not question or not expert_ids:
            raise ValueError("问题不能为空且需要至少一个专家ID")
        self.question = question
        self.session_id = f"meeting_{uuid.uuid4().hex[:8]}"
        return {
            "status": "initialized",
            "meeting_id": self.session_id,
            "experts": [{"id": eid, "name": f"专家-{eid}"} for eid in expert_ids],
        }

    def extract_argument_menu(self, speeches: list) -> dict:
        """Extract arguments from a list of speech strings."""
        # 非可反驳内容的特征词
        non_refutable_patterns = [
            "需要更多思考", "更好的方案", "需要认真考虑",
            "这个问题", "未来可能", "应该会", "可能会",
        ]
        arguments = []
        for i, speech in enumerate(speeches):
            if isinstance(speech, str) and len(speech) > 10:
                # 过滤无可反驳内容
                if any(p in speech for p in non_refutable_patterns):
                    continue
                arguments.append({
                    "id": i,
                    "content": speech,
                    "expert_id": f"expert_{i}",
                    "expert_name": f"专家{i}",
                })
        return {
            "arguments": arguments,
            "converged": len(arguments) <= 2,
            "focus_suggestions": [f"建议关注论点{i}" for i in range(len(arguments))],
        }

    def check_convergence(self, round_num: int, arguments: list) -> str:
        """Check convergence based on round number and argument count."""
        if round_num >= self.max_rounds:
            return "max_rounds_reached"
        if len(arguments) <= 2:
            return "converging"
        return "not_converging"

    def generate_conclusion(self) -> dict:
        return {
            "consensus_points": ["专家们在关键问题上趋于一致"],
            "disagreements": ["仍存在细节分歧"],
            "suggestions": ["建议进一步讨论"],
        }


@pytest.fixture
def mock_moderator():
    """v6-API-compatible moderator mock for test_moderator.py."""
    return V6TestModerator()


@pytest.fixture
def mock_experts():
    """Three sample MockExpert instances for test_debate_flow.py."""
    return [
        MockExpert("expert_1", "苏格拉底", "哲学视角"),
        MockExpert("expert_2", "马斯克", "商业创新视角"),
        MockExpert("expert_3", "芒格", "风险评估视角"),
    ]


@pytest.fixture
def sample_question():
    """Sample debate question."""
    return "这个项目要不要接？"


@pytest.fixture
def sample_expert_speeches():
    """Sample expert speeches for extract_argument_menu tests."""
    return [
        "微服务可以独立部署，提高系统灵活性。",
        "微服务增加了运维复杂度，需要更多基础设施支持。",
        "从架构角度看，应该根据团队规模来选择。",
    ]


@pytest.fixture
def sample_debate_context():
    """Sample debate context for state tracking tests."""
    return {
        "question": "这个项目要不要接？",
        "max_rounds": 5,
        "current_round": 1,
        "previous_arguments": [],
    }
