"""
ConvergenceDetector - 收敛检测器

实现三指标加权收敛检测：
- overlap_rate: 本轮与上轮论点的 Jaccard 相似度
- new_arg_density: 每专家平均新论点（active 状态）
- confidence_drift: 跨专家平均 |conf_curr - conf_prev|

综合得分: score = 0.4·overlap + 0.4·(1−density) + 0.2·(1−drift)

2026-06-24 Box哲学改进：增加收敛判断的置信度度量
"""

import math
import typing
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable, TYPE_CHECKING
import logging

from ..types import (
    ExpertStatement,
    ConvergenceTuning,
    ConvergenceSignal,
    DebateSession,
    Round,
    Argument,
    ArgumentStatus,
    ArgumentMenu,
    RoundNumber,
)

if TYPE_CHECKING:
    from ..types import DebateSession

logger = logging.getLogger(__name__)


def calculate_overlap_rate(
    current_args: tuple[Argument, ...],
    previous_args: tuple[Argument, ...],
) -> float:
    """
    计算两个论点集之间的 Jaccard 相似度。
    
    使用论点的 claim 文本进行相似度计算。
    """
    if not previous_args:
        return 0.0
    if not current_args:
        return 0.0
    
    # 提取 claim 集合
    current_claims = set()
    for arg in current_args:
        if arg.status == ArgumentStatus.ACTIVE:
            # 归一化文本用于比较
            normalized = _normalize_text(arg.claim)
            current_claims.add(normalized)
    
    previous_claims = set()
    for arg in previous_args:
        if arg.status == ArgumentStatus.ACTIVE:
            normalized = _normalize_text(arg.claim)
            previous_claims.add(normalized)
    
    if not previous_claims:
        return 0.0
    
    # Jaccard 相似度
    intersection = len(current_claims & previous_claims)
    union = len(current_claims | previous_claims)
    
    if union == 0:
        return 0.0
    
    return intersection / union


def _normalize_text(text: str) -> str:
    """归一化文本用于比较。"""
    # 转为小写，移除标点和多余空格
    import re
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def calculate_new_arg_density(
    current_args: tuple[Argument, ...],
    previous_args: tuple[Argument, ...],
    num_experts: int,
) -> float:
    """
    计算新论点密度。
    
    新论点 = 当前轮中不在上一轮的论点
    密度 = 新论点数 / 专家数
    """
    if num_experts == 0:
        return 0.0
    
    # 提取上一轮的 claim 集合
    previous_claims = set()
    for arg in previous_args:
        normalized = _normalize_text(arg.claim)
        previous_claims.add(normalized)
    
    # 计算当前轮的新论点
    current_active = [arg for arg in current_args if arg.status == ArgumentStatus.ACTIVE]
    new_count = 0
    
    for arg in current_active:
        normalized = _normalize_text(arg.claim)
        if normalized not in previous_claims:
            new_count += 1
    
    return new_count / num_experts


def calculate_confidence_drift(
    current_args: tuple[Argument, ...],
    previous_args: tuple[Argument, ...],
) -> float:
    """
    计算置信度漂移。
    
    对于同一论点的置信度变化，计算平均漂移。
    """
    if not previous_args:
        return 0.0
    
    # 建立上一轮论点 claim -> confidence 的映射
    prev_confidence: dict[str, float] = {}
    for arg in previous_args:
        if arg.status == ArgumentStatus.ACTIVE:
            normalized = _normalize_text(arg.claim)
            prev_confidence[normalized] = arg.confidence
    
    if not prev_confidence:
        return 0.0
    
    # 计算当前轮的置信度漂移
    total_drift = 0.0
    matched_count = 0
    
    for arg in current_args:
        if arg.status == ArgumentStatus.ACTIVE:
            normalized = _normalize_text(arg.claim)
            if normalized in prev_confidence:
                drift = abs(arg.confidence - prev_confidence[normalized])
                total_drift += drift
                matched_count += 1
    
    if matched_count == 0:
        return 1.0  # 最大漂移
    
    return total_drift / matched_count


class JaccardCalculator:
    """
    Jaccard 相似度计算器。
    
    可自定义归一化和相似度算法。
    """
    
    def __init__(
        self,
        normalize_fn: callable = _normalize_text,
        similarity_fn: typing.Optional[callable] = None,
    ):
        self._normalize = normalize_fn
        self._similarity = similarity_fn or self._jaccard
    
    @staticmethod
    def _jaccard(set1: set, set2: set) -> float:
        """标准 Jaccard 相似度。"""
        if not set1 and not set2:
            return 0.0
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0
    
    def calculate(
        self,
        items1: tuple[str, ...],
        items2: tuple[str, ...],
    ) -> float:
        """计算两组文本的相似度。"""
        set1 = {self._normalize(item) for item in items1}
        set2 = {self._normalize(item) for item in items2}
        return self._similarity(set1, set2)


# ── ConvergenceSignal 使用 types.py 的定义，不需要本地重复定义 ──────────────────

@runtime_checkable
class ConvergenceDetector(Protocol):
    """
    收敛检测器协议。
    
    观察辩论会话，计算当前轮收敛信号。
    """
    
    def __init__(self, config: ConvergenceTuning) -> None:
        """初始化收敛检测器。"""
        ...
    
    def observe(self, session: "DebateSession") -> ConvergenceSignal:
        """观察一个 session，计算当前轮收敛信号。"""
        ...
    
    def reset(self) -> None:
        """重置检测器状态。"""
        ...


class AdaptiveThresholdTracker:
    """
    数据驱动的收敛阈值校准器。
    
    Box模型哲学：所有阈值都是错的，有些有用。
    初始阈值是人为设定的，从未数据校准。
    这个追踪器用历史数据来调整阈值。
    """
    
    def __init__(self, initial_threshold: float = 0.65):
        self._threshold = initial_threshold
        self._history: list[tuple[float, bool]] = []  # (score, actual_converged)
        self._min_samples = 20  # 最少20个样本才开始校准
    
    def record_outcome(self, score: float, actually_converged: bool):
        """记录一次决策的结果"""
        self._history.append((score, actually_converged))
        # 保留最近200条
        if len(self._history) > 200:
            self._history = self._history[-200:]
    
    def get_adaptive_threshold(self) -> float:
        """获取自适应阈值（最少min_samples样本后才生效）"""
        if len(self._history) < self._min_samples:
            return self._threshold  # 样本不够，用初始值
        
        # 分析历史：找到最佳阈值
        # 遍历可能的阈值，找精确率+召回率的最佳平衡点
        scores = [s for s, _ in self._history]
        min_s, max_s = min(scores), max(scores)
        
        best_threshold = self._threshold
        best_f1 = 0.0
        
        # 遍历100个候选阈值
        for candidate in [min_s + (max_s - min_s) * i / 100 for i in range(101)]:
            tp = sum(1 for s, c in self._history if s >= candidate and c)
            fp = sum(1 for s, c in self._history if s >= candidate and not c)
            fn = sum(1 for s, c in self._history if s < candidate and c)
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
            
            if f1 > best_f1:
                best_f1 = f1
                best_threshold = candidate
        
        # 平滑变化（不要突变）
        self._threshold = self._threshold * 0.7 + best_threshold * 0.3
        return self._threshold
    
    def get_calibration_stats(self) -> dict:
        """获取校准统计"""
        if len(self._history) < self._min_samples:
            return {"calibrated": False, "sample_count": len(self._history)}
        
        return {
            "calibrated": True,
            "current_threshold": round(self._threshold, 4),
            "sample_count": len(self._history),
            "observed_convergence_rate": round(
                sum(1 for _, c in self._history if c) / len(self._history), 3
            ),
        }


class DefaultConvergenceDetector:
    """
    默认收敛检测器实现。
    
    使用三指标加权算法判断辩论是否收敛。
    """
    
    def __init__(self, config: ConvergenceTuning) -> None:
        """
        初始化收敛检测器。
        
        Args:
            config: 收敛配置参数
        """
        self._config = config
        self._jaccard_calc = JaccardCalculator()
        self._consecutive_count = 0
        self._last_signal: ConvergenceSignal | None = None
        
        # 数据驱动的自适应阈值校准器
        self._threshold_tracker = AdaptiveThresholdTracker(initial_threshold=config.score_threshold)
        
        # 验证权重和
        w1, w2, w3 = config.weights
        if abs(w1 + w2 + w3 - 1.0) > 1e-6:
            raise ValueError(f"权重和必须为 1.0，当前: {w1 + w2 + w3}")
    
    @property
    def config(self) -> ConvergenceTuning:
        """获取配置。"""
        return self._config
    
    @property
    def consecutive_count(self) -> int:
        """获取连续收敛轮数。"""
        return self._consecutive_count
    
    @property
    def last_signal(self) -> ConvergenceSignal | None:
        """获取上一轮收敛信号。"""
        return self._last_signal
    
    def observe(self, session: "DebateSession") -> ConvergenceSignal:
        """
        观察会话，计算收敛信号。
        
        Args:
            session: 当前辩论会话
            
        Returns:
            ConvergenceSignal: 收敛信号
        """
        round_number = RoundNumber(len(session.rounds))
        return self._compute_signal_from_rounds(
            round_number=round_number,
            current_round=session.rounds[-1] if session.rounds else None,
            previous_round=session.rounds[-2] if len(session.rounds) >= 2 else None,
        )

    def detect(
        self,
        *,
        round_number: RoundNumber,
        current_menu: ArgumentMenu,
        previous_menu: ArgumentMenu | None,
        statements: tuple[ExpertStatement, ...],
    ) -> ConvergenceSignal:
        """
        兼容性别名 for observe() - 支持直接传入菜单和发言。

        Args:
            round_number: 当前轮次
            current_menu: 本轮论点菜单
            previous_menu: 上一轮论点菜单
            statements: 本轮专家发言

        Returns:
            ConvergenceSignal: 收敛信号
        """
        # 从 statements 构造 mock Round 对象用于复用 _compute_signal_from_rounds
        current_round = Round(
            round_number=round_number,
            menu=current_menu,
            statements=statements,
        )
        prev_round = Round(
            round_number=RoundNumber(int(round_number) - 1),
            menu=previous_menu,
            statements=(),
        ) if previous_menu else None

        return self._compute_signal_from_rounds(
            round_number=round_number,
            current_round=current_round,
            previous_round=prev_round,
        )

    def _compute_signal_from_rounds(
        self,
        round_number: RoundNumber,
        current_round: Round | None,
        previous_round: Round | None,
    ) -> ConvergenceSignal:
        """从轮次对象计算收敛信号。"""
        if current_round is None or previous_round is None:
            # 第一轮或无历史，无法计算收敛
            signal = ConvergenceSignal(
                round_number=round_number,
                overlap_rate=0.0,
                new_arg_density=1.0,
                confidence_drift=0.0,
                score=0.0,
                converged=False,
                hard_converged=False,
                consecutive_count=0,
                details={"reason": "insufficient_history"},
            )
            self._last_signal = signal
            return signal

        current_menu = current_round.menu
        prev_menu = previous_round.menu
        current_stmts = current_round.statements
        prev_stmts = previous_round.statements

        # 1. 计算论点重叠率
        overlap = self._compute_overlap(current_menu, prev_menu)
        
        # 2. 计算新论点密度
        new_arg_density = self._compute_new_arg_density(
            current_menu, prev_menu, len(current_stmts)
        )
        
        # 3. 计算置信度漂移（基于论点置信度的跨轮变化）
        drift = self._compute_confidence_drift(
            current_stmts, prev_stmts, current_menu, prev_menu
        )
        
        # 4. 综合得分
        score = self._compute_score(overlap, new_arg_density, drift)
        
        # 5. 使用自适应阈值判断收敛
        adaptive_threshold = self._threshold_tracker.get_adaptive_threshold()
        
        if score >= adaptive_threshold:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 0
        
        converged = self._consecutive_count >= self._config.require_consecutive
        hard_converged = (
            overlap >= self._config.overlap_hard_threshold and
            new_arg_density <= self._config.new_arg_hard_threshold
        )
        
        details = {
            "overlap_component": self._config.weights[0] * overlap,
            "density_component": self._config.weights[1] * (1 - new_arg_density),
            "drift_component": self._config.weights[2] * (1 - drift),
            "consecutive_count": self._consecutive_count,
            "threshold": self._config.score_threshold,
            "adaptive_threshold": round(adaptive_threshold, 4),
            "expert_count": len(current_stmts),
            # 2026-06-24 Box哲学新增：收敛判断的不确定性度量
            # 承认模型可能误判，给出置信区间
            "confidence": self._compute_confidence(overlap, new_arg_density, drift, score, len(current_stmts)),
            "confidence_level": self._get_confidence_level(
                overlap, new_arg_density, drift, score, len(current_stmts)
            ),
        }
        
        signal = ConvergenceSignal(
            round_number=round_number,
            overlap_rate=overlap,
            new_arg_density=new_arg_density,
            confidence_drift=drift,
            score=score,
            converged=converged,
            hard_converged=hard_converged,
            consecutive_count=self._consecutive_count,
            details=details,
        )
        
        # 记录决策结果用于后续阈值校准
        self._threshold_tracker.record_outcome(score, converged)
        
        self._last_signal = signal
        return signal
    
    def _compute_overlap(
        self,
        current_menu: ArgumentMenu,
        prev_menu: ArgumentMenu | None,
    ) -> float:
        """论点重叠率（Jaccard 相似度，基于 claim 文本）。"""
        if prev_menu is None or not prev_menu.items or not current_menu.items:
            return 0.0
        prev_claims = {arg.claim.lower().strip() for arg in prev_menu.items}
        curr_claims = {arg.claim.lower().strip() for arg in current_menu.items}
        if not prev_claims or not curr_claims:
            return 0.0
        intersection = len(prev_claims & curr_claims)
        union = len(prev_claims | curr_claims)
        return intersection / union if union > 0 else 0.0
    
    def _compute_new_arg_density(
        self,
        current_menu: ArgumentMenu,
        prev_menu: ArgumentMenu | None,
        num_experts: int,
    ) -> float:
        """新论点密度（每专家平均新论点，归一化到 [0,1]）。"""
        if prev_menu is None or not prev_menu.items:
            return 0.0
        prev_claims = {arg.claim.lower().strip() for arg in prev_menu.items}
        new_count = sum(
            1 for arg in current_menu.items
            if arg.claim.lower().strip() not in prev_claims
        )
        if num_experts <= 0:
            return 0.0
        avg_new_per_expert = new_count / num_experts
        normalized = avg_new_per_expert / 3.0
        return min(1.0, max(0.0, normalized))
    
    def _compute_confidence_drift(
        self,
        current_stmts: tuple[ExpertStatement, ...],
        prev_stmts: tuple[ExpertStatement, ...],
        current_menu: ArgumentMenu,
        prev_menu: ArgumentMenu | None,
    ) -> float:
        """
        置信度漂移：基于论点置信度的跨轮变化。
        
        对于上一轮出现过的论点，比较本轮与上轮的置信度差异。
        若论点为新提出（上一轮没有），不计入漂移计算。
        
        公式：drift = mean(|conf_curr - conf_prev|) for matched arguments
        """
        if prev_menu is None or not prev_menu.items:
            return 0.0
        
        # 建立上一轮 claim -> confidence 映射（只针对 active 论点）
        prev_confidence: dict[str, float] = {}
        for arg in prev_menu.items:
            if arg.status == ArgumentStatus.ACTIVE:
                prev_confidence[arg.claim.lower().strip()] = arg.confidence
        
        if not prev_confidence:
            return 0.0
        
        # 计算当前轮匹配论点的置信度漂移
        total_drift = 0.0
        matched_count = 0
        
        for arg in current_menu.items:
            if arg.status == ArgumentStatus.ACTIVE:
                key = arg.claim.lower().strip()
                if key in prev_confidence:
                    drift = abs(arg.confidence - prev_confidence[key])
                    total_drift += drift
                    matched_count += 1
        
        if matched_count == 0:
            return 1.0  # 无匹配论点，最大漂移
        
        return min(1.0, total_drift / matched_count)
    
    def _compute_score(
        self,
        overlap: float,
        new_arg_density: float,
        drift: float,
    ) -> float:
        """
        综合收敛得分。
        score = w1*overlap + w2*(1-density) + w3*(1-drift)
        """
        w1, w2, w3 = self._config.weights
        score = w1 * overlap + w2 * (1 - new_arg_density) + w3 * (1 - drift)
        return min(1.0, max(0.0, score))
    
    def _check_convergence(
        self,
        overlap: float,
        new_arg_density: float,
        score: float,
    ) -> tuple[bool, bool]:
        """判断是否收敛。Returns: (软收敛, 硬收敛)."""
        hard_converged = (
            overlap >= self._config.overlap_hard_threshold and
            new_arg_density <= self._config.new_arg_hard_threshold
        )
        soft_converged = (
            self._consecutive_count >= self._config.require_consecutive
        )
        return soft_converged, hard_converged
    
    def _compute_confidence(
        self,
        overlap: float,
        new_arg_density: float,
        drift: float,
        score: float,
        num_experts: int,
    ) -> float:
        """
        2026-06-24 Box哲学：计算收敛判断的置信度（0-1）。
        
        置信度影响因素：
        1. 专家数量：越多越可靠
        2. 指标稳定性：三个指标值越稳定（不过于接近阈值边界），置信度越高
        3. 连续收敛次数：越多越可靠
        
        返回：0-1 的置信度，越高表示收敛判断越可靠
        """
        # 样本量因子：专家越多，置信度越高（对数增长，边际递减）
        sample_factor = min(1.0, math.log(num_experts + 1) / math.log(8))
        
        # 稳定性因子：指标越远离阈值边界，越稳定
        # score 距离 0.5（中间值）越远，越确定
        stability_score = abs(score - 0.5) * 2  # 0-1，0.5时为0，0或1时为1
        
        # 重叠率稳定性
        # 远离 0（完全无重叠）和 1（完全重叠）
        stability_overlap = 1.0 - abs(overlap - 0.7) if overlap < 0.7 else overlap
        
        # 新论点密度稳定性：低密度表示收敛
        stability_density = 1.0 - new_arg_density
        
        # 组合稳定性
        combined_stability = (stability_score * 2 + stability_overlap + stability_density) / 4
        
        # 综合置信度
        confidence = (sample_factor * 0.3 + combined_stability * 0.5 + 
                     (self._consecutive_count / max(self._config.require_consecutive, 1)) * 0.2)
        
        return round(min(1.0, max(0.0, confidence)), 3)
    
    def _get_confidence_level(
        self,
        overlap: float,
        new_arg_density: float,
        drift: float,
        score: float,
        num_experts: int,
    ) -> str:
        """
        2026-06-24 Box哲学：返回收敛判断的置信等级。
        
        置信等级：
        - "high": 置信度 >= 0.8，收敛判断高度可靠
        - "medium": 置信度 0.5-0.8，收敛判断中等可靠
        - "low": 置信度 < 0.5，收敛判断不可靠，可能误判
        """
        conf = self._compute_confidence(overlap, new_arg_density, drift, score, num_experts)
        if conf >= 0.8:
            return "high"
        elif conf >= 0.5:
            return "medium"
        else:
            return "low"
    
    def reset(self) -> None:
        """重置检测器状态（连续收敛计数器等）。"""
        self._consecutive_count = 0
        self._last_signal = None


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
        计算当前轮次的收敛信号。
        
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
        计算综合收敛得分。
        
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
        判断是否收敛。
        
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
        self._co

