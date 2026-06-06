"""
session_recorder.py - 会议记录器

实现辩论会话的完整记录，支持内存和文件两种存储方式。
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from .types import (
    ArgumentMenu,
    DebateSession,
    ExternalConsultation,
    ExpertStatement,
    ModeratorDecision,
    ModeratorDirective,
    RoundNumber,
    SessionId,
    SessionRecorder,
    SessionStatus,
    UserQuestion,
    UserResponse,
)

logger = logging.getLogger(__name__)


@dataclass
class SessionEvent:
    """会话事件"""
    event_type: str
    timestamp: float
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "data": self.data,
        }


class InMemoryRecorder:
    """
    内存会话记录器（默认实现）。
    
    将所有事件存储在内存中，支持导出为 JSON。
    """

    def __init__(self) -> None:
        self._events: list[SessionEvent] = []
        self._session_id: SessionId | None = None
        self._started_at: float | None = None
        self._ended_at: float | None = None

    def on_session_start(self, session: DebateSession) -> None:
        """会话开始"""
        self._session_id = session.session_id
        self._started_at = time.time()
        self._add_event("session_start", {
            "session_id": session.session_id,
            "question": session.question,
            "config": asdict(session.config) if session.config else {},
            "initial_panel_ids": [str(e.id) for e in session.initial_panel],
        })

    def on_round_start(self, round_num: RoundNumber) -> None:
        """轮次开始"""
        self._add_event("round_start", {
            "round_number": int(round_num),
        })

    def on_statement(self, stmt: ExpertStatement) -> None:
        """专家发言"""
        self._add_event("statement", {
            "expert_id": stmt.expert_id,
            "expert_name": stmt.expert_name,
            "role": stmt.role.value if hasattr(stmt.role, "value") else str(stmt.role),
            "content": stmt.content,
            "confidence": stmt.confidence,
            "targeted_argument": (
                asdict(stmt.targeted_argument) 
                if stmt.targeted_argument else None
            ),
            "has_methodology": stmt.methodology_result is not None,
            "warnings": list(stmt.warnings),
        })

    def on_menu_built(self, menu: ArgumentMenu) -> None:
        """菜单构建"""
        self._add_event("menu_update", {
            "round_number": int(menu.round_number),
            "active_arguments": [
                {"id": a.argument_id, "claim": a.claim, "confidence": a.confidence}
                for a in menu.active()
            ],
            "converged_arguments": [
                {"id": a.argument_id, "claim": a.claim}
                for a in menu.converged
            ],
            "focus_topics": list(menu.focus),
        })

    def on_convergence(self, signal: Any) -> None:
        """收敛信号"""
        from .types import ConvergenceSignal
        if isinstance(signal, ConvergenceSignal):
            self._add_event("convergence_signal", {
                "round_number": int(signal.round_number),
                "overlap_rate": signal.overlap_rate,
                "score": signal.score,
                "converged": signal.converged,
                "hard_converged": signal.hard_converged,
            })

    def on_decision(self, decision: ModeratorDecision) -> None:
        """主持人决策"""
        self._add_event("moderator_decision", {
            "action": decision.action.value if hasattr(decision.action, "value") else str(decision.action),
            "reason": decision.reason,
            "hints": list(decision.hints),
        })

    def on_user_question(self, q: UserQuestion, r: UserResponse | None) -> None:
        """用户交互"""
        self._add_event("user_intervention", {
            "question": {
                "id": q.question_id,
                "text": q.text,
                "triggered_by": q.triggered_by,
                "options": list(q.options),
            },
            "response": {
                "id": r.question_id if r else None,
                "answer": r.answer if r else None,
                "new_information": list(r.new_information) if r else [],
            } if r else None,
        })

    def on_external_consultation(self, c: ExternalConsultation) -> None:
        """外部咨询"""
        self._add_event("consult_call", {
            "expert_id": c.request.expert_id,
            "question": c.request.question,
            "timed_out": c.timed_out,
            "response_length": len(c.response_text),
        })

    def on_session_end(self) -> None:
        """会话结束"""
        self._ended_at = time.time()
        duration = (self._ended_at - self._started_at) if self._started_at else 0
        self._add_event("session_end", {
            "duration_s": duration,
        })

    def _add_event(self, event_type: str, data: dict[str, Any]) -> None:
        """添加事件"""
        event = SessionEvent(
            event_type=event_type,
            timestamp=time.time(),
            data=data,
        )
        self._events.append(event)
        logger.debug(f"Recorded event: {event_type}")

    def to_dict(self) -> dict[str, Any]:
        """导出为字典"""
        return {
            "session_id": self._session_id,
            "started_at": self._started_at,
            "ended_at": self._ended_at,
            "events": [e.to_dict() for e in self._events],
            "stats": self._compute_stats(),
        }

    def to_json(self) -> str:
        """导出为 JSON 字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def _compute_stats(self) -> dict[str, Any]:
        """计算统计信息"""
        event_counts: dict[str, int] = {}
        for event in self._events:
            event_counts[event.event_type] = event_counts.get(event.event_type, 0) + 1

        return {
            "total_events": len(self._events),
            "event_counts": event_counts,
            "duration_s": (
                self._ended_at - self._started_at 
                if self._ended_at and self._started_at else 0
            ),
        }

    def summary(self) -> str:
        """生成摘要"""
        stats = self._compute_stats()
        lines = [
            "Session Recording Summary",
            "=" * 40,
            f"Session ID: {self._session_id}",
            f"Started: {datetime.fromtimestamp(self._started_at) if self._started_at else 'N/A'}",
            f"Duration: {stats['duration_s']:.1f}s",
            "",
            "Event Counts:",
        ]
        for event_type, count in stats.get("event_counts", {}).items():
            lines.append(f"  {event_type}: {count}")
        return "\n".join(lines)

    def render(self) -> str:
        """渲染为 Markdown 格式的报告"""
        lines = [
            "# 辩论会话记录",
            "",
            f"**Session ID**: {self._session_id}",
            f"**开始时间**: {datetime.fromtimestamp(self._started_at).isoformat() if self._started_at else 'N/A'}",
            f"**持续时间**: {self._ended_at - self._started_at if self._ended_at and self._started_at else 0:.1f}s",
            "",
            "## 事件流",
            "",
        ]

        for event in self._events:
            ts = datetime.fromtimestamp(event.timestamp).strftime("%H:%M:%S")
            lines.append(f"### [{ts}] {event.event_type}")
            
            if event.event_type == "statement":
                data = event.data
                lines.append(f"- **专家**: {data.get('expert_name', 'N/A')}")
                lines.append(f"- **角色**: {data.get('role', 'N/A')}")
                lines.append(f"- **置信度**: {data.get('confidence', 0):.2f}")
                content = data.get('content', '')
                if len(content) > 200:
                    content = content[:200] + "..."
                lines.append(f"- **内容**: {content}")
