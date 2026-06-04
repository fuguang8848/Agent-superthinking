"""
Team Integration — 将 AgentTeam ContextBoard 多专家协作能力接入 SuperThinking.

ContextBoard 提供共享空间，让各专家视角可以：
- 发布自己的分析进度和结论
- 看到其他专家的当前状态
- 基于已有结论深化自己的分析
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class ExpertPhase(str, Enum):
    """专家分析阶段。"""

    THINKING = "thinking"  # 正在分析
    CONCLUDED = "concluded"  # 已得出结论
    WAITING = "waiting"  # 等待其他专家结论
    REVIEWING = "reviewing"  # 在参考其他专家结论


@dataclass
class ExpertContextEntry:
    """专家在 ContextBoard 上的上下文条目。"""

    expert_name: str
    perspective_id: str
    phase: ExpertPhase
    title: str  # 如："尼采视角：关于人生意义的分析"
    description: Optional[str] = None
    key_insights: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    links_to: list[str] = field(default_factory=list)  # 链接到其他专家 ID
    file_path: Optional[str] = None
    is_pinned: bool = False


class TeamIntegration:
    """
    多专家协作管理层。

    将 AgentTeam ContextBoard 的协作机制适配到 SuperThinking：
    - 各专家视角分析时，在 context_board 上发布自己的进度
    - 其他专家可以"感知"已有结论，实现协作深化
    - 最终综合阶段读取所有条目，生成完整报告

    使用方式：
        team = TeamIntegration(session_id="analysis_20240101")
        team.publish_start(expert_name="尼采", perspective_id="nietzsche_perspective", title="...")
        # ... 尼采视角分析中 ...
        team.publish_insight("尼采", "反抗荒谬是生命的意义所在")
        team.publish_concluded("尼采", ["核心结论1", "核心结论2"])
        # 其他专家可以读取已有结论深化
        other_insights = team.get_other_insights(exclude="尼采")
    """

    def __init__(self, session_id: str = ""):
        self._session_id = session_id or datetime.now(timezone.utc).strftime(
            "%Y%m%d_%H%M%S"
        )
        self._board: dict[str, ExpertContextEntry] = {}
        self._concluded_count = 0
        self._total_experts = 0

    @property
    def session_id(self) -> str:
        return self._session_id

    def register_experts(self, expert_names: list[str]) -> None:
        """注册参与本次分析的专家列表。"""
        self._total_experts = len(expert_names)
        self._concluded_count = 0

    def publish_start(
        self,
        expert_name: str,
        perspective_id: str,
        title: str,
        description: Optional[str] = None,
    ) -> None:
        """发布专家开始分析。"""
        entry = ExpertContextEntry(
            expert_name=expert_name,
            perspective_id=perspective_id,
            phase=ExpertPhase.THINKING,
            title=title,
            description=description,
        )
        self._board[expert_name] = entry
        logger.info(f"[{self._session_id}] {expert_name} 开始分析")

    def publish_insight(
        self,
        expert_name: str,
        insight: str,
        link_to: Optional[list[str]] = None,
    ) -> None:
        """发布专家的中间洞察。"""
        if expert_name not in self._board:
            logger.warning(f"Expert {expert_name} not registered")
            return

        entry = self._board[expert_name]
        entry.key_insights.append(insight)
        if link_to:
            entry.links_to.extend(link_to)
        logger.debug(f"[{self._session_id}] {expert_name} insight: {insight[:50]}...")

    def publish_concluded(
        self,
        expert_name: str,
        conclusions: list[str],
        tags: Optional[list[str]] = None,
    ) -> None:
        """发布专家得出最终结论。"""
        if expert_name not in self._board:
            logger.warning(f"Expert {expert_name} not registered")
            return

        entry = self._board[expert_name]
        entry.phase = ExpertPhase.CONCLUDED
        entry.key_insights.extend(conclusions)
        if tags:
            entry.tags.extend(tags)
        self._concluded_count += 1
        logger.info(
            f"[{self._session_id}] {expert_name} 得出结论 ({self._concluded_count}/{self._total_experts})"
        )

    def mark_waiting(self, expert_name: str, waiting_for: list[str]) -> None:
        """标记专家正在等待其他专家结论。"""
        if expert_name not in self._board:
            return
        entry = self._board[expert_name]
        entry.phase = ExpertPhase.WAITING

    def mark_reviewing(self, expert_name: str) -> None:
        """标记专家正在参考其他专家结论。"""
        if expert_name not in self._board:
            return
        entry = self._board[expert_name]
        entry.phase = ExpertPhase.REVIEWING

    def get_other_insights(
        self,
        exclude: str,
        phases: Optional[list[ExpertPhase]] = None,
    ) -> list[tuple[str, list[str]]]:
        """获取其他专家的洞察（供深化分析用）。"""
        results = []
        for name, entry in self._board.items():
            if name == exclude:
                continue
            if phases and entry.phase not in phases:
                continue
            if entry.key_insights:
                results.append((name, entry.key_insights))
        return results

    def get_concluded_experts(self) -> list[str]:
        """获取已得出结论的专家列表。"""
        return [
            name
            for name, entry in self._board.items()
            if entry.phase == ExpertPhase.CONCLUDED
        ]

    def get_waiting_experts(self) -> list[str]:
        """获取正在等待的专家列表。"""
        return [
            name
            for name, entry in self._board.items()
            if entry.phase == ExpertPhase.WAITING
        ]

    def get_board_summary(self) -> dict[str, Any]:
        """获取 board 状态摘要。"""
        by_phase = {}
        for name, entry in self._board.items():
            phase = entry.phase.value
            if phase not in by_phase:
                by_phase[phase] = []
            by_phase[phase].append(name)

        return {
            "session_id": self._session_id,
            "total_experts": self._total_experts,
            "concluded_count": self._concluded_count,
            "progress": (
                f"{self._concluded_count}/{self._total_experts}"
                if self._total_experts > 0
                else "0/0"
            ),
            "by_phase": by_phase,
        }

    def get_full_context(self) -> str:
        """
        生成完整的协作上下文字符串。

        用于在综合阶段将所有专家的洞察汇总。
        """
        lines = [f"## 专家协作分析记录 [{self._session_id}]\n"]
        lines.append(f"进度：{self.get_board_summary()['progress']}\n")

        # 按阶段排序输出
        phase_order = [
            ExpertPhase.CONCLUDED,
            ExpertPhase.REVIEWING,
            ExpertPhase.THINKING,
            ExpertPhase.WAITING,
        ]

        for phase in phase_order:
            experts_in_phase = [
                (name, e)
                for name, e in self._board.items()
                if e.phase == phase
            ]
            if not experts_in_phase:
                continue

            lines.append(f"\n### {phase.value.upper()} ({len(experts_in_phase)}位)\n")
            for name, entry in experts_in_phase:
                lines.append(f"\n#### {name}: {entry.title}\n")
                if entry.key_insights:
                    for insight in entry.key_insights:
                        lines.append(f"- {insight}\n")
                if entry.links_to:
                    lines.append(f"  → 链接到: {', '.join(entry.links_to)}\n")

        return "".join(lines)

    def reset(self) -> None:
        """重置 board 状态。"""
        self._board.clear()
        self._concluded_count = 0
        self._total_experts = 0


# 便捷函数：创建团队协作会话
def create_team_session(question: str, experts: list[str]) -> TeamIntegration:
    """创建团队协作会话。"""
    session_id = f"supthink_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    team = TeamIntegration(session_id=session_id)
    team.register_experts(experts)
    return team
