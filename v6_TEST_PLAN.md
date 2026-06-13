# 超思考 v6 · 可测试性规范

> 状态：Phase 1 设计稿
> 日期：2026-06-05
> 范围：给后端工程师与 QA 的可测试性规范
> 目标：**每个决策点都能被独立 mock/单测**；不依赖网络/真实 LLM/真实用户

---

## 1. 测试架构总览

### 1.1 三层测试金字塔

```
                 ▲
                ╱ ╲          E2E：完整辩论剧本（DeterministicProvider + FakeExpert）
               ╱───╲
              ╱     ╲       集成：模块协作（Orchestrator + Moderator + Pool + Recorder）
             ╱───────╲
            ╱         ╲     单元：纯计算/纯协议（Convergence、Extractor、Adapter、Validator）
           ╱───────────╲
```

### 1.2 测试目录

```
tests/
├── test_core.py                # 现有 v5 测试，必须保持绿
├── test_v6/                    # v6 新增
│   ├── conftest.py             # 共享 fixtures：FakeExpert, DeterministicProvider 等
│   ├── test_types.py           # Dataclass 不变量
│   ├── test_argument_extractor.py
│   ├── test_menu_builder.py
│   ├── test_convergence.py
│   ├── test_expert_v5_adapter.py
│   ├── test_expert_pool.py
│   ├── test_methodology_registry.py
│   ├── test_user_interaction.py
│   ├── test_recorder.py
│   ├── test_moderator.py
│   ├── test_orchestrator.py
│   ├── test_compat_jury_adapter.py
│   ├── fixtures/               # 脚本化输入
│   │   ├── scripts_converge_3rounds.json
│   │   ├── scripts_diverge_5rounds.json
│   │   ├── scripts_user_intervention.json
│   │   └── scripts_external_consultation.json
│   └── e2e/
│       ├── test_debate_converge.py
│       ├── test_debate_max_rounds.py
│       ├── test_debate_user_hold.py
│       └── test_compat_v5_equivalence.py
```

### 1.3 Fixtures 共享层（`conftest.py`）

```python
# tests/test_v6/conftest.py
import pytest, time
from super_thinking.v6.types import (
    ExpertId, SpeakRole, SpeakPrompt, ExpertStatement,
    Argument, ArgumentRef, ArgumentMenu, RoundNumber,
    MethodId, MethodologyCall, MethodologyResult,
)
from super_thinking.v6.expert.expert import Expert
from super_thinking.v6.llm.provider import LLMProvider
from super_thinking.v6.recorder.recorder import SessionRecorder
from super_thinking.v6.interaction.user_interaction import (
    UserInteraction, UserQuestion, UserResponse
)
from super_thinking.v6.methods.provider import MethodologyProvider


# ---- 1. FakeExpert：可脚本化的专家 ----
class FakeExpert:
    def __init__(self, expert_id: str, name: str, scripts: dict[SpeakRole, list[str]]):
        self._id = ExpertId(expert_id)
        self._name = name
        self._scripts = scripts
        self.calls: list[SpeakPrompt] = []

    @property
    def id(self) -> ExpertId: return self._id
    @property
    def name(self) -> str: return self._name
    @property
    def description(self) -> str: return f"Fake expert {self._id}"
    @property
    def domain(self) -> str: return "test"
    @property
    def trigger_keywords(self) -> tuple[str, ...]: return ()
    @property
    def is_methodology(self) -> bool: return False

    def speak(self, prompt: SpeakPrompt) -> ExpertStatement:
        self.calls.append(prompt)
        text = self._scripts.get(prompt.role, [""])[0]
        return ExpertStatement(
            expert_id=self._id, expert_name=self._name, role=prompt.role,
            targeted_argument=prompt.targeted_arguments[0] if prompt.targeted_arguments else None,
            content=text, confidence=0.7,
        )


# ---- 2. DeterministicProvider：按 prompt 关键字段路由返回 ----
class DeterministicProvider:
    def __init__(self, script: dict[str, str] | None = None):
        self.script = script or {}
        self.calls: list[str] = []

    def complete(self, prompt: str, *, system: str | None = None,
                 temperature: float = 0.2, max_tokens: int = 2000) -> str:
        self.calls.append(prompt)
        for key, val in self.script.items():
            if key in prompt:
                return val
        return "{}"   # 兜底空 JSON

    def complete_json(self, prompt: str, *, system: str | None = None,
                      schema: dict | None = None) -> dict:
        import json
        return json.loads(self.complete(prompt, system=system))


# ---- 3. InMemoryRecorder：捕获所有事件 ----
class InMemoryRecorder:
    def __init__(self):
        self.events: list[tuple[str, object]] = []
    def on_session_start(self, s): self.events.append(("start", s))
    def on_round_start(self, r): self.events.append(("round_start", r))
    def on_statement(self, s): self.events.append(("stmt", s))
    def on_menu_built(self, m): self.events.append(("menu", m))
    def on_convergence(self, s): self.events.append(("conv", s))
    def on_decision(self, d): self.events.append(("decision", d))
    def on_user_question(self, q, r): self.events.append(("user_q", (q, r)))
    def on_external_consultation(self, c): self.events.append(("consult", c))
    def on_session_end(self, s): self.events.append(("end", s))
    def render(self) -> str: return "\n".join(str(e) for e in self.events)
    def to_dict(self) -> dict: return {"events": [(k, str(v)) for k, v in self.events]}


# ---- 4. FakeUserInteraction：可脚本化的用户 ----
class FakeUserInteraction:
    def __init__(self, scripted_answers: list[str] | None = None,
                 auto_abort: bool = False):
        self._answers = list(scripted_answers or [])
        self.asked: list[UserQuestion] = []
        self.auto_abort = auto_abort
    def ask(self, q: UserQuestion) -> UserResponse:
        self.asked.append(q)
        if self.auto_abort:
            raise RuntimeError("user aborted")
        ans = self._answers.pop(0) if self._answers else ""
        return UserResponse(question_id=q.question_id, answer=ans,
                            answered_at=time.time())
    def on_user_input(self, text: str): return None


# ---- 5. FakeMethodologyProvider：可脚本化的方法论 ----
class FakeMethodologyProvider:
    def __init__(self, method_id: str, applicable: bool = True,
                 output: str = "ok"):
        self._id = MethodId(method_id)
        self._applicable = applicable
        self._output = output
    @property
    def method_id(self): return self._id
    @property
    def display_name(self): return self._id
    @property
    def summary(self): return "fake"
    @property
    def when_to_use(self): return "test"
    @property
    def keywords(self): return ()
    def is_applicable(self, claim, ctx): return (self._applicable, "ok" if self._applicable else "n/a")
    def call(self, call: MethodologyCall) -> MethodologyResult:
        return MethodologyResult(method_id=self._id, output=self._output,
                                 validity="ok", prompt_injection=f"[{self._id}] {self._output}")


@pytest.fixture
def fake_experts():
    return [
        FakeExpert("alpha", "Alpha", {
            SpeakRole.INITIAL: ["alpha initial claim, because X"],
            SpeakRole.REBUTTAL: ["alpha rebuttal, because Y"],
            SpeakRole.FINAL: ["alpha final, because Z"],
        }),
        FakeExpert("beta", "Beta", {
            SpeakRole.INITIAL: ["beta initial claim, because P"],
            SpeakRole.REBUTTAL: ["beta rebuttal, because Q"],
            SpeakRole.FINAL: ["beta final, because R"],
        }),
        FakeExpert("gamma", "Gamma", {
            SpeakRole.INITIAL: ["gamma initial claim, because M"],
            SpeakRole.REBUTTAL: ["gamma rebuttal, because N"],
            SpeakRole.FINAL: ["gamma final, because O"],
        }),
    ]

@pytest.fixture
def deterministic_llm():
    return DeterministicProvider()

@pytest.fixture
def recorder():
    return InMemoryRecorder()

@pytest.fixture
def fake_user():
    return FakeUserInteraction(scripted_answers=["用户补充的事实1"])

@pytest.fixture
def fake_methodology():
    reg = ...  # 由 test_methodology_registry.py 自己构造
    return reg
```

---

## 2. 每个模块的可 mock 边界

| 模块 | 依赖 | mock 边界 | 单元测试要点 |
|------|------|----------|--------------|
| `v6.types` | 无 | 无（纯 dataclass） | `__post_init__` 校验；frozen 不变性 |
| `v6.expert.expert` | 无 | `FakeExpert` | Protocol 字段全部存在 |
| `v6.expert.v5_adapter` | v5 Perspective | `FakePerspective` | 输入转换 / 输出转换 / 字段对齐 |
| `v6.expert.native.NativeExpert` | 抽象 | 子类 | `speak` 抽象方法 |
| `v6.pool.expert_pool` | `Expert` 列表 | `FakeExpert` | `register/unregister/suggest_for/apply_roster_change` |
| `v6.methods.registry` | `MethodologyProvider` | `FakeMethodologyProvider` | `register/call/is_applicable` |
| `v6.methods.builtin` | 无 | 无 | 18 个方法论的语法/接口 |
| `v6.moderator.argument_extractor` | 无（纯函数） | 无 | 4 标准机械过滤；不依赖 LLM |
| `v6.moderator.menu_builder` | `LLMProvider` | `DeterministicProvider` | 输入语句 → 菜单 |
| `v6.moderator.moderator` | LLM/ExpertPool/Methodology/Recorder | 全部 fake | `decide` 输出枚举；reason 必填 |
| `v6.convergence.detector` | `DebateSession` | 构造任意 session | 三指标公式 / 阈值 / 硬规则 |
| `v6.interaction.user_interaction` | 用户 | `FakeUserInteraction` | `ask` 阻塞；timeout 行为 |
| `v6.recorder.in_memory` | 无 | 无 | 7 个钩子顺序与字段 |
| `v6.recorder.file_recorder` | 文件系统 | `tmp_path` | JSONL 追加写 |
| `v6.llm.deterministic` | 无 | 无 | 路由逻辑 |
| `v6.llm.openai_compat` | HTTP | `responses` mock | 不在 v6 必测范围（可选） |
| `v6.orchestrator` | Moderator/Expert/Pool/Recorder/UI | 全部 fake | 状态机转移；max_rounds 兜底 |
| `v6.compat.jury_adapter` | v5 Jury + v6 Session | `FakeJury`（可选） | v5 JuryResult 字段对齐 |

---

## 3. 单元测试规范

### 3.1 收敛算法（最高优先，必须确定性）

```python
# tests/test_v6/test_convergence.py
def test_overlap_rate_jaccard():
    """两轮菜单论点的 Jaccard 相似度计算正确。"""
    from super_thinking.v6.convergence.signals import overlap_rate
    prev = {"A-R1-001", "A-R1-002", "A-R1-003"}
    curr = {"A-R1-001", "A-R1-002", "B-R2-001"}
    assert abs(overlap_rate(prev, curr) - 2/4) < 1e-9  # |∩|=2, |∪|=4

def test_new_arg_density_per_expert():
    from super_thinking.v6.convergence.signals import new_arg_density
    n_new, n_experts = 3, 5
    assert new_arg_density(n_new, n_experts) == 0.6

def test_confidence_drift_mean_abs():
    from super_thinking.v6.convergence.signals import confidence_drift
    prev = {"a": 0.5, "b": 0.8, "c": 0.6}
    curr = {"a": 0.6, "b": 0.7, "c": 0.6}
    # |0.1|+|0.1|+|0.0|)/3 ≈ 0.0667
    assert abs(confidence_drift(prev, curr) - 0.0667) < 1e-3

def test_score_threshold_triggers_converge():
    from super_thinking.v6.convergence.detector import ConvergenceDetector
    from super_thinking.v6.types import ConvergenceTuning
    det = ConvergenceDetector(ConvergenceTuning(score_threshold=0.65))
    session = build_session_with_3_rounds(score_per_round=[0.5, 0.6, 0.7])
    sig = det.observe(session)
    assert sig.converged is True
    assert sig.score >= 0.65

def test_hard_converge_rule():
    det = ConvergenceDetector(ConvergenceTuning(
        score_threshold=0.99,   # 高到正常不收敛
        overlap_hard_threshold=0.7,
        new_arg_hard_threshold=0.5,
    ))
    session = build_session_with_overlap_above_70_and_density_below_50()
    sig = det.observe(session)
    assert sig.hard_converged is True
    assert sig.converged is True

def test_max_rounds_forced_converge():
    det = ConvergenceDetector(ConvergenceTuning(score_threshold=0.99))
    session = build_session_with_5_rounds(score_per_round=[0.1]*5)
    assert det.observe(session).converged is False  # 算法未收敛
    # 但 Orchestrator 应该强制 enter_final
    orch = OrchestratorWithFakes(det=det, max_rounds=5)
    final = orch.run(session)
    assert final.status == SessionStatus.MAX_ROUNDS
```

### 3.2 论点提取器（纯函数）

```python
# tests/test_v6/test_argument_extractor.py
def test_extract_specific_argument_kept():
    from super_thinking.v6.moderator.argument_extractor import filter_candidates
    stmts = [
        ExpertStatement(
            expert_id=ExpertId("a"), expert_name="A", role=SpeakRole.INITIAL,
            content="关于X，我认为Y，因为Z。", confidence=0.8,
        ),
    ]
    kept, discarded = filter_candidates(stmts)
    assert len(kept) == 1
    assert kept[0].claim.startswith("Y")

def test_vague_argument_discarded():
    stmts = [ExpertStatement(
        expert_id=ExpertId("a"), expert_name="A", role=SpeakRole.INITIAL,
        content="这个问题很复杂，需要更多思考。", confidence=0.5,
    )]
    kept, discarded = filter_candidates(stmts)
    assert len(kept) == 0
    assert "具体性" in discarded[0].reason or "可反驳性" in discarded[0].reason

def test_duplicate_discarded_as_non_disagreement():
    stmts = [
        ExpertStatement(expert_id=ExpertId("a"), expert_name="A",
                        role=SpeakRole.INITIAL, content="X是好的。", confidence=0.8),
        ExpertStatement(expert_id=ExpertId("b"), expert_name="B",
                        role=SpeakRole.INITIAL, content="X是好的。", confidence=0.8),
    ]
    kept, _ = filter_candidates(stmts)
    assert len(kept) <= 1   # 分歧性过滤

def test_targeted_rebuttal_validates():
    """REBUTTAL 角色必须 targeted_argument 非空。"""
    from super_thinking.moderator.argument_extractor import validate_rebuttal_format
    bad = ExpertStatement(expert_id=ExpertId("a"), expert_name="A",
                          role=SpeakRole.REBUTTAL, content="泛泛而谈。",
                          targeted_argument=None)
    errors = validate_rebuttal_format(bad)
    assert any("targeted" in e.lower() or "针对" in e for e in errors)
```

### 3.3 V5 适配器

```python
# tests/test_v6/test_expert_v5_adapter.py
def test_v5_perspective_to_expert_round_trip():
    """v5 PerspectiveOutput 字段 → ExpertStatement → PerspectiveOutput 字段一致。"""
    from super_thinking.perspectives._interface import PerspectiveOutput
    from super_thinking.v6.expert.v5_adapter import V5PerspectiveAdapter

    class P:
        id = "x"; name = "X"; description = "..."
        trigger_keywords = ["k"]
        def think(self, input, context):
            return PerspectiveOutput(
                perspective_id="x", perspective_name="X",
                analysis="analysis", confidence=0.7,
                key_points=["k1", "k2"], tags=["t1"], warnings=["w1"],
            )

    adapter = V5PerspectiveAdapter(P())
    stmt = adapter.speak(SpeakPrompt(
        session_id=SessionId("s"), round_number=RoundNumber(1),
        role=SpeakRole.INITIAL, question="q",
    ))
    # 字段映射正确
    assert stmt.expert_id == ExpertId("x")
    assert stmt.expert_name == "X"
    assert "analysis" in stmt.content
    assert len(stmt.suggested_arguments) == 2   # 来自 key_points
    assert stmt.warnings == ("w1",)

def test_adapter_is_expert_protocol():
    from super_thinking.v6.expert.expert import Expert
    class P:
        id = "y"; name = "Y"; description = "d"
        trigger_keywords = []
        def think(self, input, context): return None
    assert isinstance(V5PerspectiveAdapter(P()), Expert)  # @runtime_checkable
```

### 3.4 专家池

```python
# tests/test_v6/test_expert_pool.py
def test_register_and_get(fake_experts):
    from super_thinking.v6.pool.expert_pool import InMemoryExpertPool
    pool = InMemoryExpertPool()
    for e in fake_experts:
        pool.register(e)
    assert pool.get(ExpertId("alpha")) is fake_experts[0]

def test_unregister(fake_experts):
    pool = InMemoryExpertPool()
    pool.register(fake_experts[0])
    pool.unregister(ExpertId("alpha"))
    assert pool.get(ExpertId("alpha")) is None

def test_suggest_for_returns_top_k(fake_experts):
    pool = InMemoryExpertPool()
    for e in fake_experts:
        pool.register(e)
    top = pool.suggest_for("alpha 主题", top_k=2)
    assert len(top) == 2

def test_roster_change_add_and_remove(fake_experts):
    pool = InMemoryExpertPool()
    session = ...  # 构造一个 DebateSession
    change = RosterChange(action="add", expert_id=ExpertId("alpha"), reason="视角缺失")
    assert pool.apply_roster_change(session, change) is True
    assert ExpertId("alpha") in [e.id for e in session.active_experts]
```

### 3.5 方法论池

```python
# tests/test_v6/test_methodology_registry.py
def test_register_and_call():
    reg = InMemoryMethodologyRegistry()
    p = FakeMethodologyProvider("gametheory", applicable=True, output="纳什均衡")
    reg.register(p)
    result = reg.call(MethodologyCall(
        method_id=MethodId("gametheory"), arguments={}, caller_id=ExpertId("a"),
        requested_at=0.0,
    ))
    assert result.validity == "ok"
    assert "纳什均衡" in result.prompt_injection

def test_unknown_method_returns_misuse():
    reg = InMemoryMethodologyRegistry()
    result = reg.call(MethodologyCall(method_id=MethodId("nope"), arguments={},
                                       caller_id=ExpertId("a"), requested_at=0.0))
    assert result.validity == "misuse"

def test_is_applicable_filters():
    p = FakeMethodologyProvider("x", applicable=False, output="")
    ok, _ = p.is_applicable("any claim", {})
    assert ok is False
```

### 3.6 主持人（Moderator）

```python
# tests/test_v6/test_moderator.py
def test_decide_returns_valid_action(fake_experts, deterministic_llm, recorder):
    from super_thinking.v6.moderator.moderator import DefaultModerator
    from super_thinking.v6.types import DebateConfig, DebateMode
    cfg = DebateConfig(mode=DebateMode.STANDARD, max_rounds=5)
    pool = InMemoryExpertPool()
    for e in fake_experts: pool.register(e)
    mreg = InMemoryMethodologyRegistry()
    mod = DefaultModerator(llm=deterministic_llm, config=cfg,
                           expert_pool=pool, methodology_registry=mreg,
                           recorder=recorder)
    session = build_session_with_3_rounds_signal_converged()
    decision = mod.decide(session, last_signal=None)
    assert decision.action in {a.value for a in ModeratorAction}
    assert decision.reason

def test_decide_ask_user_when_deep_divergence():
    # scripted llm returns "ask_user" with reason
    llm = DeterministicProvider({"分歧": json.dumps({
        "action": "ask_user", "reason": "...", "question_to_user": "X?",
    })})
    ...
    decision = mod.decide(session, last_signal=low_score_signal)
    assert decision.action == "ask_user"
    assert decision.question_to_user

def test_select_initial_panel_within_bounds(fake_experts):
    pool = InMemoryExpertPool()
    for e in fake_experts: pool.register(e)
    mod = DefaultModerator(llm=DeterministicProvider(), config=DebateConfig(),
                           expert_pool=pool, methodology_registry=InMemoryMethodologyRegistry(),
                           recorder=InMemoryRecorder())
    panel = mod.select_initial_panel("alpha question", {})
    assert 3 <= len(panel) <= 6
```

### 3.7 编排器（Orchestrator）

```python
# tests/test_v6/test_orchestrator.py
def test_run_converge_in_3_rounds(fake_experts, deterministic_llm, recorder, fake_user):
    cfg = DebateConfig(max_rounds=5)
    pool = InMemoryExpertPool(); [pool.register(e) for e in fake_experts]
    mreg = InMemoryMethodologyRegistry()
    mod = DefaultModerator(llm=scripted_llm_converge_3(), config=cfg, ...)
    orch = SessionOrchestrator(config=cfg, llm=scripted_llm_converge_3(),
                               expert_pool=pool, methodology_registry=mreg,
                               moderator=mod, recorder=recorder,
                               interaction=fake_user)
    session = build_init_session()
    final = orch.run(session)
    assert final.status == SessionStatus.CONVERGED
    assert len(final.rounds) == 3

def test_run_max_rounds_fallback(fake_experts, deterministic_llm, recorder, fake_user):
    orch = ...  # scripted llm 永不收敛
    final = orch.run(build_init_session())
    assert final.status == SessionStatus.MAX_ROUNDS
    assert len(final.rounds) == 5

def test_run_user_hold_then_resume(...):
    # Round 2 后主持人 ask_user，user 回答，Round 3 收敛
    ...

def test_run_external_consultation(...):
    ...

def test_invalid_state_transition_raises():
    # 手动构造一个非法状态转移
    ...
    with pytest.raises(InvalidStateTransition): ...
```

### 3.8 Recorder

```python
# tests/test_v6/test_recorder.py
def test_in_memory_captures_all_events():
    rec = InMemoryRecorder()
    rec.on_session_start(build_session())
    rec.on_round_start(build_round(1))
    rec.on_statement(build_statement())
    rec.on_menu_built(build_menu(1))
    rec.on_convergence(build_signal(1))
    rec.on_decision(build_decision())
    rec.on_session_end(build_session())
    kinds = [e[0] for e in rec.events]
    assert kinds == ["start","round_start","stmt","menu","conv","decision","end"]

def test_in_memory_to_dict_is_json_safe():
    rec = InMemoryRecorder()
    rec.on_session_start(build_session())
    d = rec.to_dict()
    json.dumps(d)   # 不抛

def test_file_recorder_appends_jsonl(tmp_path):
    from super_thinking.v6.recorder.file_recorder import FileRecorder
    path = tmp_path / "s.jsonl"
    rec = FileRecorder(path)
    rec.on_session_start(build_session())
    rec.on_session_end(build_session())
    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    json.loads(lines[0]); json.loads(lines[1])
```

### 3.9 v5 兼容适配器

```python
# tests/test_v6/test_compat_jury_adapter.py
def test_v5_jury_think_returns_compatible_juryresult():
    """旧 v5 调用走 v6 适配，返回 v5 JuryResult 字段不变。"""
    from super_thinking.core.jury import Jury
    from super_thinking.v6.compat import JuryAdapter

    jury = Jury(use_v6=True)
    result = jury.think("test", mode="force_all")
    # 字段集
    assert hasattr(result, "outputs")
    assert hasattr(result, "errors")
    assert hasattr(result, "routing_result")
    assert hasattr(result, "total_perspectives")
    assert hasattr(result, "successful")
    assert hasattr(result, "failed")
    assert hasattr(result, "get_outputs")
    assert hasattr(result, "has_errors")
    assert hasattr(result, "get_perspective_ids")
    # 类型
    for k, v in result.outputs.items():
        from super_thinking.perspectives._interface import PerspectiveOutput
        assert isinstance(v, PerspectiveOutput)

def test_v5_test_core_suite_still_passes():
    """tests/test_core.py 必须全绿。"""
    import subprocess
    r = subprocess.run(
        ["pytest", "tests/test_core.py", "-q"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stdout + r.stderr
```

---

## 4. 端到端测试（E2E）

```python
# tests/test_v6/e2e/test_debate_converge.py
def test_debate_converge_3_rounds_end_to_end(fake_experts, recorder):
    """完整辩论：3 轮后 status=CONVERGED；Recorder 事件序列与 v6_DATA_FLOW §12 一致。"""
    llm = scripted_llm_for_convergence()
    session = think_v6(
        "Should we use microservices or monolith?",
        config=DebateConfig(max_rounds=5),
        llm=llm,
        recorder=recorder,
        interaction=FakeUserInteraction(),
    )
    assert session.status == SessionStatus.CONVERGED
    assert len(session.rounds) == 3
    # 事件序列
    expected = ["start","round_start","stmt","stmt","stmt","menu",
                "conv","decision","round_start","stmt","stmt","stmt",
                "menu","conv","decision","round_start","stmt","stmt","stmt",
                "menu","conv","decision","stmt","stmt","stmt","end"]
    actual = [e[0] for e in recorder.events]
    assert actual == expected
```

---

## 5. 确定性测试点（QA 必查）

| # | 测试点 | 期望 |
|---|--------|------|
| 1 | 给定相同脚本化输入，3 轮后 status=CONVERGED | 必须 |
| 2 | 给定永不收敛脚本，max_rounds=5 → status=MAX_ROUNDS | 必须 |
| 3 | 收敛信号 score=0.0/0.65/1.0 边界 | 必须 |
| 4 | 硬规则 overlap≥0.7 ∧ density<0.5 → hard_converged=true | 必须 |
| 5 | 第 N≥2 轮无 targeted_argument → validate_rebuttal 返回错误 | 必须 |
| 6 | 主持人发起外部咨询 → Recorder.on_external_consultation 触发 | 必须 |
| 7 | 外部咨询超时 30s → 标 timed_out=true，不抛 | 必须 |
| 8 | 用户 ASK 后注入新事实，下轮 prompt.context_summary 含此事实 | 必须 |
| 9 | 专家数 < min_experts_to_continue → 强制 enter_final | 必须 |
| 10 | v5 Jury().think() 走适配器 → JuryResult 字段集完全一致 | 必须 |
| 11 | LLM 5xx 模拟（用 FakeProvider 抛错）→ Orchestrator 进入 aborted | 必须 |
| 12 | Recorder.on_statement 顺序 = expert_id 字典序 | 必须 |
| 13 | DebateConfig 权重和 ≠ 1.0 → ConfigError 抛出 | 必须 |
| 14 | DebateConfig.max_rounds < 1 → ConfigError 抛出 | 必须 |
| 15 | status 转移非法（如 CONVERGED → RUNNING）→ InvalidStateTransition | 必须 |

---

## 6. 性能与成本（不强制，但应可观测）

| 指标 | 来源 | 用途 |
|------|------|------|
| 单 session 平均轮数 | session.stats["rounds"] | 调优 max_rounds 默认 |
| 单 session LLM 调用数 | session.stats["llm_calls"] | 成本预算 |
| 外部咨询次数 | session.external_consultations | 调优默认上限 |
| Recorder 事件总数 | recorder.events | 调试 IO |
| 单轮耗时 | session.rounds[i].ended_at - started_at | 性能回归 |

---

## 7. 测试覆盖率目标

| 模块 | 目标 | 测试文件 |
|------|------|----------|
| `v6.types` | 100% 行覆盖 | test_types.py |
| `v6.moderator.argument_extractor` | 100% 行覆盖 | test_argument_extractor.py |
| `v6.convergence.detector` | 100% 分支覆盖 | test_convergence.py |
| `v6.expert.v5_adapter` | 100% 行覆盖 | test_expert_v5_adapter.py |
| `v6.pool.expert_pool` | 95% 行覆盖 | test_expert_pool.py |
| `v6.methods.registry` | 95% 行覆盖 | test_methodology_registry.py |
| `v6.recorder` | 90% 行覆盖 | test_recorder.py |
| `v6.moderator.moderator` | 90% 分支覆盖 | test_moderator.py |
| `v6.orchestrator` | 90% 分支覆盖 | test_orchestrator.py |
| `v6.compat.jury_adapter` | 100% 字段对齐 | test_compat_jury_adapter.py |
| E2E 完整辩论 | 4 个剧本 | e2e/test_*.py |

> 100% 覆盖率是建议；分支覆盖更关键（决策点不能漏）。

---

## 8. CI 集成建议

```yaml
# .github/workflows/test.yml 片段
- name: v5 兼容（不能破坏）
  run: pytest tests/test_core.py -q

- name: v6 单元
  run: pytest tests/test_v6/test_*.py -q --cov=super_thinking.v6 --cov-fail-under=85

- name: v6 E2E
  run: pytest tests/test_v6/e2e/ -q

- name: v5 vs 适配 v6 等价性
  run: pytest tests/test_v6/test_compat_jury_adapter.py -v
```

---

## 9. QA 手工剧本（黑盒）

1. **3 轮收敛剧本**（`scripts_converge_3rounds.json`）
   - 输入：金融/伦理/哲学混合问题
   - 期望：3 轮内 status=CONVERGED
   - 验收：会议结论 + 专家最终观点 + 外部咨询（若有）输出完整

2. **5 轮兜底剧本**（`scripts_diverge_5rounds.json`）
   - 输入：高度争议性问题
   - 期望：5 轮后 status=MAX_ROUNDS
   - 验收：标 "未收敛，强制进入终态" 日志；会议结论标 "分歧未解决"

3. **用户介入剧本**（`scripts_user_intervention.json`）
   - 输入：第 2 轮后分歧深，主持人 ask_user
   - 期望：用户回答 "X" → 下一轮主持人把 X 注入 context_summary
   - 验收：Recorder 含 on_user_question 事件；下一轮 prompt 包含 X

4. **外部咨询剧本**（`scripts_external_consultation.json`）
   - 输入：当前专家组合缺 "博弈论" 视角
   - 期望：主持人发起外部咨询；结果注入下一轮
   - 验收：Recorder.on_external_consultation 触发；下次 speak prompt 含方法论注入

5. **v5 兼容剧本**（`scripts_v5_compat.json`）
   - 输入：v5 examples 里的 feedback_example.md 问题
   - 期望：旧调用走适配器；输出与原 v5 examples 文档描述一致
   - 验收：JuryResult.outputs key/value 与 v5 同形

---

_楚灵 · 可测试性规范 Phase 1 · 2026-06-05_
