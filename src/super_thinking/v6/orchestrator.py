"""
v6 顶层协调器模块

公共入口:DebateOrchestrator.run(question, config) -> Verdict
串联 Moderator + Recorder + UserInteraction + ExternalConsultation。
"""

from __future__ import annotations

import logging
import os
import time
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from .types import (
    DebateConfig,
    DebateMode,
    DebateSession,
    ExpertPool,
    ExpertStatement,
    ExternalConsultation,
    FinalConsensus,
    LLMProvider,
    MethodologyRegistry,
    ModeratorAction,
    ModeratorDecision,
    Round,
    RoundNumber,
    SessionId,
    SessionRecorder,
    SessionStatus,
    SpeakRole,
    UserInteraction,
    UserQuestion,
    UserResponse,
)

if TYPE_CHECKING:
    from .moderator import Moderator
    from .external_consultation import ExternalConsultationManager

logger = logging.getLogger(__name__)


# =============================================================================
# SessionOrchestrator 协议
# =============================================================================

@runtime_checkable
class SessionOrchestrator(Protocol):
    """会话协调器协议"""

    def run(self, session: DebateSession) -> DebateSession:
        """主循环:选专家 → 第一轮 → 辩论循环 → 终态"""
        ...

    def run_single_round(self, session: DebateSession) -> Round:
        """调试用:单轮执行"""
        ...

    def finalize(self, session: DebateSession) -> DebateSession:
        """终态收敛/总结"""
        ...


# =============================================================================
# DebateOrchestrator - 辩论协调器
# =============================================================================

class DebateOrchestrator:
    """
    顶层辩论协调器。

    提供公共 API:run(question, config) -> DebateSession

    内部流程:
    1. 初始化 session
    2. 选择初始专家面板
    3. 执行辩论循环
    4. 生成最终结论
    """

    def __init__(
        self,
        *,
        config: DebateConfig,
        llm: LLMProvider,
        expert_pool: ExpertPool,
        methodology_registry: MethodologyRegistry,
        moderator: Moderator,
        recorder: SessionRecorder,
        interaction: UserInteraction,
        consultation_manager: ExternalConsultationManager | None = None,
    ):
        self.config = config
        self.llm = llm
        self.expert_pool = expert_pool
        self.methodology_registry = methodology_registry
        self.moderator = moderator
        self.recorder = recorder
        self.interaction = interaction
        self.consultation_manager = consultation_manager

        # 检查是否启用 v5 兼容模式
        self._legacy_mode = os.environ.get("SUPER_THINKING_LEGACY", "0") == "1"

    def run(self, question: str, context: dict | None = None) -> DebateSession:
        """
        主入口:运行完整辩论。

        Args:
            question: 用户问题
            context: 额外上下文

        Returns:
            DebateSession: 包含完整辩论结果的会话
        """
        # 1. 初始化会话
        session = self._create_session(question, context or {})

        # v5 兼容模式
        if self._legacy_mode or self.config.mode == DebateMode.NON_DEBATE:
            return self._run_legacy_mode(session)

        # 记录开始
        self.recorder.on_session_start(session)

        try:
            # 2. 选择初始专家
            initial_panel = self.moderator.select_initial_panel(question, context or {})
            session = session.model_copy(update={
                "initial_panel": initial_panel,
                "active_experts": initial_panel,
                "status": SessionStatus.RUNNING,
            })

            # 3. 执行辩论循环
            session = self._run_debate_loop(session)

            # 4. 最终收敛
            session = self.finalize(session)

        except Exception as e:
            logger.error(f"Debate failed: {e}")
            session = session.model_copy(update={
                "status": SessionStatus.ABORTED,
                "stats": {**session.stats, "error": str(e)},
            })

        # 记录结束
        self.recorder.on_session_end(session)

        return session

    def _create_session(self, question: str, context: dict) -> DebateSession:
        """创建新会话"""
        return DebateSession(
            session_id=SessionId(f"s-{int(time.time() * 1000)}"),
            question=question,
            context=context,
            config=self.config,
            expert_pool=self.expert_pool,
            initial_panel=(),
            active_experts=(),
            rounds=(),
            final_stmts=(),
            final_consensus=None,
            external_consultations=(),
            status=SessionStatus.INIT,
            stats={"start_time": time.time()},
            recorder=self.recorder,
        )

    def _run_debate_loop(self, session: DebateSession) -> DebateSession:
        """执行辩论循环"""
        round_number = RoundNumber(1)
        role = SpeakRole.INITIAL

        while True:
            logger.info(f"Starting round {round_number}, role={role}")

            # 执行一轮
            round_obj, success = self.moderator.execute_round(session, round_number, role)

            # 记录轮次
            self.recorder.on_round_start(round_obj)
            for stmt in round_obj.statements:
                self.recorder.on_statement(stmt)
            self.recorder.on_menu_built(round_obj.menu)
            if round_obj.convergence_signal:
                self.recorder.on_convergence(round_obj.convergence_signal)

            # 更新会话
            session = session.model_copy(update={
                "rounds": session.rounds + (round_obj,),
            })

            # 决策
            decision = self.moderator.decide(session, round_obj.convergence_signal)
            round_obj = round_obj.model_copy(update={"moderator_decision": decision})

            self.recorder.on_decision(decision)

            # 根据决策执行
            if decision.action.value in ("converge", "enter_final"):
                break

            # 处理外部咨询（§2.4）：主持人判断需要补充视角时，私下咨询专家
            if decision.action == ModeratorAction.EXTERNAL_CONSULT:
                if self.consultation_manager is not None:
                    consult_req = decision.roster_change.external_consult
                    if consult_req is not None:
                        logger.info(
                            f"Performing external consultation with {consult_req.expert_id} "
                            f"(timeout={consult_req.deadline_s}s)"
                        )
                        # 外部咨询：同步阻塞，超时则自动降级
                        consultation_result = self.consultation_manager.consult(
                            expert_id=consult_req.expert_id,
                            question=consult_req.question,
                            context=consult_req.context_summary,
                            timeout_s=consult_req.deadline_s,
                            max_chars=consult_req.max_response_chars,
                        )
                        # 记录咨询结果
                        self.recorder.on_external_consultation(consultation_result)
                        # 存入 session，继续辩论循环（不打断当前轮次）
                        session = session.model_copy(update={
                            "external_consultations": (
                                session.external_consultations + (consultation_result,)
                            ),
                        })
                        logger.info(
                            f"External consultation complete: timed_out={consultation_result.timed_out}, "
                            f"response_len={len(consultation_result.response_text)}"
                        )
                        # 继续辩论循环，不切换轮次
                        continue

            if decision.action.value == "ask_user":
                # 询问用户
                user_q = self.moderator.ask_user(session, decision.question_to_user or "")
                response = self.interaction.ask(user_q)
                self.recorder.on_user_question(user_q, response)

                # 如果用户选择中止
                if response.answer.lower() in ("abort", "停止", "结束"):
                    break

            if decision.action.value == "abort":
                break

            # 继续下一轮
            round_number = RoundNumber(int(round_number) + 1)
            role = SpeakRole.REBUTTAL

        return session

    def _run_legacy_mode(self, session: DebateSession) -> DebateSession:
        """
        v5 兼容模式:单轮非辩论。

        等价于 v5 Jury().think()。
        """
        from .types import DebateSession, Round, ArgumentMenu, ConvergenceSignal, RoundNumber

        # 选择一个专家
        experts = self.expert_pool.list_registered()[:1]
        if not experts:
            return session.model_copy(update={"status": SessionStatus.ABORTED})

        expert = experts[0]

        # 执行一轮
        from .types import SpeakPrompt
        prompt = SpeakPrompt(
            session_id=session.session_id,
            round_number=RoundNumber(1),
            role=SpeakRole.INITIAL,
            question=session.question,
        )

        statements = (expert.speak(prompt),)

        # 构建简单菜单
        menu = ArgumentMenu(
            round_number=RoundNumber(1),
            items=(),
            converged=(),
            focus=(),
        )

        round_obj = Round(
            round_number=RoundNumber(1),
            menu=menu,
            statements=statements,
            convergence_signal=None,
            moderator_decision=None,
        )

        return session.model_copy(update={
            "initial_panel": (expert,),
            "active_experts": (expert,),
            "rounds": (round_obj,),
            "status": SessionStatus.COMPLETED,
        })

    def run_single_round(self, session: DebateSession) -> Round:
        """
        调试用:执行单轮辩论。

        Returns:
            Round: 执行后的 Round 对象
        """
        round_number = RoundNumber(len(session.rounds) + 1)
        role = SpeakRole.INITIAL
        round_obj, _ = self.moderator.execute_round(session, round_number, role)
        return round_obj

    def finalize(self, session: DebateSession) -> DebateSession:
        """
        终态收敛/总结。

        根据辩论结果生成最终共识,更新 session 状态。
        """
        consensus = self.moderator.format_final_consensus(session)
        final_stmts = tuple(
            stmt for r in session.rounds for stmt in r.statements
        )

        # 确定最终状态
        last_signal = session.rounds[-1].convergence_signal if session.rounds else None
        if last_signal and last_signal.converged:
            status = SessionStatus.CONVERGED
        elif len(session.rounds) >= self.config.max_rounds:
            status = SessionStatus.MAX_ROUNDS
        else:
            status = SessionStatus.COMPLETED

        return session.model_copy(update={
            "final_consensus": consensus,
            "final_stmts": final_stmts,
            "status": status,
        })


# =============================================================================
# 工厂函数
# =============================================================================

def create_orchestrator(
    *,
    config: DebateConfig,
    llm: LLMProvider,
    expert_pool: ExpertPool,
    methodology_registry: MethodologyRegistry,
    moderator: Moderator,
    recorder: SessionRecorder,
    interaction: UserInteraction,
    consultation_manager: ExternalConsultationManager | None = None,
) -> DebateOrchestrator:
    """
    工厂函数：创建 DebateOrchestrator 实例。

    推荐通过此函数创建协调器，而非直接实例化 DebateOrchestrator。
    """
    return DebateOrchestrator(
        config=config,
        llm=llm,
        expert_pool=expert_pool,
        methodology_registry=methodology_registry,
        moderator=moderator,
        recorder=recorder,
        interaction=interaction,
        consultation_manager=consultation_manager,
    )


def run_debate(
    question: str,
    *,
    config: DebateConfig,
    llm: LLMProvider,
    expert_pool: ExpertPool,
    methodology_registry: MethodologyRegistry,
    moderator: Moderator,
    recorder: SessionRecorder,
    interaction: UserInteraction,
    consultation_manager: ExternalConsultationManager | None = None,
    context: dict | None = None,
) -> DebateSession:
    """
    便捷函数：一步完成完整辩论。

    等价于 create_orchestrator(...).run(question)。
    """
    orchestrator = create_orchestrator(
        config=config,
        llm=llm,
        expert_pool=expert_pool,
        methodology_registry=methodology_registry,
        moderator=moderator,
        recorder=recorder,
        interaction=interaction,
        consultation_manager=consultation_manager,
    )
    return orchestrator.run(question, context=context)
