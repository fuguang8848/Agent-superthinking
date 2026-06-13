# 超思考 v6 · 接口契约

> 状态：Phase 1 设计稿
> 日期：2026-06-05
> 范围：v6 各模块的 Protocol / Dataclass 完整签名
> 目的：给后端/QA 提供"接口形状准确"的契约（不要求可运行，但要求类型完整）

> **约定**
> - 所有 Dataclass 用 `@dataclass(frozen=True, kw_only=True)`（`frozen` 便于不可变推理，`kw_only` 便于向前兼容）
> - 所有跨模块依赖用 `typing.Protocol` 描述（运行时可由 `@runtime_checkable` 校验）
> - ID 类型用 `NewType` 包裹以避免字符串混用
> - 默认依赖仅 `dataclasses`/`typing`/`enum`/`time`；`pydantic` 在 v6.types 提供 `validate()` 方法的"软校验"可选钩子

---

## 0. ID 类型与状态机常量

```python
# v6/types.py
from typing import NewType
from enum import Enum

SessionId = NewType("SessionId", str)
RoundNumber = NewType("RoundNumber", int)        # 1-based
ArgumentId = NewType("ArgumentId", str)          # "A-R1-002"
ExpertId = NewType("ExpertId", str)
MethodId = NewType("MethodId", str)
QuestionId = NewType("QuestionId", str)


class SessionStatus(str, Enum):
    INIT = "init"
    RUNNING = "running"
    CONVERGED = "converged"
    MAX_ROUNDS = "max_rounds"
    USER_HOLD = "user_hold"            # 等待用户回复
    ABORTED = "aborted"
    COMPLETED = "completed"            # 已输出最终结论


class SpeakRole(str, Enum):
    INITIAL = "initial"                # 第 1 轮独立陈述
    REBUTTAL = "rebuttal"              # 第 N 轮针对发言
    FREE_ADDENDUM = "free_addendum"    # 自由补充（可附在 rebuttal 之后）
    FINAL = "final"                    # 最终陈述
    CONSULTATION = "consultation"      # 外部咨询返回


class ArgumentStatus(str, Enum):
    ACTIVE = "active"
    CONVERGED = "converged"
    REJECTED = "rejected"
    REPLACED = "replaced"              # 被新轮次的更好表述替代


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
```

---

## 1. DebateConfig（运行期配置）

```python
# v6/types.py
from dataclasses import dataclass

@dataclass(frozen=True, kw_only=True)
class ConvergenceTuning:
    score_threshold: float = 0.65            # 综合得分阈值
    require_consecutive: int = 1             # 需连续 N 轮达标
    overlap_hard_threshold: float = 0.70     # 硬收敛：重叠率
    new_arg_hard_threshold: float = 0.50     # 硬收敛：新增论点密度
    weights: tuple[float, float, float] = (0.4, 0.4, 0.2)  # overlap, density, drift
    # 权重和必须 = 1.0（构造时校验）

@dataclass(frozen=True, kw_only=True)
class DebateConfig:
    mode: DebateMode = DebateMode.STANDARD
    max_rounds: int = 5
    min_initial_experts: int = 3
    max_initial_experts: int = 6
    min_experts_to_continue: int = 2         # 少于则强制 enter_final
    max_external_consultations_per_round: int = 2
    external_consultation_timeout_s: float = 30.0
    expert_speak_timeout_s: float = 60.0
    convergence: ConvergenceTuning = field(default_factory=ConvergenceTuning)
    require_targeted_argument: bool = True   # 第 N>=2 轮发言必须针对
    allow_free_addendum: bool = True
```

---

## 2. Argument / ArgumentMenu / ArgumentRef（核心辩论单元）

```python
# v6/types.py
from dataclasses import dataclass, field

@dataclass(frozen=True, kw_only=True)
class ArgumentRef:
    """轻量引用，用于跨轮引用一个论点（不进 LLM 上下文）。"""
    argument_id: ArgumentId
    author_id: ExpertId
    round_number: RoundNumber

@dataclass(frozen=True, kw_only=True)
class Argument:
    """一条具体论点（菜单中的一行）。"""
    argument_id: ArgumentId                   # "A-R1-002"  编码规则: <作者首字母>-R<轮次>-<序号>
    round_number: RoundNumber
    author_id: ExpertId
    author_name: str
    claim: str                                # 观点
    rationale: str                            # 理由
    supports: tuple[str, ...] = ()            # 证据/论据
    confidence: float = 0.5                   # 该论点的确信度
    methodology_used: MethodId | None = None  # 引用过的方法论
    status: ArgumentStatus = ArgumentStatus.ACTIVE
    original_quote: str = ""                  # 从发言原文截取的关键句

@dataclass(frozen=True, kw_only=True)
class SuggestedArgument:
    """Moderator 解析器从发言中提取的候选论点（待评估）。"""
    claim: str
    rationale: str
    quote: str
    confidence: float
    targets: tuple[ArgumentRef, ...] = ()    # 发言针对的论点
    methodology_call: "MethodologyCall | None" = None

@dataclass(frozen=True, kw_only=True)
class ArgumentMenu:
    round_number: RoundNumber
    items: tuple[Argument, ...]                # 本轮有效论点
    converged: tuple[Argument, ...] = ()       # 已在历史轮次收敛的
    focus: tuple[str, ...] = ()                # 建议下轮重点关注
    discarded: tuple[SuggestedArgument, ...] = ()  # 过滤掉的候选及原因

    def active(self) -> tuple[Argument, ...]:
        return tuple(a for a in self.items if a.status == ArgumentStatus.ACTIVE)

    def by_id(self, argument_id: ArgumentId) -> Argument | None:
        ...
```

---

## 3. ExpertStatement / SpeakPrompt（专家发言）

```python
# v6/types.py
from typing import Any, Protocol, runtime_checkable

@dataclass(frozen=True, kw_only=True)
class SpeakPrompt:
    session_id: SessionId
    round_number: RoundNumber
    role: SpeakRole
    question: str                              # 原始用户问题
    argument_menu: ArgumentMenu | None         # None 表示 initial
    context_summary: str                       # 主持人对当前态势的概括
    targeted_arguments: tuple[ArgumentRef, ...] = ()  # 限定本轮必须回应的论点
    free_addendum_max_chars: int = 600
    methodology_hints: tuple[MethodId, ...] = ()
    constraints: tuple[str, ...] = ()          # 例如 "必须至少针对一个论点"
    extra: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True, kw_only=True)
class MethodologyCall:
    method_id: MethodId
    arguments: dict[str, Any]                  # 方法论参数
    caller_id: ExpertId                        # 哪一位专家触发的
    requested_at: float

@dataclass(frozen=True, kw_only=True)
class MethodologyResult:
    method_id: MethodId
    output: str                                # 方法论视角的输出
    validity: str                              # "ok" | "misuse" | "inconclusive"
    misuse_reason: str | None = None
    prompt_injection: str                      # 注入到下一轮 prompt 的文本
    elapsed_s: float = 0.0

@dataclass(frozen=True, kw_only=True)
class ExpertStatement:
    expert_id: ExpertId
    expert_name: str
    role: SpeakRole
    targeted_argument: ArgumentRef | None      # 主要针对的论点
    extra_targets: tuple[ArgumentRef, ...] = ()
    content: str                               # 发言正文（已含针对+补充）
    free_addendum: str | None = None           # 单独抽取的自由补充部分
    methodology_call: MethodologyCall | None = None
    methodology_result: MethodologyResult | None = None
    confidence: float = 0.5
    suggested_arguments: tuple[SuggestedArgument, ...] = ()  # 候选论点（供 Moderator 评估）
    raw: Any | None = None                     # 底层 v5 PerspectiveOutput（如有）
    warnings: tuple[str, ...] = ()
    elapsed_s: float = 0.0

# ---- 格式验证（主持人/Orchestrator 共享） ----
@runtime_checkable
class ExpertStatementValidator(Protocol):
    def validate_initial(self, stmt: ExpertStatement) -> tuple[str, ...]:
        """返回错误信息列表；空列表表示合法。"""
        ...
    def validate_rebuttal(self, stmt: ExpertStatement) -> tuple[str, ...]:
        ...
    def validate_final(self, stmt: ExpertStatement) -> tuple[str, ...]:
        ...
```

---

## 4. Expert Protocol（专家参与接口）

```python
# v6/expert/expert.py
from typing import Protocol, runtime_checkable

@runtime_checkable
class Expert(Protocol):
    """v6 专家协议。v5 Perspective 通过 V5PerspectiveAdapter 适配。"""

    @property
    def id(self) -> ExpertId: ...
    @property
    def name(self) -> str: ...
    @property
    def description(self) -> str: ...
    @property
    def domain(self) -> str: ...                # "philosophy" / "gametheory" / ...
    @property
    def trigger_keywords(self) -> tuple[str, ...]: ...
    @property
    def is_methodology(self) -> bool: ...       # True 表示这是方法论型专家

    def speak(self, prompt: SpeakPrompt) -> ExpertStatement:
        """同步发言；超时由 Orchestrator 强制。"""
        ...
```

### 4.1 适配器（v5 Perspective → v6 Expert）

```python
# v6/expert/v5_adapter.py
class V5PerspectiveAdapter:
    """把 v5 Perspective 包装为 v6 Expert。"""

    def __init__(self, perspective: Any, *, role_map: dict[SpeakRole, str] | None = None):
        self._p = perspective
        self._role_map = role_map or {}

    @property
    def id(self) -> ExpertId: return ExpertId(self._p.id)
    @property
    def name(self) -> str: return self._p.name
    @property
    def description(self) -> str: return getattr(self._p, "description", "")
    @property
    def domain(self) -> str: return "unknown"
    @property
    def trigger_keywords(self) -> tuple[str, ...]: return tuple(getattr(self._p, "trigger_keywords", []))
    @property
    def is_methodology(self) -> bool: return False

    def speak(self, prompt: SpeakPrompt) -> ExpertStatement:
        # 把 SpeakPrompt 序列化成 v5 Perspective.think 的 (input, context)
        input_text = self._compose_input(prompt)
        context = self._compose_context(prompt)
        out = self._p.think(input_text, context)     # PerspectiveOutput
        return self._convert(out, prompt)

    def _compose_input(self, prompt: SpeakPrompt) -> str: ...
    def _compose_context(self, prompt: SpeakPrompt) -> dict: ...
    def _convert(self, out: "PerspectiveOutput", prompt: SpeakPrompt) -> ExpertStatement: ...
```

### 4.2 原生 v6 Expert 抽象

```python
# v6/expert/native.py
class NativeExpert(ABC):
    """v6 推荐的新专家基类；自带格式校验/错误隔离。"""
    id: str
    name: str
    description: str
    domain: str
    trigger_keywords: list[str]
    is_methodology: bool = False

    @abstractmethod
    def speak(self, prompt: SpeakPrompt) -> ExpertStatement: ...

    # 默认实现：从 ExpertStatement 构造"看起来合理"的 v5 PerspectiveOutput
    def to_v5_output(self, stmt: ExpertStatement) -> "PerspectiveOutput": ...
```

---

## 5. ExpertPool（动态专家池）

```python
# v6/pool/expert_pool.py
from typing import Protocol, runtime_checkable

@dataclass(frozen=True, kw_only=True)
class RosterChange:
    """主持人对阵容的变更提案。"""
    action: str                                 # "add" | "remove" | "replace"
    expert_id: ExpertId
    reason: str
    proposed_by: str = "moderator"              # "moderator" | "user" | "system"
    context_to_pass: tuple[ArgumentRef, ...] = ()  # 加入时给新专家的论点

@runtime_checkable
class ExpertPool(Protocol):
    def register(self, expert: Expert) -> None: ...
    def unregister(self, expert_id: ExpertId) -> None: ...
    def get(self, expert_id: ExpertId) -> Expert | None: ...
    def list_registered(self) -> tuple[Expert, ...]: ...
    def list_active_in_session(self, session: "DebateSession") -> tuple[Expert, ...]: ...

    def suggest_for(self, question: str, *, top_k: int = 5) -> tuple[Expert, ...]:
        """基于 trigger_keywords 评分；委托 v5 Router 实现。"""
        ...

    def apply_roster_change(self, session: "DebateSession", change: RosterChange) -> bool:
        """应用变更：把 expert 真正加入/移出 session.active_experts。"""
        ...
```

---

## 6. Methodology（方法论池）

```python
# v6/methods/types.py
@runtime_checkable
class MethodologyProvider(Protocol):
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

    def is_applicable(self, claim: str, context: dict) -> tuple[bool, str]:
        """返回 (是否适用, 原因)。用于主持人防"乱用"。"""
        ...

    def call(self, call: MethodologyCall) -> MethodologyResult: ...

@runtime_checkable
class MethodologyRegistry(Protocol):
    def register(self, provider: MethodologyProvider) -> None: ...
    def unregister(self, method_id: MethodId) -> None: ...
    def get(self, method_id: MethodId) -> MethodologyProvider | None: ...
    def list_all(self) -> tuple[MethodologyProvider, ...]: ...
    def suggest_for(self, claim: str, *, top_k: int = 3) -> tuple[MethodologyProvider, ...]: ...
    def call(self, call: MethodologyCall) -> MethodologyResult: ...
```

---

## 7. ConvergenceDetector

```python
# v6/convergence/detector.py
@dataclass(frozen=True, kw_only=True)
class ConvergenceSignal:
    round_number: RoundNumber
    overlap_rate: float            # 0-1，本轮与上轮论点的 Jaccard 相似度
    new_arg_density: float         # 每专家平均新论点（active 状态）
    confidence_drift: float        # 0-1，跨专家平均 |conf_curr - conf_prev|
    score: float                   # 综合 0-1
    converged: bool                # 综合阈值 + 连续次数
    hard_converged: bool           # 硬规则触发
    details: dict[str, Any] = field(default_factory=dict)

@runtime_checkable
class ConvergenceDetector(Protocol):
    def __init__(self, config: ConvergenceTuning) -> None: ...
    def observe(self, session: "DebateSession") -> ConvergenceSignal:
        """观察一个 session，计算当前轮收敛信号。"""
        ...
    def reset(self) -> None: ...
```

---

## 8. Moderator（主持人）

### 8.1 决策输出

```python
# v6/moderator/types.py
@dataclass(frozen=True, kw_only=True)
class ExternalConsultationRequest:
    expert_id: ExpertId
    question: str
    relevant_arguments: tuple[ArgumentRef, ...]
    context_summary: str
    max_response_chars: int = 1500
    deadline_s: float = 30.0

@dataclass(frozen=True, kw_only=True)
class ExternalConsultation:
    request: ExternalConsultationRequest
    response_text: str
    response_arguments: tuple[SuggestedArgument, ...] = ()
    received_at: float
    timed_out: bool = False

@dataclass(frozen=True, kw_only=True)
class RosterChangeRequest:
    """主持人发起的阵容变更（含加入/请离/外部咨询）。"""
    change: RosterChange | None = None
    external_consult: ExternalConsultationRequest | None = None

@dataclass(frozen=True, kw_only=True)
class ModeratorDecision:
    action: ModeratorAction
    reason: str
    question_to_user: str | None = None
    roster_change: RosterChangeRequest | None = None
    suggested_methodology_for: tuple[ExpertId, MethodId] | None = None
    hints: tuple[str, ...] = ()                      # 注入到专家下一轮 prompt
    extra: dict[str, Any] = field(default_factory=dict)
```

### 8.2 Moderator 接口

```python
# v6/moderator/moderator.py
@runtime_checkable
class Moderator(Protocol):
    def __init__(
        self,
        *,
        llm: "LLMProvider",
        config: DebateConfig,
        expert_pool: ExpertPool,
        methodology_registry: MethodologyRegistry,
        recorder: "SessionRecorder",
    ) -> None: ...

    def select_initial_panel(self, question: str, context: dict) -> tuple[Expert, ...]:
        """选 3-5 位初始专家。"""
        ...

    def build_menu(
        self,
        session: "DebateSession",
        statements: tuple[ExpertStatement, ...],
    ) -> ArgumentMenu:
        """从本轮发言构造下轮菜单。"""
        ...

    def decide(
        self,
        session: "DebateSession",
        last_signal: ConvergenceSignal | None,
    ) -> ModeratorDecision:
        """基于当前态势做下一步决策。"""
        ...

    def format_final_consensus(self, session: "DebateSession") -> "FinalConsensus":
        """生成会议结论（共识/分歧/未解决矛盾/建议）。"""
        ...

    def ask_user(self, session: "DebateSession", reason: str) -> "UserQuestion": ...
```

### 8.3 主持人使用的 LLM Provider

```python
# v6/llm/provider.py
@runtime_checkable
class LLMProvider(Protocol):
    def complete(self, prompt: str, *, system: str | None = None,
                 temperature: float = 0.2, max_tokens: int = 2000) -> str: ...
    def complete_json(self, prompt: str, *, system: str | None = None,
                      schema: dict | None = None) -> dict: ...
```

---

## 9. UserInteraction（用户交互）

```python
# v6/interaction/user_interaction.py
@dataclass(frozen=True, kw_only=True)
class UserQuestion:
    question_id: QuestionId
    text: str
    options: tuple[str, ...] = ()                  # 0 个表示自由回答
    triggered_by: str                              # "convergence" | "ambiguity" | "moderator_init" | "user"
    context: dict = field(default_factory=dict)

@dataclass(frozen=True, kw_only=True)
class UserResponse:
    question_id: QuestionId | None
    answer: str
    new_information: tuple[str, ...] = ()         # 解析出的新事实
    answered_at: float

@dataclass(frozen=True, kw_only=True)
class ModeratorDirective:
    """把用户输入解析为主持人可执行指令。"""
    action: str                                    # "continue" | "abort" | "add_expert" | "remove_expert" | "no_op"
    payload: dict = field(default_factory=dict)

@runtime_checkable
class UserInteraction(Protocol):
    def ask(self, question: UserQuestion) -> UserResponse: ...
    def on_user_input(self, text: str) -> ModeratorDirective: ...
```

---

## 10. SessionRecorder（记录器）

```python
# v6/recorder/recorder.py
@runtime_checkable
class SessionRecorder(Protocol):
    def on_session_start(self, session: "DebateSession") -> None: ...
    def on_round_start(self, round: "Round") -> None: ...
    def on_statement(self, stmt: ExpertStatement) -> None: ...
    def on_menu_built(self, menu: ArgumentMenu) -> None: ...
    def on_convergence(self, signal: ConvergenceSignal) -> None: ...
    def on_decision(self, decision: ModeratorDecision) -> None: ...
    def on_user_question(self, q: UserQuestion, r: UserResponse | None) -> None: ...
    def on_external_consultation(self, c: ExternalConsultation) -> None: ...
    def on_session_end(self, session: "DebateSession") -> None: ...

    def render(self) -> str: ...                   # 人读 markdown
    def to_dict(self) -> dict: ...                 # 机读 JSON
```

---

## 11. DebateSession / Round / FinalConsensus

```python
# v6/types.py
@dataclass(frozen=True, kw_only=True)
class Round:
    round_number: RoundNumber
    menu: ArgumentMenu
    statements: tuple[ExpertStatement, ...]        # 字典序排序后写入
    convergence_signal: ConvergenceSignal | None = None
    moderator_decision: ModeratorDecision | None = None
    started_at: float = 0.0
    ended_at: float = 0.0

@dataclass(frozen=True, kw_only=True)
class FinalConsensus:
    consensus_points: tuple[str, ...]              # 共识
    divergence_points: tuple[str, ...]             # 分歧
    root_contradictions: tuple[str, ...]           # 未解决的根本矛盾
    suggestions: tuple[str, ...]                  # 给用户的建议
    final_stmts: tuple[ExpertStatement, ...]       # 专家最终表态
    raw_outputs: tuple["PerspectiveOutput", ...] = ()  # 终态 Fusion 输入

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
    stats: dict[str, Any] = field(default_factory=dict)  # 成本/调用统计
    recorder: "SessionRecorder" = None             # type: ignore[assignment]
    started_at: float = 0.0
    ended_at: float | None = None
```

---

## 12. Orchestrator 接口

```python
# v6/orchestrator.py
@runtime_checkable
class SessionOrchestrator(Protocol):
    def __init__(
        self,
        *,
        config: DebateConfig,
        llm: "LLMProvider",
        expert_pool: ExpertPool,
        methodology_registry: MethodologyRegistry,
        moderator: Moderator,
        recorder: "SessionRecorder",
        interaction: UserInteraction,
    ) -> None: ...

    def run(self, session: DebateSession) -> DebateSession:
        """主循环：选专家 → 第一轮 → 辩论循环 → 终态。"""
        ...

    def run_single_round(self, session: DebateSession) -> Round: ...   # 调试用
    def finalize(self, session: DebateSession) -> DebateSession: ...   # 终态收敛/总结
```

---

## 13. v5 → v6 兼容适配器

```python
# v6/compat/jury_adapter.py
from super_thinking.core.jury import Jury, JuryResult     # v5
from super_thinking.core.router import RoutingResult      # v5
from super_thinking.perspectives._interface import PerspectiveOutput  # v5

def v5_jury_to_v6_session(jury: "Jury", question: str,
                          context: dict, mode: str,
                          selective_ids: list[str] | None) -> DebateSession: ...
def v6_session_to_v5_jury_result(session: DebateSession) -> JuryResult: ...

class JuryAdapter:
    """在 v5 Jury 内部使用：think() 实际委托给 v6 单轮退化模式。"""
    def __init__(self, jury: "Jury"):
        self._jury = jury
    def think(self, input: str, context: dict | None, mode: str,
              selective_ids: list[str] | None) -> JuryResult: ...
```

兼容性不变量（构造时校验）：
- `JuryResult.outputs` 中 value 是 v5 `PerspectiveOutput`（**不是** v6 `ExpertStatement`）
- `JuryResult.errors` / `routing_result` / `total_perspectives` / `successful` / `failed` 全部保留
- `JuryResult.get_outputs()` / `has_errors()` / `get_perspective_ids()` 行为不变

---

## 14. 接口不变量与可测试边界

| 接口 | 不变量 | 测试可 mock 边界 |
|------|--------|-----------------|
| `Expert.speak` | 纯函数：相同 prompt → 相同 statement（伪随机种子固定） | 注入 `FakeExpert` 列表 |
| `MethodologyProvider.call` | 纯函数 | 注入 `FakeMethodology` |
| `ConvergenceDetector.observe` | 纯计算 | 不依赖外部 |
| `Moderator.*` | 所有外部输入通过 Protocol 注入 | 注入 `DeterministicLLM` |
| `UserInteraction.ask` | 阻塞 | 注入 `FakeUserInteraction` |
| `SessionRecorder.*` | 全局副作用 | 注入 `InMemoryRecorder`/`NoopRecorder` |
| `LLMProvider.complete` | 阻塞 | 注入 `DeterministicProvider` |

---

## 15. 错误类型

```python
# v6/errors.py
class V6Error(Exception): ...
class ConfigError(V6Error): ...
class InvalidStateTransition(V6Error): ...
class ExpertError(V6Error):
    expert_id: ExpertId
    cause: str
class MethodologyError(V6Error):
    method_id: MethodId
    reason: str
class LLMError(V6Error): ...
class UserInteractionTimeout(V6Error): ...
class DebateAborted(V6Error):
    session: "DebateSession"
    reason: str
```

---

## 16. 接口版本策略

- v6.0 锁定本文档中的所有字段
- 新增字段 = minor（向后兼容）；删除/改语义 = major
- 旧字段加 `Deprecated` 后缀保留 1 个 minor 版本再移除
- Protocol 用 `runtime_checkable` 标记；测试用 `isinstance(obj, Protocol)` 验证

---

_楚灵 · 接口契约 Phase 1 · 2026-06-05_
