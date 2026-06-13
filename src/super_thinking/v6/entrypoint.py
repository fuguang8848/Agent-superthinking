"""
v6 Entrypoint Module

顶层公共 API：think_v6() / convene_v6()

单轮快速思考（think_v6）和多轮正式辩论（convene_v6）的统一入口。
"""

from __future__ import annotations

import dataclasses

import logging
import time as time_module
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from .types import (
    ConvergenceTuning,
    DebateConfig,
    DebateMode,
    DebateSession,
    Expert,
    LLMProvider,
    MethodologyRegistry,
    ModeratorDecision,
    ModeratorAction,
    Round,
    RoundNumber,
    SessionId,
    SessionStatus,
    SpeakRole,
    UserQuestion,
    QuestionId,
)
from .orchestrator import DebateOrchestrator
from .moderator.moderator import DefaultModerator, ModeratorConfig
from .methodology import DefaultMethodologyRegistry
from .session_recorder import InMemoryRecorder
from .user_interaction import SyncUserInteraction

if TYPE_CHECKING:
    from .moderator import Moderator
    from .llm.openai_compat import OpenAICompatProvider

logger = logging.getLogger(__name__)


# =============================================================================
# 专家池实现（entrypoint 内部用，不依赖 expert_pool.py）
# =============================================================================

class _ExpertPoolImpl:
    """
    轻量级专家池实现，用于 entrypoint。

    实现了 ExpertPool protocol 的核心方法。
    """

    def __init__(self):
        self._experts: dict = {}
        self._session_active: dict[str, set] = {}

    def register(self, expert) -> None:
        self._experts[expert.id] = expert

    def unregister(self, expert_id) -> None:
        if expert_id in self._experts:
            del self._experts[expert_id]

    def get(self, expert_id):
        return self._experts.get(expert_id)

    def list_registered(self):
        return tuple(self._experts.values())

    def list_active_in_session(self, session):
        active_ids = self._session_active.get(str(session.session_id), set())
        return tuple(self._experts[eid] for eid in active_ids if eid in self._experts)

    def suggest_for(self, question: str, *, top_k: int = 5):
        scored = []
        for expert in self._experts.values():
            score = sum(1 for kw in expert.trigger_keywords if kw.lower() in question.lower())
            scored.append((score, expert))
        scored.sort(key=lambda x: -x[0])
        return tuple(e for _, e in scored[:top_k])

    def apply_roster_change(self, session, change):
        session_id = str(session.session_id)
        if session_id not in self._session_active:
            self._session_active[session_id] = set()
        if change.action == "add":
            expert = self._experts.get(change.expert_id)
            if expert:
                self._session_active[session_id].add(change.expert_id)
                return True
        elif change.action == "remove":
            self._session_active[session_id].discard(change.expert_id)
            return True
        return False


# Alias for external use
ExpertPool = _ExpertPoolImpl


# =============================================================================
# 默认专家池
# =============================================================================

class _SimpleExpert:
    """
    一个极简专家实现，用于 think_v6 的默认专家池。

    当用户不提供专家时使用此实现。
    """

    def __init__(
        self,
        expert_id: str,
        name: str,
        domain: str,
        trigger_keywords: list[str],
        response_template: str,
    ):
        from .types import ExpertId
        self._id = ExpertId(expert_id)
        self._name = name
        self._domain = domain
        self._trigger_keywords = tuple(trigger_keywords)
        self._response_template = response_template

    @property
    def id(self):
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return f"{self._name} - {self._domain}专家"

    @property
    def domain(self) -> str:
        return self._domain

    @property
    def trigger_keywords(self) -> tuple[str, ...]:
        return self._trigger_keywords

    @property
    def is_methodology(self) -> bool:
        return False

    def speak(self, prompt):
        from .types import ExpertStatement
        content = self._response_template.format(
            question=prompt.question,
            domain=self._domain,
        )
        return ExpertStatement(
            expert_id=self._id,
            expert_name=self._name,
            role=prompt.role,
            content=content,
            confidence=0.6,
            elapsed_s=0.0,
        )


def _create_default_expert_pool() -> ExpertPool:
    """
    创建包含3个默认领域专家的专家池。

    涵盖：技术分析、风险评估、多角度综合。
    """
    pool = ExpertPool()

    # 技术分析师
    pool.register(_SimpleExpert(
        expert_id="tech-analyst",
        name="技术分析师",
        domain="技术分析",
        trigger_keywords=["技术", "实现", "架构", "方案", "代码", "系统"],
        response_template="【技术分析】关于「{question}」的技术可行性需要从系统设计角度评估。关键在于实现复杂度、扩展性和可维护性。当前主流方案倾向于模块化设计，分层架构能够有效降低耦合度。",
    ))

    # 风险评估师
    pool.register(_SimpleExpert(
        expert_id="risk-analyst",
        name="风险评估师",
        domain="风险分析",
        trigger_keywords=["风险", "问题", "隐患", "失败", "挑战", "障碍"],
        response_template="【风险评估】「{question}」的主要风险包括：实施风险（资源不足）、外部风险（环境变化）、技术风险（技术选型失误）。建议建立风险缓冲机制，定期评估。",
    ))

    # 综合分析师
    pool.register(_SimpleExpert(
        expert_id="synthesizer",
        name="综合分析师",
        domain="综合分析",
        trigger_keywords=["应该", "如何", "怎样", "最佳", "最好", "建议"],
        response_template="【综合分析】综合来看，「{question}」需要平衡多个维度。建议采取渐进式策略：短期聚焦核心问题，中期完善支撑体系，长期考虑生态建设。关键决策点在于初期技术路线选择。",
    ))

    return pool


# =============================================================================
# 内部轮次执行（用于 think_v6 单轮模式）
# =============================================================================

def _run_single_round_for(
    question: str,
    expert_pool: ExpertPool,
    llm: LLMProvider,
    recorder: InMemoryRecorder,
    max_rounds: int = 1,
) -> DebateSession:
    """
    执行单轮辩论（think_v6 内部实现）。

    创建 session，选择专家，执行一轮，生成结论。
    """
    session_id = SessionId(f"s-{int(time_module.time() * 1000)}")

    # 选择初始专家面板
    suggested = expert_pool.suggest_for(question, top_k=3)
    if not suggested:
        all_experts = expert_pool.list_registered()
        suggested = all_experts[:3] if all_experts else ()

    initial_panel = tuple(suggested[:3])

    # 构建初始会话
    config = DebateConfig(
        mode=DebateMode.NON_DEBATE,
        max_rounds=max_rounds,
        min_initial_experts=1,
        max_initial_experts=3,
        min_experts_to_continue=1,
    )

    from .types import DebateSession as DSD
    session = DSD(
        session_id=session_id,
        question=question,
        context={},
        config=config,
        expert_pool=expert_pool,
        initial_panel=initial_panel,
        active_experts=initial_panel,
        rounds=(),
        final_stmts=(),
        final_consensus=None,
        external_consultations=(),
        status=SessionStatus.INIT,
        stats={"start_time": time_module.time()},
        recorder=recorder,
    )

    recorder.on_session_start(session)

    # 执行一轮
    from .types import ArgumentMenu, ConvergenceSignal, SpeakPrompt
    from .convergence import ConvergenceCalculator

    statements: list = []
    for expert in initial_panel:
        prompt = SpeakPrompt(
            session_id=session_id,
            round_number=RoundNumber(1),
            role=SpeakRole.INITIAL,
            question=question,
        )
        try:
            stmt = expert.speak(prompt)
            statements.append(stmt)
        except Exception as e:
            logger.error(f"Expert {expert.id} error: {e}")

    statements = tuple(statements)

    # 记录发言
    for stmt in statements:
        recorder.on_statement(stmt)

    # 构建菜单
    menu = ArgumentMenu(
        round_number=RoundNumber(1),
        items=(),
        converged=(),
        focus=(),
    )

    recorder.on_menu_built(menu)

    # 收敛检测（直接使用 ConvergenceCalculator）
    from .convergence import ConvergenceCalculator
    calculator = ConvergenceCalculator(config.convergence)
    signal = calculator.compute_signal(
        current_menu=menu,
        prev_menu=None,
        statements=statements,
        round_number=RoundNumber(1),
    )

    if signal:
        recorder.on_convergence(signal)

    round_obj = Round(
        round_number=RoundNumber(1),
        menu=menu,
        statements=statements,
        convergence_signal=signal,
        moderator_decision=ModeratorDecision(
            action=ModeratorAction.CONVERGE,
            reason="think_v6 single round mode",
        ),
    )

    # 最终结论
    all_args = list(menu.items)
    consensus = [a.claim for a in all_args if a.confidence >= 0.65]
    divergence = [a.claim for a in all_args if a.confidence < 0.5]

    from .types import FinalConsensus as FC
    final_consensus = FC(
        consensus_points=tuple(set(consensus)),
        divergence_points=tuple(set(divergence)),
        root_contradictions=tuple(a.claim for a in all_args),
        suggestions=("Consider multi-round debate for deeper analysis.",),
        final_stmts=statements,
        raw_outputs=(),
    )

    session = dataclasses.replace(
        session,
        rounds=(round_obj,),
        final_stmts=statements,
        final_consensus=final_consensus,
        status=SessionStatus.COMPLETED,
    )

    recorder.on_session_end()

    return session


# =============================================================================
# think_v6 — 单轮快速思考
# =============================================================================

def think_v6(
    question: str,
    *,
    experts: list[Expert] | None = None,
    max_rounds: int = 5,
    convergence_threshold: float = 0.65,
    llm_provider=None,
) -> DebateSession:
    """
    单轮快速思考模式。

    内部创建默认 ExpertPool + Moderator，执行一轮辩论即返回。
    适用于快速评估和简单问题分析。

    Args:
        question: 用户问题
        experts: 可选，自定义专家列表（若不提供则使用内置默认专家）
        max_rounds: 最大轮次（仅在正式辩论模式下使用，think_v6 固定为1）
        convergence_threshold: 收敛阈值（0.0-1.0）
        llm_provider: 可选，LLM provider（当前版本中 think_v6 不依赖 LLM）

    Returns:
        DebateSession: 包含辩论结果的会话对象
    """
    # 创建专家池
    if experts:
        pool = ExpertPool()
        for exp in experts:
            pool.register(exp)
    else:
        pool = _create_default_expert_pool()

    # 创建记录器
    recorder = InMemoryRecorder()

    # 执行单轮
    session = _run_single_round_for(
        question=question,
        expert_pool=pool,
        llm=llm_provider,
        recorder=recorder,
        max_rounds=max_rounds,
    )

    return session


# =============================================================================
# convene_v6 — 正式圆桌辩论
# =============================================================================

def convene_v6(
    question: str,
    *,
    expert_pool: ExpertPool,
    methodology_registry: MethodologyRegistry | None = None,
    moderator: Moderator | None = None,
    recorder=None,
    max_rounds: int = 5,
    convergence_threshold: float = 0.65,
    llm_provider=None,
) -> DebateSession:
    """
    正式圆桌辩论模式。

    用户提供完整的 expert_pool，支持多轮辩论、收敛判断、动态专家池变更。

    Args:
        question: 用户问题
        expert_pool: 专家池（必须提供）
        methodology_registry: 可选，方法论注册表（默认使用 DefaultMethodologyRegistry）
        moderator: 可选，自定义主持人（默认使用 DefaultModerator）
        recorder: 可选，会话记录器（默认使用 InMemoryRecorder）
        max_rounds: 最大辩论轮次（默认5）
        convergence_threshold: 收敛阈值（默认0.65）
        llm_provider: LLM provider（必须提供）

    Returns:
        DebateSession: 包含完整辩论结果的会话对象
    """
    if llm_provider is None:
        raise ValueError("llm_provider is required for convene_v6")

    # 默认记录器
    if recorder is None:
        recorder = InMemoryRecorder()

    # 默认方法论注册表
    if methodology_registry is None:
        methodology_registry = DefaultMethodologyRegistry()

    # 构建 DebateConfig
    config = DebateConfig(
        mode=DebateMode.STANDARD,
        max_rounds=max_rounds,
        min_initial_experts=2,
        max_initial_experts=6,
        min_experts_to_continue=2,
        convergence=ConvergenceTuning(
            score_threshold=convergence_threshold,
            require_consecutive=1,
        ),
    )

    # 默认主持人
    if moderator is None:
        moderator = DefaultModerator(
            llm=llm_provider,
            config=config,
            expert_pool=expert_pool,
            methodology_registry=methodology_registry,
            recorder=recorder,
        )

    # 创建协调器
    orchestrator = DebateOrchestrator(
        config=config,
        llm=llm_provider,
        expert_pool=expert_pool,
        methodology_registry=methodology_registry,
        moderator=moderator,
        recorder=recorder,
        interaction=SyncUserInteraction(),
    )

    # 执行辩论
    session = orchestrator.run(question)

    return session


# =============================================================================
# __all__
# =============================================================================

__all__ = [
    "think_v6",
    "convene_v6",
    "DebateSession",
    "ExpertPool",
    "DefaultMethodologyRegistry",
    "InMemoryRecorder",
    "OpenAICompatProvider",
]
