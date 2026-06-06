"""
v6 超思考辩论系统

核心模块：论点菜单、专家发言、收敛判断、主持人、协调器、v5兼容。
"""

from __future__ import annotations

# =============================================================================
# 基础类型（核心）
# =============================================================================
from .types import (
    # ID 类型
    SessionId,
    RoundNumber,
    ArgumentId,
    ExpertId,
    MethodId,
    QuestionId,
    # 枚举
    SessionStatus,
    SpeakRole,
    ArgumentStatus,
    ModeratorAction,
    DebateMode,
    # 配置
    ConvergenceTuning,
    DebateConfig,
    # 数据类
    ArgumentRef,
    Argument,
    SuggestedArgument,
    ArgumentMenu,
    SpeakPrompt,
    MethodologyCall,
    MethodologyResult,
    ExpertStatement,
    ConvergenceSignal,
    ExternalConsultationRequest,
    ExternalConsultation,
    RosterChange,
    RosterChangeRequest,
    ModeratorDecision,
    Round,
    FinalConsensus,
    DebateSession,
    # Protocol
)

# =============================================================================
# 论点菜单
# =============================================================================
from .argument_menu import (
    compute_overlap_ratio,
    merge_menus,
    StructuredExtractor,
    ExtractionResult,
)

# =============================================================================
# 专家发言
# =============================================================================
from .expert_statement import (
    StatementParser,
    ParseResult,
    parse_statement,
    ExpertStatementValidator,
    DefaultStatementValidator,
    DUAL_TRACK_SEPARATOR,
)

# =============================================================================
# 收敛判断
# =============================================================================
# Import from convergence package
from .convergence import (
    ConvergenceDetector,
    ConvergenceCalculator,
    DefaultConvergenceDetector,
)

# =============================================================================
# 主持人
# =============================================================================
from .moderator import (
    Moderator,
    ModeratorImpl,
)

# =============================================================================
# 协调器
# =============================================================================
from .orchestrator import (
    SessionOrchestrator,
    DebateOrchestrator,
    create_orchestrator,
    run_debate,
)

# =============================================================================
# v5 兼容
# =============================================================================
from .compat import (
    V5JuryResult,
    JuryAdapter,
    create_jury_adapter,
    is_legacy_mode,
    enable_legacy_mode,
    disable_legacy_mode,
    wrap_v5_perspective_output,
)

# =============================================================================
# 顶层入口
# =============================================================================
from .entrypoint import (
    think_v6,
    convene_v6,
)

# =============================================================================
# 公共 API
# =============================================================================
__all__ = [
    # 基础类型
    "SessionId",
    "RoundNumber",
    "ArgumentId",
    "ExpertId",
    "MethodId",
    "QuestionId",
    # 枚举
    "SessionStatus",
    "SpeakRole",
    "ArgumentStatus",
    "ModeratorAction",
    "DebateMode",
    # 配置
    "ConvergenceTuning",
    "DebateConfig",
    # 数据类
    "ArgumentRef",
    "Argument",
    "SuggestedArgument",
    "ArgumentMenu",
    "SpeakPrompt",
    "MethodologyCall",
    "MethodologyResult",
    "ExpertStatement",
    "ConvergenceSignal",
    "ExternalConsultationRequest",
    "ExternalConsultation",
    "RosterChange",
    "RosterChangeRequest",
    "ModeratorDecision",
    "Round",
    "FinalConsensus",
    "DebateSession",
    # 论点菜单
    "compute_overlap_ratio",
    "merge_menus",
    "StructuredExtractor",
    "ExtractionResult",
    # 专家发言
    "StatementParser",
    "ParseResult",
    "parse_statement",
    "ExpertStatementValidator",
    "DefaultStatementValidator",
    "DUAL_TRACK_SEPARATOR",
    # 收敛判断
    "ConvergenceDetector",
    "ConvergenceCalculator",
    "DefaultConvergenceDetector",
    "compute_session_convergence",
    "should_continue_debate",
    # 主持人
    "Moderator",
    "ModeratorImpl",
    # 协调器
    "SessionOrchestrator",
    "DebateOrchestrator",
    "create_orchestrator",
    "run_debate",
    # v5 兼容
    "V5JuryResult",
    "JuryAdapter",
    "create_jury_adapter",
    "is_legacy_mode",
    "enable_legacy_mode",
    "disable_legacy_mode",
    "wrap_v5_perspective_output",
    # 顶层入口
    "think_v6",
    "convene_v6",
]

# 版本信息
__version__ = "6.0.0"
