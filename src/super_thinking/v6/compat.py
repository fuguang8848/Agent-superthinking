"""
v6 v5 兼容层

提供 v5 到 v6 的适配器，确保 v5 Jury().think() 行为不变。
通过 SUPER_THINKING_LEGACY=1 环境变量控制。
"""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Any

from .types import (
    DebateConfig,
    DebateMode,
    ExpertStatement,
    ExpertPool,
    ExternalConsultationRequest,
    ExternalConsultation,
    FinalConsensus,
    LLMProvider,
    MethodologyRegistry,
    ModeratorDecision,
    Round,
    RoundNumber,
    SessionId,
    SessionRecorder,
    SessionStatus,
    SpeakPrompt,
    SpeakRole,
)

if TYPE_CHECKING:
    from .moderator import Moderator
    from .user_interaction import UserInteraction

logger = logging.getLogger(__name__)


# =============================================================================
# v5 类型别名（保持兼容）
# =============================================================================

class V5JuryResult:
    """
    v5 JuryResult 兼容类。
    
    100% 保留 v5 字段集：
    - outputs: v5 PerspectiveOutput 列表
    - errors: 错误列表
    - routing_result: 路由结果
    - total_perspectives: 总专家数
    - successful: 成功数量
    - failed: 失败数量
    
    通过 SUPER_THINKING_LEGACY=1 环境变量控制。
    """
    
    def __init__(
        self,
        outputs: list,
        errors: list,
        routing_result: Any,
        total_perspectives: int,
        successful: int,
        failed: int,
        session_id: str | None = None,
    ):
        self.outputs = outputs
        self.errors = errors
        self.routing_result = routing_result
        self.total_perspectives = total_perspectives
        self.successful = successful
        self.failed = failed
        self._session_id = session_id
    
    def get_outputs(self) -> list:
        """获取输出列表"""
        return self.outputs
    
    def has_errors(self) -> bool:
        """是否有错误"""
        return len(self.errors) > 0
    
    def get_perspective_ids(self) -> list[str]:
        """获取视角 ID 列表"""
        return [getattr(o, 'id', str(i)) for i, o in enumerate(self.outputs)]
    
    def __repr__(self) -> str:
        return (
            f"V5JuryResult("
            f"total={self.total_perspectives}, "
            f"successful={self.successful}, "
            f"failed={self.failed})"
        )


# =============================================================================
# JuryAdapter — v5 Jury 到 v6 的适配器
# =============================================================================

class JuryAdapter:
    """
    v5 Jury 适配器。
    
    在 v5 Jury 内部使用：think() 实际委托给 v6 单轮退化模式。
    
    行为：
    - 始终使用单轮非辩论模式（DebateMode.NON_DEBATE）
    - 只选择 1 个专家
    - 不触发收敛判断
    - 返回兼容的 V5JuryResult
    """
    
    def __init__(
        self,
        *,
        llm: LLMProvider,
        expert_pool: ExpertPool,
        methodology_registry: MethodologyRegistry,
        recorder: SessionRecorder,
        interaction: UserInteraction,
    ):
        self.llm = llm
        self.expert_pool = expert_pool
        self.methodology_registry = methodology_registry
        self.recorder = recorder
        self.interaction = interaction
        
        # 创建 v6 配置
        self._config = DebateConfig(
            mode=DebateMode.NON_DEBATE,
            max_rounds=1,
            min_initial_experts=1,
            max_initial_experts=1,
        )
    
    def think(
        self,
        input_text: str,
        context: dict | None,
        mode: str,
        selective_ids: list[str] | None,
    ) -> V5JuryResult:
        """
        v5 think() 方法的替代实现。
        
        内部委托给 v6 单轮模式。
        """
        # 导入 v6 组件
        from .orchestrator import DebateOrchestrator
        from .moderator import ModeratorImpl
        
        # 创建主持人
        moderator = ModeratorImpl(
            llm=self.llm,
            config=self._config,
            expert_pool=self.expert_pool,
            methodology_registry=self.methodology_registry,
            recorder=self.recorder,
        )
        
        # 创建协调器
        orchestrator = DebateOrchestrator(
            config=self._config,
            llm=self.llm,
            expert_pool=self.expert_pool,
            methodology_registry=self.methodology_registry,
            moderator=moderator,
            recorder=self.recorder,
            interaction=self.interaction,
        )
        
        # 运行辩论
        session = orchestrator.run(input_text, context)
        
        # 转换为 v5 格式
        return self._to_v5_result(session)
    
    def _to_v5_result(self, session) -> V5JuryResult:
        """将 v6 session 转换为 v5 JuryResult"""
        outputs = []
        errors = []
        
        if session.rounds:
            for stmt in session.rounds[0].statements:
                # 转换为 v5 格式（简化）
                output = self._convert_statement_to_v5(stmt)
                if output:
                    outputs.append(output)
                else:
                    errors.append(f"Failed to convert statement from {stmt.expert_id}")
        
        return V5JuryResult(
            outputs=outputs,
            errors=errors,
            routing_result=None,
            total_perspectives=len(session.active_experts),
            successful=len(outputs),
            failed=len(errors),
            session_id=session.session_id,
        )
    
    def _convert_statement_to_v5(self, stmt: ExpertStatement) -> Any | None:
        """将 v6 ExpertStatement 转换为 v5 输出"""
        # 创建一个兼容对象
        class V5CompatibleOutput:
            def __init__(self, stmt: ExpertStatement):
                self.id = str(stmt.expert_id)
                self.name = stmt.expert_name
                self.content = stmt.content
                self.confidence = stmt.confidence
                self.role = str(stmt.role)
                self.warnings = stmt.warnings
            
            def __repr__(self) -> str:
                return f"V5Output({self.id}: {self.name})"
        
        return V5CompatibleOutput(stmt)


# =============================================================================
# v5 包装器
# =============================================================================

def create_jury_adapter(
    llm: LLMProvider,
    expert_pool: ExpertPool,
    methodology_registry: MethodologyRegistry,
    recorder: SessionRecorder,
    interaction: UserInteraction,
) -> JuryAdapter:
    """
    创建 v5 Jury 适配器。
    
    便捷函数。
    """
    return JuryAdapter(
        llm=llm,
        expert_pool=expert_pool,
        methodology_registry=methodology_registry,
        recorder=recorder,
        interaction=interaction,
    )


def is_legacy_mode() -> bool:
    """检查是否启用 v5 兼容模式"""
    return os.environ.get("SUPER_THINKING_LEGACY", "0") == "1"


def enable_legacy_mode() -> None:
    """启用 v5 兼容模式"""
    os.environ["SUPER_THINKING_LEGACY"] = "1"


def disable_legacy_mode() -> None:
    """禁用 v5 兼容模式"""
    os.environ["SUPER_THINKING_LEGACY"] = "0"


# =============================================================================
# v5 兼容函数
# =============================================================================

def wrap_v5_perspective_output(output: Any) -> ExpertStatement:
    """
    将 v5 PerspectiveOutput 包装为 v6 ExpertStatement。
    
    用于 v5 到 v6 的数据迁移。
    """
    from .types import ExpertId
    
    # 尝试提取字段
    expert_id = getattr(output, 'id', 'unknown')
    expert_name = getattr(output, 'name', 'Unknown Expert')
    content = getattr(output, 'content', str(output))
    
    return ExpertStatement(
        expert_id=ExpertId(expert_id),
        expert_name=expert_name,
        role=SpeakRole.INITIAL,
        content=content,
        confidence=getattr(output, 'confidence', 0.5),
        raw=output,
    )


# =============================================================================
# v5 兼容
# =============================================================================

__all__ = [
    "V5JuryResult",
    "JuryAdapter",
    "create_jury_adapter",
    "is_legacy_mode",
    "enable_legacy_mode",
    "disable_legacy_mode",
    "wrap_v5_perspective_output",
]
