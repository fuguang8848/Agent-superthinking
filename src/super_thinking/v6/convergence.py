"""
v6 收敛判断模块

实现核心收敛算法，判断辩论是否达到收敛状态。
算法公式：score = 0.4·overlap + 0.4·(1−new_arg_density) + 0.2·(1−drift)
阈值 0.65 持续 ≥ 1 轮触发收敛。
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from .types import (
    ConvergenceSignal,
    ConvergenceTuning,
    DebateSession,
    Argument,
    ArgumentMenu,
    ExpertStatement,
    RoundNumber,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


# =============================================================================
# ConvergenceDetector 协议
# =============================================================================

@runtime_checkable
class ConvergenceDetector(Protocol):
    """收敛检测器协议"""

    def observe(self, session: DebateSession) -> ConvergenceSignal:
        """观察 session，计算当前轮收敛信号"""
        ...

    def reset(self) -> None:
        """重置状态"""
        ...


# =============================================================================
# ConvergenceCalculator — 收敛计算器
# =============================================================================

class ConvergenceCalculator:
    """
    收敛状态计算器。

    核心算法：
    score = 0.4·overlap + 0.4·(1−new_arg_density) + 0.2·(1−drift)

    其中：
    - overlap: 本轮与上轮论点的重叠率（Jaccard 相似度）
    - new_arg_density: 每专家平均新论点数量（归一化）
    - drift: 跨专家平均置信度变化

    收敛条件：
    - 软收敛：score >= threshold 持续 require_consecutive 轮
    - 硬收敛：overlap >= overlap_hard_threshold 且 new_arg_density <= new_arg_hard_threshold
    """

    def __init__(self, config: ConvergenceTuning):
        self.config = config
        self._consecutive_count = 0  # 连续达标次数
        self._last_signal: ConvergenceSignal | None = None

    def compute_signal(
        self,
        current_menu: ArgumentMenu,
        prev_menu: ArgumentMenu | None,
        statements: tuple[ExpertStatement, ...],
        round_number: RoundNumber,
    ) -> ConvergenceSignal:
        """
        计算当前轮次的收敛信号.

        Args:
            current_menu: 本轮菜单
            prev_menu: 上一轮菜单
            statements: 本轮所有专家发言
            round_number: 当前轮次

        Returns:
            ConvergenceSignal: 收敛信号
        """
        # 边界处理：首轮不判断
        if round_number <= 1:
            return ConvergenceSignal(
                round_number=round_number,
                overlap_rate=0.0,
                new_arg_density=0.0,
                confidence_drift=0.0,
                score=0.0,
                converged=False,
                hard_converged=False,
                details={"reason": "First round, not evaluated"},
            )

        # 边界处理：只有一个专家不判断
        if len(statements) <= 1:
            return ConvergenceSignal(
                round_number=round_number,
                overlap_rate=0.0,
                new_arg_density=0.0,
                confidence_drift=0.0,
                score=0.0,
                converged=False,
                hard_converged=False,
                details={"reason": "Single expert, not evaluated"},
            )

        # 1. 计算重叠率
        overlap = self._compute_overlap(current_menu, prev_menu)

        # 2. 计算新论点密度
        new_arg_density = self._compute_new_arg_density(current_menu, prev_menu, len(statements))

        # 3. 计算置信度漂移
        drift = self._compute_confidence_drift(statements)

        # 4. 计算综合得分
        score = self._compute_score(overlap, new_arg_density, drift)

        # 5. 判断收敛
        converged, hard_converged = self._check_convergence(overlap, new_arg_density, score)

        # 构建详情
        details = {
            "overlap_component": 0.4 * overlap,
            "density_component": 0.4 * (1 - new_arg_density),
            "drift_component": 0.2 * (1 - drift),
            "consecutive_count": self._consecutive_count,
            "threshold": self.config.score_threshold,
            "expert_count": len(statements),
        }

        signal = ConvergenceSignal(
            round_number=round_number,
            overlap_rate=overlap,
            new_arg_density=new_arg_density,
            confidence_drift=drift,
            score=score,
            converged=converged,
            hard_converged=hard_converged,
            details=details,
        )

        self._last_signal = signal
        return signal

    def _compute_overlap(
        self,
        current_menu: ArgumentMenu,
        prev_menu: ArgumentMenu | None,
    ) -> float:
        """
        计算论点重叠率（Jaccard 相似度）。

        基于 claim 文本的字符串相等判断。
        """
        if prev_menu is None or not prev_menu.items or not current_menu.items:
            return 0.0

        # 使用 Jaccard 相似度
        prev_claims = {arg.claim.lower().strip() for arg in prev_menu.items}
        curr_claims = {arg.claim.lower().strip() for arg in current_menu.items}

        if not prev_claims or not curr_claims:
            return 0.0

        intersection = len(prev_claims & curr_claims)
        union = len(prev_claims | curr_claims)

        if union == 0:
            return 1.0

        return intersection / union

    def _compute_new_arg_density(
        self,
        current_menu: ArgumentMenu,
        prev_menu: ArgumentMenu | None,
        num_experts: int,
    ) -> float:
        """
        计算新论点密度（每专家平均新论点）。

        归一化到 [0, 1]，其中 0 表示有很多新论点，1 表示没有新论点。
        """
        if prev_menu is None or not prev_menu.items:
            # 首轮或无历史，所有论点都是新的
            return 0.0

        prev_claims = {arg.claim.lower().strip() for arg in prev_menu.items}
        new_count = sum(
            1 for arg in current_menu.items
            if arg.claim.lower().strip() not in prev_claims
        )

        # 每专家平均新论点
        if num_experts <= 0:
            return 0.0

        avg_new_per_expert = new_count / num_experts

        # 归一化：假设每专家最多 3 个新论点是"正常"值
        normalized = avg_new_per_expert / 3.0
        return min(1.0, max(0.0, normalized))

    def _compute_confidence_drift(
        self,
        statements: tuple[ExpertStatement, ...],
    ) -> float:
        """
        计算跨专家的置信度漂移。

        比较本轮置信度与上一轮的差异。
        """
        if not statements:
            return 0.0

        # 计算平均置信度
        avg_confidence = sum(stmt.confidence for stmt in statements) / len(statements)

        # 估算漂移：置信度偏离 0.5 的程度
        # 0.5 是中性置信度，越接近 0.5 表示越不确定
        drift = abs(avg_confidence - 0.5) * 2

        return min(1.0, max(0.0, drift))

    def _compute_score(
        self,
        overlap: float,
        new_arg_density: float,
        drift: float,
    ) -> float:
        """
        计算综合收敛得分.

        score = 0.4·overlap + 0.4·(1−new_arg_density) + 0.2·(1−drift)

        得分越高表示越收敛：
        - overlap 高：论点重叠多
        - new_arg_density 低：新论点少
        - drift 低：置信度稳定
        """
        w_overlap, w_density, w_drift = self.config.weights

        score = (
            w_overlap * overlap +
            w_density * (1 - new_arg_density) +
            w_drift * (1 - drift)
        )

        return min(1.0, max(0.0, score))

    def _check_convergence(
        self,
        overlap: float,
        new_arg_density: float,
        score: float,
    ) -> tuple[bool, bool]:
        """
        判断是否收敛.

        Returns:
            (软收敛, 硬收敛)
        """
        hard_converged = (
            overlap >= self.config.overlap_hard_threshold and
            new_arg_density <= self.config.new_arg_hard_threshold
        )

        if score >= self.config.score_threshold:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 0

        soft_converged = self._consecutive_count >= self.config.require_consecutive

        return soft_converged, hard_converged

    def reset(self) -> None:
        """重置状态"""
        self._consecutive_count = 0
        self._last_signal = None


# =============================================================================
# DefaultConvergenceDetector — 默认收敛检测器实现
# =============================================================================

class DefaultConvergenceDetector:
    """
    默认收敛检测器。

    实现了 ConvergenceDetector 协议，并额外提供 detect() 方法
    用于直接计算当前轮的收敛信号。
    """

    def __init__(self, config: ConvergenceTuning | None = None):
        self._config = config or ConvergenceTuning()
        self._calculator = ConvergenceCalculator(self._config)

    def detect(
        self,
        round_number: RoundNumber,
        current_menu: ArgumentMenu,
        previous_menu: ArgumentMenu | None,
        statements: tuple[ExpertStatement, ...],
    ) -> ConvergenceSignal:
        """
        直接计算当前轮的收敛信号。

        这是 DefaultModerator 使用的便捷方法。
        """
        return self._calculator.compute_signal(
            current_menu=current_menu,
            prev_menu=previous_menu,
            statements=statements,
            round_number=round_number,
        )

    def observe(self, session: DebateSession) -> ConvergenceSignal:
        """
        从 session 中提取当前轮信息并计算收敛信号。
        """
        if not session.rounds:
            return ConvergenceSignal(
                round_number=RoundNumber(1),
                converged=False,
                hard_converged=False,
            )
        last_round = session.rounds[-1]
        prev_menu = session.rounds[-1].menu if len(session.rounds) > 1 else None
        return self._calculator.compute_signal(
            current_menu=last_round.menu,
            prev_menu=prev_menu,
            statements=last_round.statements,
            round_number=RoundNumber(len(session.rounds)),
        )

    def reset(self) -> None:
        """重置状态"""
        self._calculator.reset()


# =============================================================================
# 便捷函数
# =============================================================================

def compute_session_convergence(session: DebateSession) -> ConvergenceSignal:
    """
    便捷函数：从 session 计算整体收敛状态。
    """
    detector = DefaultConvergenceDetector(session.config.convergence)
    return detector.observe(session)


def should_continue_debate(session: DebateSession) -> bool:
    """
    判断辩论是否应该继续。

    Returns:
        True 如果应该继续，False 如果应该收敛或结束。
    """
    signal = compute_session_convergence(session)
    if signal.converged or signal.hard_converged:
        return False
    if len(session.rounds) >= session.config.max_rounds:
        return False
    if len(session.active_experts) < session.config.min_experts_to_continue:
        return False
    return True


__all__ = [
    "ConvergenceDetector",
    "ConvergenceCalculator",
    "DefaultConvergenceDetector",
    "compute_session_convergence",
    "should_continue_debate",
]
