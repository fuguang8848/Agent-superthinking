"""
v6 主持人模块

核心辩论编排逻辑：选专家 → 拉取菜单 → 并行发言 → 提取菜单 → 收敛判断 → 决策。
"""

from __future__ import annotations

import logging
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import TYPE_CHECKING, Protocol, runtime_checkable, Any

from .types import (
    DebateConfig,
    DebateMode,
    DebateSession,
    Expert,
    ExpertId,
    ExpertPool,
    ExpertStatement,
    ExternalConsultation,
    ExternalConsultationRequest,
    MethodId,
    MethodologyRegistry,
    ModeratorAction,
    ModeratorDecision,
    Round,
    RoundNumber,
    SessionId,
    SessionStatus,
    SpeakPrompt,
    SpeakRole,
    UserQuestion,
    QuestionId,
)

if TYPE_CHECKING:
    from .llm.provider import LLMProvider
    from .session_recorder import SessionRecorder
    from .user_interaction import UserInteraction

logger = logging.getLogger(__name__)


# =============================================================================
# Moderator 协议
# =============================================================================

@runtime_checkable
class Moderator(Protocol):
    """主持人协议"""
    
    def select_initial_panel(self, question: str, context: dict) -> tuple[Expert, ...]:
        """选择初始专家面板"""
        ...
    
    def build_menu(
        self,
        session: DebateSession,
        statements: tuple[ExpertStatement, ...],
    ) -> Any:
        """从发言构建论点菜单"""
        ...
    
    def decide(
        self,
        session: DebateSession,
        last_signal: Any | None,
    ) -> ModeratorDecision:
        """基于当前态势做决策"""
        ...
    
    def format_final_consensus(self, session: DebateSession) -> Any:
        """生成会议结论"""
        ...
    
    def ask_user(self, session: DebateSession, reason: str) -> UserQuestion:
        """询问用户"""
        ...


# =============================================================================
# ModeratorImpl — 主持人实现
# =============================================================================

class ModeratorImpl:
    """
    主持人实现类。
    
    核心流程：
    1. select_initial_panel: 选择初始专家
    2. execute_round: 执行一轮辩论
       - gather_statements: 并行获取专家发言
       - build_menu: 构建论点菜单
       - detect_convergence: 检测收敛
    3. decide: 决定下一步行动
    4. format_final_consensus: 生成最终结论
    """
    
    def __init__(
        self,
        *,
        llm: LLMProvider,
        config: DebateConfig,
        expert_pool: ExpertPool,
        methodology_registry: MethodologyRegistry,
        recorder: SessionRecorder,
    ):
        self.llm = llm
        self.config = config
        self.expert_pool = expert_pool
        self.methodology_registry = methodology_registry
        self.recorder = recorder
        
        # 导入避免循环依赖
        from .argument_menu import StructuredExtractor
        from .convergence import DefaultConvergenceDetector
        
        self.extractor = StructuredExtractor(use_llm=False)
        self.convergence_detector = DefaultConvergenceDetector(config.convergence)
    
    def select_initial_panel(self, question: str, context: dict) -> tuple[Expert, ...]:
        """选择初始专家面板"""
        # 使用 expert_pool 的建议功能
        suggested = self.expert_pool.suggest_for(question, top_k=self.config.max_initial_experts)
        
        # 确保不少于最小专家数
        if len(suggested) < self.config.min_initial_experts:
            # 填充到最小数量（取前几个）
            all_experts = self.expert_pool.list_registered()
            for exp in all_experts:
                if exp not in suggested and len(suggested) < self.config.min_initial_experts:
                    suggested = list(suggested) + [exp]
        
        # 限制到最大数量
        return tuple(suggested[:self.config.max_initial_experts])
    
    def execute_round(
        self,
        session: DebateSession,
        round_number: RoundNumber,
        role: SpeakRole = SpeakRole.INITIAL,
    ) -> tuple[Round, bool]:
        """
        执行一轮辩论。
        
        Args:
            session: 当前会话
            round_number: 轮次编号
            role: 发言角色
        
        Returns:
            (本轮 Round, 是否成功)
        """
        started_at = time.time()
        
        # 1. 构建发言提示
        prompt = self._build_speak_prompt(session, round_number, role)
        
        # 2. 并行获取专家发言
        statements, errors = self._gather_statements(session, prompt, round_number, role)
        
        # 3. 构建论点菜单
        prev_menu = session.rounds[-1].menu if session.rounds else None
        menu, _ = self.extractor.build_argument_menu(
            expert_id=ExpertId("system"),
            expert_name="System",
            round_number=round_number,
            statements=statements,
            prev_menu=prev_menu,
        )
        
        # 4. 检测收敛
        signal = self.convergence_detector.observe(session)
        
        # 5. 记录事件
        ended_at = time.time()
        
        round_obj = Round(
            round_number=round_number,
            menu=menu,
            statements=statements,
            convergence_signal=signal,
            moderator_decision=None,
            started_at=started_at,
            ended_at=ended_at,
        )
        
        return round_obj, len(errors) == 0
    
    def _build_speak_prompt(
        self,
        session: DebateSession,
        round_number: RoundNumber,
        role: SpeakRole,
    ) -> SpeakPrompt:
        """构建发言提示"""
        # 获取上一轮菜单
        prev_menu = session.rounds[-1].menu if session.rounds else None
        
        # 获取针对论点
        targeted_args = []
        if prev_menu and role in (SpeakRole.REBUTTAL, SpeakRole.FREE_ADDENDUM):
            for arg in prev_menu.active():
                targeted_args.append(type(arg).argument_id)
        
        # 生成上下文摘要
        context_summary = self._generate_context_summary(session)
        
        return SpeakPrompt(
            session_id=session.session_id,
            round_number=round_number,
            role=role,
            question=session.question,
            argument_menu=prev_menu,
            context_summary=context_summary,
            targeted_arguments=tuple(targeted_args),
            free_addendum_max_chars=self.config.convergence.free_addendums if hasattr(self.config.convergence, 'free_addendums') else 600,
            constraints=(
                ("必须至少针对一个论点",) if self.config.require_targeted_argument and role == SpeakRole.REBUTTAL else ()
            ),
        )
    
    def _generate_context_summary(self, session: DebateSession) -> str:
        """生成上下文摘要"""
        if not session.rounds:
            return "这是第一轮辩论，请各位专家独立陈述观点。"
        
        # 简单摘要：统计上一轮发言数量
        last_round = session.rounds[-1]
        summary = f"第 {last_round.round_number} 轮结束，共 {len(last_round.statements)} 位专家发言。"
        
        if last_round.convergence_signal:
            summary += f"收敛得分: {last_round.convergence_signal.score:.2f}。"
        
        return summary
    
    def _gather_statements(
        self,
        session: DebateSession,
        prompt: SpeakPrompt,
        round_number: RoundNumber,
        role: SpeakRole,
    ) -> tuple[tuple[ExpertStatement, ...], list[dict]]:
        """
        并行获取专家发言。
        
        异常隔离：单个专家崩溃不影响整轮。
        """
        statements: list[ExpertStatement] = []
        errors: list[dict] = []
        
        # 准备发言任务
        tasks = []
        for expert in session.active_experts:
            expert_prompt = SpeakPrompt(
                session_id=prompt.session_id,
                round_number=round_number,
                role=role,
                question=prompt.question,
                argument_menu=prompt.argument_menu,
                context_summary=prompt.context_summary,
                targeted_arguments=prompt.targeted_arguments,
                free_addendum_max_chars=prompt.free_addendum_max_chars,
                methodology_hints=prompt.methodology_hints,
                constraints=prompt.constraints,
            )
            tasks.append((expert, expert_prompt))
        
        # 并行执行（使用线程池）
        with ThreadPoolExecutor(max_workers=len(tas
