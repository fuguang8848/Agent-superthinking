"""
recorder/file_recorder.py - JSONL 文件记录器

§5.7 SessionRecorder：追加写，每次事件一行 JSON。
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from ..types import (
    DebateSession,
    ExpertStatement,
    ArgumentMenu,
    ModeratorDecision,
    ConvergenceSignal,
    UserQuestion,
    UserResponse,
    ExternalConsultation,
    RoundNumber,
    SessionId,
)

if True:
    from ..types import SessionRecorder

logger = logging.getLogger(__name__)


class FileRecorder:
    """
    JSONL 文件记录器，追加写。

    每次事件写入一行 JSON，便于日志收集和回放。
    """

    def __init__(self, path: str | Path):
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._buffer: list[dict] = []
        self._session_id: SessionId | None = None

    # -------------------------------------------------------------------------
    # 内部工具
    # -------------------------------------------------------------------------

    def _write(self, event_type: str, data: dict, round_number: RoundNumber | None = None) -> None:
        record = {
            "event_type": event_type,
            "session_id": str(self._session_id) if self._session_id else None,
            "round_number": int(round_number) if round_number else None,
            "timestamp": _now(),
            "data": data,
        }
        self._buffer.append(record)
        try:
            with open(self._path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.warning(f"FileRecorder write failed: {e}")

    # -------------------------------------------------------------------------
    # SessionRecorder Protocol 实现
    # -------------------------------------------------------------------------

    def on_session_start(self, session: DebateSession) -> None:
        self._session_id = session.session_id
        self._write("session_start", {
            "question": session.question,
            "config": {
                "max_rounds": session.config.max_rounds,
                "mode": session.config.mode.value,
            },
        })

    def on_round_start(self, round_number: RoundNumber) -> None:
        self._write("round_start", {"round": int(round_number)}, round_number)

    def on_statement(self, stmt: ExpertStatement) -> None:
        self._write("statement", {
            "expert_id": str(stmt.expert_id),
            "expert_name": stmt.expert_name,
            "role": stmt.role.value,
            "content": stmt.content,
            "confidence": stmt.confidence,
        })

    def on_menu_built(self, menu: ArgumentMenu) -> None:
        self._write("menu_built", {
            "round": int(menu.round_number),
            "item_count": len(menu.items),
        }, menu.round_number)

    def on_convergence(self, signal: Any) -> None:
        if not isinstance(signal, ConvergenceSignal):
            return
        self._write("convergence", {
            "converged": signal.converged,
            "overall_score": signal.overall_score,
            "overlap": signal.overlap,
            "new_arg_density": signal.new_arg_density,
            "confidence_drift": signal.confidence_drift,
        })

    def on_decision(self, decision: ModeratorDecision) -> None:
        self._write("decision", {
            "action": decision.action.value,
            "reason": decision.reason,
            "question_to_user": decision.question_to_user,
        })

    def on_user_question(self, q: UserQuestion, r: UserResponse | None) -> None:
        self._write("user_question", {
            "question_id": str(q.question_id),
            "question": q.question,
            "response": r.response_text if r else None,
        })

    def on_external_consultation(self, c: ExternalConsultation) -> None:
        self._write("external_consultation", {
            "expert_id": str(c.expert_id),
            "question": c.question,
            "response": c.response_text,
            "timed_out": c.timed_out,
        })

    def on_session_end(self) -> None:
        self._write("session_end", {"buffered": len(self._buffer)})

    # -------------------------------------------------------------------------
    # 读取接口
    # -------------------------------------------------------------------------

    def to_dict(self) -> dict:
        """将文件中所有记录读回为 list[dict]。"""
        if not self._path.exists():
            return {"records": []}
        records = []
        with open(self._path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except Exception:
                        pass
        return {"records": records}

    def render(self) -> str:
        """人类可读格式输出。"""
        data = self.to_dict()
        lines = [f"=== FileRecorder: {self._path} ==="]
        for rec in data.get("records", []):
            ts = rec.get("timestamp", "")
            evt = rec.get("event_type", "")
            d = rec.get("data", {})
            lines.append(f"[{ts}] {evt}: {d}")
        return "\n".join(lines)


def _now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


__all__ = ["FileRecorder"]