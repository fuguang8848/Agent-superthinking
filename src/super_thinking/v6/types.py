"""
v6 基础类型定义

包含 ID 类型、枚举、基础 dataclass 定义。
遵循 v6_INTERFACES.md 契约。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, NewType, Protocol, runtime_checkable, Tuple, Callable
from datetime import datetime

# =============================================================================
# ID 类型
# =============================================================================

SessionId = NewType("SessionId", str)
RoundNumber = NewType("RoundNumber", int)  # 1-based
ArgumentId = NewType("ArgumentId", str)  # "A-R1-002"
ExpertId = NewType("ExpertId", str)
MethodId = NewType("MethodId", str)
QuestionId = NewType("QuestionId", str)


# =============================================================================
# 枚举
# =============================================================================

class SessionStatus(str, Enum):
    INIT = "init"
    RUNNING = "running"
    CONVERGED = "converged"
    MAX_ROUNDS = "max_rounds"
    USER_HOLD = "user_hold"
    ABORTED = "aborted"
    COMPLETED = "completed"


class SpeakRole(str, Enum):
    INITIAL = "initial"  # 第 1 轮独立陈述
    REBUTTAL = "rebuttal"  # 第 N 轮针对发言
    FREE_ADDENDUM = "free_addendum"  # 自由补充（可附在 rebuttal 之后）
    FINAL = "final"  # 最终陈述
    CONSULTATION = "consultation"  # 外部咨询返回


class ArgumentStatus(str, Enum):
    ACTIVE = "active"
    CONVERGED = "converged"
    REJECTED = "rejected"
    REPLACED = "replaced"  # 被新轮次的更好表述替代


class ModeratorAction(str, Enum):
    CONTINUE = "continue"
    CONVERGE = "converge"
    ASK_USER = "ask_user"
    ENTER_FINAL = "enter_final"
    ABORT = "abort"
    EXTERNAL_CONSULT = "external_consult"


class DebateMode(str, Enum):
    """'non_debate' = 1 轮非辩论（v5 兼容）；'standard' = 多轮辩论。"""
    NON_DEBATE = "non_debate"
    STANDARD = "standard"


# =============================================================================
# 配置类
# =============================================================================

@dataclass(frozen=True, kw_only=True)
class ConvergenceTuning:
    score_threshold: float = 0.65  # 综合得分阈值
    require_consecutive: int = 1  # 需连续 N 轮达标
    overlap_hard_threshold: float = 0.70  # 硬收敛：重叠率
    new_arg_hard_threshold: float = 0.50  # 硬收敛：新增论点密度
    weights: tuple[float, float, float] = (0.4, 0.4, 0.2)  # overlap, density, drift
    # 权重和必须 = 1.0（构造时校验）

    def __post_init__(self) -> None:
        if abs(sum(self.weights) - 1.0) > 0.001:
            raise ValueError(f"Weights must sum to 1.0, got {self.weights}")


@dataclass(frozen=True, kw_only=True)
class DebateConfig:
    mode: DebateMode = DebateMode.STANDARD
    max_rounds: int = 5
    min_initial_experts: int = 3
    max_initial_experts: int = 6
    min_experts_to_continue: int = 2  # 少于则强制 enter_final
    max_external_consultations_per_round: int = 2
    external_consultation_timeout_s: float = 30.0
    expert_speak_timeout_s: float = 60.0
    convergence: ConvergenceTuning = field(default_factory=ConvergenceTuning)
    require_targeted_argument: bool = True  # 第 N>=2 轮发言必须针对
    allow_free_addendum: bool = True


# =============================================================================
# 核心数据类
# =============================================================================

@dataclass(frozen=True, kw_only=True)
class ArgumentRef:
    """轻量引用，用于跨轮引用一个论点（不进 LLM 上下文）。"""
    argument_id: ArgumentId
    author_id: ExpertId
    round_number: RoundNumber


@dataclass(frozen=True, kw_only=True)
class Argument:
    """一条具体论点（菜单中的一行）。"""
    argument_id: ArgumentId  # "A-R1-002" 编码规则: <作者首字母>-R<轮次>-<序号>
    round_number: RoundNumber
    author_id: ExpertId
    author_name: str
    claim: str  # 观点
    rationale: str  # 理由
    supports: tuple[str, ...] = ()  # 证据/论据
    confidence: float = 0.5  # 该论点的确信度
    methodology_used: MethodId | None = None  # 引用过的方法论
    status: ArgumentStatus = ArgumentStatus.ACTIVE
    original_quote: str = ""  # 从发言原文截取的关键句


@dataclass(frozen=True, kw_only=True)
class SuggestedArgument:
    """Moderator 解析器从发言中提取的候选论点（待评估）。"""
    claim: str
    rationale: str
    quote: str
    confidence: float
    targets: tuple[ArgumentRef, ...] = ()  # 发言针对的论点
    methodology_call: MethodologyCall | None = None


@dataclass(frozen=True, kw_only=True)
class ArgumentMenu:
    round_number: RoundNumber
    items: tuple[Argument, ...] = ()  # 本轮有效论点
    converged: tuple[Argument, ...] = ()  # 已在历史轮次收敛的
    focus: tuple[str, ...] = ()  # 建议下轮重点关注
    discarded: tuple[SuggestedArgument, ...] = ()  # 过滤掉的候选及原因

    def active(self) -> tuple[Argument, ...]:
        return tuple(a for a in self.items if a.status == ArgumentStatus.ACTIVE)

    def by_id(self, argument_id: ArgumentId) -> Argument | None:
        for arg in self.items:
            if arg.argument_id == argument_id:
                return arg
        return None


@dataclass(frozen=True, kw_only=True)
class SpeakPrompt:
    session_id: SessionId
    round_number: RoundNumber
    role: SpeakRole
    question: str  # 原始用户问题
    argument_menu: ArgumentMenu | None = None  # None 表示 initial
    context_summary: str = ""  # 主持人对当前态势的概括
    targeted_arguments: tuple[ArgumentRef, ...] = ()  # 限定本轮必须回应的论点
    free_addendum_max_chars: int = 600
    methodology_hints: tuple[MethodId, ...] = ()
    methodology_feedback: tuple[MethodologyResult, ...] = ()  # 上一轮方法论反馈
    constraints: tuple[str, ...] = ()  # 例如 "必须至少针对一个论点"
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, kw_only=True)
class MethodologyCall:
    method_id: MethodId
    arguments: dict[str, Any]  # 方法论参数
    caller_id: ExpertId  # 哪一位专家触发的
    requested_at: float


@dataclass(frozen=True, kw_only=True)
class MethodologyResult:
    method_id: MethodId
    output: str  # 方法论视角的输出
    validity: str  # "ok" | "misuse" | "inconclusive"
    misuse_reason: str | None = None
    prompt_injection: str = ""  # 注入到下一轮 prompt 的文本
    elapsed_s: float = 0.0
    # --- v6 增强字段 ---
    verdict: str = ""  # "confirmed" | "questionable" | "rejected"
    findings: tuple[str, ...] = ()  # 方法论发现的论点问题列表
    reframed_claim: str = ""  # 方法论视角下的重新表述
    confidence_impact: float = 0.0  # 对置信度的影响，-0.3 到 +0.3


@dataclass(frozen=True, kw_only=True)
class ExpertStatement:
    expert_id: ExpertId
    expert_name: str
    role: SpeakRole
    targeted_argument: ArgumentRef | None = None  # 主要针对的论点
    extra_targets: tuple[ArgumentRef, ...] = ()
    content: str  # 发言正文（已含针对+补充）
    free_addendum: str | None = None  # 单独抽取的自由补充部分
    methodology_call: MethodologyCall | None = None
    methodology_result: MethodologyResult | None = None
    confidence: float = 0.5
    suggested_arguments: tuple[SuggestedArgument, ...] = ()  # 候选论点（供 Moderator 评估）
    raw: Any | None = None  # 底层 v5 PerspectiveOutput（如有）
    warnings: tuple[str, ...] = ()
    elapsed_s: float = 0.0


@dataclass(frozen=True, kw_only=True)
class ConvergenceSignal:
    round_number: RoundNumber
    overlap_rate: float = 0.0  # 0-1，本轮与上轮论点的 Jaccard 相似度
    new_arg_density: float = 0.0  # 每专家平均新论点（active 状态）
    confidence_drift: float = 0.0  # 0-1，跨专家平均 |conf_curr - conf_prev|
    score: float = 0.0  # 综合 0-1
    converged: bool = False  # 综合阈值 + 连续次数
    hard_converged: bool = False  # 硬规则触发
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, kw_only=True)
class ExternalConsultationRequest:
    expert_id: ExpertId
    question: str
    relevant_arguments: tuple[ArgumentRef, ...] = ()
    context_summary: str = ""
    max_response_chars: int = 1500
    deadline_s: float = 30.0


@dataclass(frozen=True, kw_only=True)
class ExternalConsultation:
    request: ExternalConsultationRequest
    response_text: str = ""
    response_arguments: tuple[SuggestedArgument, ...] = ()
    received_at: float = 0.0
    timed_out: bool = False


@dataclass(frozen=True, kw_only=True)
class RosterChange:
    action: str  # "add" | "remove" | "replace"
    expert_id: ExpertId
    reason: str
    proposed_by: str = "moderator"  # "moderator" | "user" | "system"
    context_to_pass: tuple[ArgumentRef, ...] = ()  # 加入时给新专家的论点


@dataclass(frozen=True, kw_only=True)
class RosterChangeRequest:
    change: RosterChange | None = None
    external_consult: ExternalConsultationRequest | None = None


@dataclass(frozen=True, kw_only=True)
class ModeratorDecision:
    action: Moderato


@dataclass(frozen=True, kw_only=True)
class ModeratorDecision:
    action: ModeratorAction
    reason: str
    question_to_user: str | None = None
    roster_change: RosterChangeRequest | None = None
    suggested_methodology_for: tuple[tuple[ExpertId, MethodId], ...] | None = None
    hints: tuple[str, ...] = ()
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, kw_only=True)
class Round:
    round_number: RoundNumber
    menu: ArgumentMenu
    statements: tuple[ExpertStatement, ...]
    convergence_signal: ConvergenceSignal | None = None
    moderator_decision: ModeratorDecision | None = None
    started_at: float = 0.0
    ended_at: float = 0.0


@dataclass(frozen=True, kw_only=True)
class FinalConsensus:
    consensus_points: tuple[str, ...] = ()
    divergence_points: tuple[str, ...] = ()
    root_contradictions: tuple[str, ...] = ()
    suggestions: tuple[str, ...] = ()
    final_stmts: tuple[ExpertStatement, ...] = ()
    raw_outputs: tuple[Any, ...] = ()
    external_views: tuple[str, ...] = ()  # 外部咨询观点（§2.10 三层信息源之一）


@dataclass(frozen=True, kw_only=True)
class DebateSession:
    session_id: SessionId
    question: str
    context: dict
    config: DebateConfig
    expert_pool: ExpertPool
    initial_panel: tuple[Expert, ...] = ()
    active_experts: tuple[Expert, ...] = ()
    rounds: tuple[Round, ...] = ()
    final_stmts: tuple[ExpertStatement, ...] = ()
    final_consensus: FinalConsensus | None = None
    external_consultations: tuple[ExternalConsultation, ...] = ()
    status: SessionStatus = SessionStatus.INIT
    stats: dict[str, Any] = field(default_factory=dict)
    recorder: SessionRecorder | None = None
    started_at: float = 0.0


# =============================================================================
# Protocol 定义
# =============================================================================

@runtime_checkable
class Expert(Protocol):
    """专家协议"""
    @property
    def id(self) -> ExpertId: ...
    @property
    def name(self) -> str: ...
    @property
    def description(self) -> str: ...
    @property
    def domain(self) -> str: ...
    @property
    def trigger_keywords(self) -> tuple[str, ...]: ...
    @property
    def is_methodology(self) -> bool: ...

    def speak(self, prompt: SpeakPrompt) -> ExpertStatement: ...


@runtime_checkable
class ExpertPool(Protocol):
    """专家池协议"""
    def register(self, expert: Expert) -> None: ...
    def unregister(self, expert_id: ExpertId) -> None: ...
    def get(self, expert_id: ExpertId) -> Expert | None: ...
    def list_registered(self) -> tuple[Expert, ...]: ...
    def list_active_in_session(self, session: DebateSession) -> tuple[Expert, ...]: ...
    def suggest_for(self, question: str, *, top_k: int = 5) -> tuple[Expert, ...]: ...
    def apply_roster_change(self, session: DebateSession, change: RosterChange) -> bool: ...


@runtime_checkable
class MethodologyProvider(Protocol):
    """方法论提供者协议"""
    @property
    def method_id(self) -> MethodId: ...
    @property
    def display_name(self) -> str: ...
    @property
    def summary(self) -> str: ...
    @property
    def when_to_use(self) -> str: ...
    @property
    def keywords(self) -> tuple[str, ...]: ...

    def is_applicable(self, claim: str, context: dict) -> tuple[bool, str]: ...
    def call(self, call: MethodologyCall) -> MethodologyResult: ...


@runtime_checkable
class MethodologyRegistry(Protocol):
    """方法论注册表协议"""
    def register(self, provider: MethodologyProvider) -> None: ...
    def unregister(self, method_id: MethodId) -> None: ...
    def get(self, method_id: MethodId) -> MethodologyProvider | None: ...
    def list_all(self) -> tuple[MethodologyProvider, ...]: ...
    def suggest_for(self, claim: str, *, top_k: int = 3) -> tuple[MethodologyProvider, ...]: ...
    def call(self, call: MethodologyCall) -> MethodologyResult: ...


@runtime_checkable
class LLMProvider(Protocol):
    """LLM 提供者协议"""
    def complete(self, prompt: str, *, system: str | None = None,
                 temperature: float = 0.2, max_tokens: int = 2000) -> str: ...
    def complete_json(self, prompt: str, *, system: str | None = None,
                      schema: dict | None = None) -> dict: ...


@runtime_checkable
class SessionRecorder(Protocol):
    """会话记录器协议"""
    def on_session_start(self, session: DebateSession) -> None: ...
    def on_round_start(self, round: Round) -> None: ...
    def on_statement(self, stmt: ExpertStatement) -> None: ...
    def on_menu_built(self, menu: ArgumentMenu) -> None: ...
    def on_convergence(self, signal: ConvergenceSignal) -> None: ...
    def on_decision(self, decision: ModeratorDecision) -> None: ...
    def on_user_question(self, q: UserQuestion, r: UserResponse | None) -> None: ...
    def on_external_consultation(self, c: ExternalConsultation) -> None: ...
    def on_session_end(self, session: DebateSession) -> None: ...
    def render(self) -> str: ...
    def to_dict(self) -> dict: ...


@dataclass(frozen=True, kw_only=True)
class UserQuestion:
    question_id: QuestionId
    text: str
    options: tuple[str, ...] = ()
    triggered_by: str = ""
    context: dict = field(default_factory=dict)


@dataclass(frozen=True, kw_only=True)
class UserResponse:
    question_id: QuestionId | None
    answer: str
    new_information: tuple[str, ...] = ()
    answered_at: float = 0.0


@runtime_checkable
class UserInteraction(Protocol):
    """用户交互协议"""
    def ask(self, question: UserQuestion) -> UserResponse: ...
    def on_user_input(self, text: str) -> ModeratorDirective: ...


@dataclass(frozen=True, kw_only=True)
class ModeratorDirective:
    action: str
    payload: dict = field(default_factory=dict)


# =============================================================================
# 辅助函数
# =============================================================================

def generate_argument_id(round_number: RoundNumber, index: int) -> ArgumentId:
    """
    生成论点 ID。

    格式：<作者首字母>-R<轮次>-<序号>
    例如："A-R1-002"
    """
    return ArgumentId(f"A-R{int(round_number)}-{index:03d}")


# =============================================================================
# 导出
# =============================================================================

__all__ = [
    # ID 类型
    "SessionId", "RoundNumber", "ArgumentId", "ExpertId", "MethodId", "QuestionId",
    # 枚举
    "SessionStatus", "SpeakRole", "ArgumentStatus", "ModeratorAction", "DebateMode",
    # 配置
    "ConvergenceTuning", "DebateConfig",
    # 数据类
    "ArgumentRef", "Argument", "SuggestedArgument", "ArgumentMenu",
    "SpeakPrompt", "MethodologyCall", "MethodologyResult", "ExpertStatement",
    "ConvergenceSignal", "ExternalConsultationRequest", "ExternalConsultation",
    "RosterChange", "RosterChangeRequest", "ModeratorDecision",
    "Round", "FinalConsensus", "DebateSession",
    "UserQuestion", "UserResponse", "ModeratorDirective",
    # Protocol
    "Expert", "ExpertPool", "MethodologyProvider", "MethodologyRegistry",
    "LLMProvider", "SessionRecorder", "UserInteraction",
    # 辅助函数
    "generate_argument_id",
]
