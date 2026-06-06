"""
Moderator - 主持人模块

实现 §2.7 方法论工具池、§2.3 主持人双重角色、§4.1 待定问题接口。
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Protocol, runtime_checkable, TYPE_CHECKING
import logging

from ..types import (
    DebateConfig, Expert, ExpertPool, ExpertStatement, ArgumentMenu,
    ModeratorDecision, ModeratorAction, ConvergenceSignal, DebateSession,
    RoundNumber, SessionStatus, UserQuestion, QuestionId, FinalConsensus,
    ExternalConsultationRequest, ExpertId, RosterChangeRequest,
    MethodologyResult, SpeakPrompt,
)
from ..methodology import MethodologyRegistry
from ..session_recorder import SessionRecorder
from ..external_consultation import ExternalConsultationManager
from .argument_extractor import ArgumentExtractor
from .menu_builder import MenuBuilder

if TYPE_CHECKING:
    from ..llm.provider import LLMProvider

logger = logging.getLogger(__name__)


# =============================================================================
# ModeratorConfig & Protocol
# =============================================================================

@dataclass(frozen=True, kw_only=True)
class ModeratorConfig:
    system_prompt_template: str = ""
    decision_prompt_template: str = ""
    use_llm_for_extraction: bool = True
    use_llm_for_decision: bool = True


@runtime_checkable
class Moderator(Protocol):
    def select_initial_panel(self, question: str, context: dict) -> tuple[Expert, ...]: ...
    def execute_round(self, session: DebateSession, round_number: RoundNumber, role: Any) -> tuple: ...
    def build_menu(self, session: DebateSession, statements: tuple[ExpertStatement, ...]) -> ArgumentMenu: ...
    def decide(self, session: DebateSession, last_signal: ConvergenceSignal | None) -> ModeratorDecision: ...
    def format_final_consensus(self, session: DebateSession) -> FinalConsensus: ...
    def ask_user(self, session: DebateSession, reason: str) -> UserQuestion: ...


# =============================================================================
# DefaultModerator
# =============================================================================

class DefaultModerator:
    """
    主持人实现。

    §2.7 方法论工具池相关职责：
    - 注入方法论提示（methodology_hints）到专家 prompt
    - 收集上一轮方法论反馈（methodology_feedback）到本轮 prompt
    - 检测方法论乱用（_validate_methodology_usage），将警告注入 statements

    §2.3 主持人双重角色：
    - 对内：组织辩论、整理论点、判断收敛
    - 对外：通过 ExternalConsultationManager 私下咨询专家，完善综合判断
    """

    def __init__(
        self,
        *,
        llm,
        config: DebateConfig,
        expert_pool: ExpertPool,
        methodology_registry: MethodologyRegistry,
        recorder: SessionRecorder,
        moderator_config: ModeratorConfig | None = None,
        consultation_manager: ExternalConsultationManager | None = None,
    ):
        self._llm = llm
        self._config = config
        self._expert_pool = expert_pool
        self._methodology = methodology_registry
        self._recorder = recorder
        self._mod_config = moderator_config or ModeratorConfig()
        self._extractor = ArgumentExtractor()
        self._menu_builder = MenuBuilder()
        self._consultation_manager = consultation_manager

    # -------------------------------------------------------------------------
    # 专家面板选择
    # -------------------------------------------------------------------------

    def select_initial_panel(self, question: str, context: dict) -> tuple[Expert, ...]:
        suggested = self._expert_pool.suggest_for(
            question, top_k=self._config.max_initial_experts
        )
        min_exp = self._config.min_initial_experts
        max_exp = self._config.max_initial_experts
        if len(suggested) < min_exp:
            all_exp = self._expert_pool.list_registered()
            remaining = [e for e in all_exp if e not in suggested]
            suggested = suggested + tuple(remaining[:min_exp - len(suggested)])
        return tuple(suggested[:max_exp])

    # -------------------------------------------------------------------------
    # 论点菜单构建
    # -------------------------------------------------------------------------

    def build_menu(
        self, session: DebateSession, statements: tuple[ExpertStatement, ...]
    ) -> ArgumentMenu:
        all_suggested = []
        for stmt in statements:
            all_suggested.extend(self._extractor.extract(stmt))

        prev_menu = session.rounds[-1].menu if session.rounds else None
        menu = self._menu_builder.build(
            RoundNumber(len(session.rounds) + 1),
            tuple(all_suggested),
            prev_menu,
        )
        self._recorder.on_menu_built(menu)
        return menu

    # -------------------------------------------------------------------------
    # 决策
    # -------------------------------------------------------------------------

    def decide(
        self, session: DebateSession, last_signal: ConvergenceSignal | None
    ) -> ModeratorDecision:
        current_round = len(session.rounds)

        if current_round >= self._config.max_rounds:
            return ModeratorDecision(
                action=ModeratorAction.ENTER_FINAL, reason="Max rounds reached"
            )

        if last_signal and last_signal.converged:
            return ModeratorDecision(
                action=ModeratorAction.CONVERGE, reason="Convergence detected"
            )

        if len(session.active_experts) < self._config.min_experts_to_continue:
            return ModeratorDecision(
                action=ModeratorAction.ENTER_FINAL,
                reason="Too few active experts",
            )

        return ModeratorDecision(action=ModeratorAction.CONTINUE, reason="Continue debate")

    # -------------------------------------------------------------------------
    # 方法论乱用检测（§4.1 第3条：主持人怎么判断"用错了"）
    # -------------------------------------------------------------------------

    def _validate_methodology_usage(
        self, statements: tuple[ExpertStatement, ...]
    ) -> tuple[ExpertStatement, ...]:
        """
        检查每位专家的方法论调用是否适用于其论点。

        §4.1 第3条实现：主持人有权提示"这个方法论不适用于当前的论点"。

        基于关键词匹配（MethodologyRegistry.validate_methodology_usage）：
        - 如果 claim 中不包含该方法论关键词，返回警告
        - 警告注入到 statement.warnings 中，供后续 prompt 使用

        Args:
            statements: 本轮所有专家发言

        Returns:
            更新了 warnings 字段的 statements tuple
        """
        validated = []
        for stmt in statements:
            if stmt.methodology_call is None:
                validated.append(stmt)
                continue

            method_id = stmt.methodology_call.method_id
            claim = stmt.content  # 用发言全文作为 claim

            is_valid, reason = self._methodology.validate_methodology_usage(
                method_id, claim
            )

            if is_valid:
                validated.append(stmt)
            else:
                # 方法论乱用，注入警告
                warnings = stmt.warnings + (
                    f"[方法论警告] 你使用的 {method_id} 在当前论点中缺乏适用依据：{reason}",
                )
                stmt = replace(stmt, warnings=warnings)
                validated.append(stmt)
                logger.info(
                    f"Methodology misuse detected: expert={stmt.expert_id} "
                    f"method={method_id} reason={reason}"
                )

        return tuple(validated)

    # -------------------------------------------------------------------------
    # 从上一轮收集方法论反馈（§4.1 第4条：方法论输出怎么反馈给专家）
    # -------------------------------------------------------------------------

    def _collect_methodology_feedback(
        self, session: DebateSession
    ) -> tuple[MethodologyResult, ...]:
        """
        收集上一轮所有方法论结果，组成反馈列表注入本轮 prompt。

        §4.1 第4条实现：方法论输出反馈给专家 → 注入 SpeakPrompt.methodology_feedback。

        反馈包括：
        - verdict（confirmed/questionable/rejected）
        - findings（发现的问题）
        - reframed_claim（重新表述）
        - confidence_impact（置信度影响）
        """
        if not session.rounds:
            return ()

        last_round = session.rounds[-1]
        feedback: list[MethodologyResult] = []

        for stmt in last_round.statements:
            if stmt.methodology_result is not None:
                feedback.append(stmt.methodology_result)

        return tuple(feedback)

    # -------------------------------------------------------------------------
    # 生成方法论提示（§4.1 第2条：系统怎么注入方法论视角）
    # -------------------------------------------------------------------------

    def _build_methodology_hints(self, session: DebateSession) -> tuple[str, ...]:
        """
        根据当前辩论态势，推荐适用的方法论，生成提示文本。

        §4.1 第2条实现：系统注入方法论视角 → 在 prompt 中提示可用方法论。
        """
        if not session.question:
            return ()

        # 用问题查询推荐方法论
        suggested = self._methodology.suggest_for(session.question, top_k=3)
        if not suggested:
            return ()

        hints = [
            f"【方法论提示】当前议题可能适合使用: {', '.join(p.display_name for p in suggested)}"
        ]
        return tuple(hints)

    # -------------------------------------------------------------------------
    # 生成方法论工具池文本块
    # -------------------------------------------------------------------------

    def _get_methodology_pool_block(self) -> str:
        """获取完整方法论工具池描述，注入到首次 prompt。"""
        return self._methodology.get_methodology_prompt_block()

    # -------------------------------------------------------------------------
    # 执行单轮辩论
    # -------------------------------------------------------------------------

    def execute_round(
        self,
        session: DebateSession,
        round_number: RoundNumber,
        role: Any,
    ) -> tuple:
        """
        执行一轮辩论。

        §2.7 方法论工具池流程：
        1. 收集上一轮方法论反馈 → 注入本轮 prompt.methodology_feedback
        2. 注入方法论提示（methodology_hints）
        3. 方法论乱用检测（_validate_methodology_usage）→ 注入 warnings

        Returns:
            tuple: (Round object, success: bool)
        """
        import time as time_module

        started_at = time_module.time()

        prev_menu = session.rounds[-1].menu if session.rounds else None
        is_initial = role.value == "initial" if hasattr(role, 'value') else False

        # §4.1 第2条：系统注入方法论视角
        methodology_hints = self._build_methodology_hints(session)

        # §4.1 第4条：收集上一轮方法论输出 → 反馈给专家
        methodology_feedback = self._collect_methodology_feedback(session)

        # 获取方法论工具池文本块（仅首次）
        methodology_pool_block = self._get_methodology_pool_block() if is_initial else ""

        statements: list = []

        for expert in session.active_experts:
            # 构建 prompt
            prompt = SpeakPrompt(
                session_id=session.session_id,
                round_number=round_number,
                role=role,
                question=session.question,
                argument_menu=prev_menu,
                methodology_hints=methodology_hints,
                methodology_feedback=methodology_feedback,
            )

            # 如果有方法论工具池文本块，附加到 extra
            if methodology_pool_block:
                prompt = replace(
                    prompt,
                    extra={**prompt.extra, "methodology_pool_block": methodology_pool_block},
                )

            try:
                stmt = expert.speak(prompt)
                statements.append(stmt)
            except Exception as e:
                logger.error(f"Expert {getattr(expert, 'id', '?')} failed to speak: {e}")

        statements = tuple(statements)

        # §4.1 第3条：检测方法论是否被乱用
        statements = self._validate_methodology_usage(statements)

        # 构建论点菜单
        menu = self.build_menu(session, statements)

        # 计算收敛信号
        from ..convergence import DefaultConvergenceDetector

        detector = DefaultConvergenceDetector(self._config.convergence)
        signal = detector.detect(
            round_number=round_number,
            current_menu=menu,
            previous_menu=prev_menu,
            statements=statements,
        )

        ended_at = time_module.time()

        round_obj = Round(
            round_number=round_number,
            menu=menu,
            statements=statements,
            convergence_signal=signal,
            moderator_decision=None,
            started_at=started_at,
            ended_at=ended_at,
        )

        return round_obj, True

    # -------------------------------------------------------------------------
    # 最终结论合成（§2.10 三层信息源）
    # -------------------------------------------------------------------------

    def format_final_consensus(self, session: DebateSession) -> FinalConsensus:
        all_args = [arg for r in session.rounds for arg in r.menu.items]
        consensus = [a.claim for a in all_args if a.confidence >= 0.7]
        divergence = [a.claim for a in all_args if a.confidence < 0.5]
        suggestions = []

        if consensus:
            suggestions.append("共识已达成")
        if divergence:
            suggestions.append("仍存在分歧")

        return FinalConsensus(
            consensus_points=tuple(set(consensus)),
            divergence_points=tuple(set(divergence)),
            root_contradictions=tuple(
                a.claim for a in all_args if a.status.value == "active"
            ),
            suggestions=tuple(suggestions),
            final_stmts=session.final_stmts,
        )

    # -------------------------------------------------------------------------
    # 询问用户
    # -------------------------------------------------------------------------

    def ask_user(self, session: DebateSession, reason: str) -> UserQuestion:
        return UserQuestion(
            question_id=QuestionId(f"Q-{session.session_id}-{len(session.rounds)}"),
            text=reason,
            options=("继续", "结束", "补充信息"),
            triggered_by="moderator_init",
            context={
                "session_id": session.session_id,
                "round": len(session.rounds),
            },
        )


# =============================================================================
# Exports
# =============================================================================

Moderator = DefaultModerator
ModeratorImpl = DefaultModerator


def create_moderator(*, llm, config, expert_pool, methodology_registry, recorder,
                       consultation_manager: ExternalConsultationManager | None = None):
    return DefaultModerator(
        llm=llm,
        config=config,
        expert_pool=expert_pool,
        methodology_registry=methodology_registry,
        recorder=recorder,
        consultation_manager=consultation_manager,
    )
