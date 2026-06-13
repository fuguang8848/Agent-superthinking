"""
v6 Expert Pool Module

Dynamic expert pool with hot-swapping support.
"""

from __future__ import annotations
import time
import logging
from typing import Protocol, runtime_checkable, TYPE_CHECKING
from .types import Expert, ExpertId, ExpertPool as ExpertPoolProtocol, DebateSession, RosterChange

if TYPE_CHECKING:
    from .types import DebateConfig, LLMProvider, MethodologyRegistry, SessionRecorder

logger = logging.getLogger(__name__)

@runtime_checkable
class ExpertPool(ExpertPoolProtocol):
    """Expert pool with registry style."""
    
    def __init__(self):
        self._experts: dict[ExpertId, Expert] = {}
        self._session_active: dict[str, set[ExpertId]] = {}
    
    def register(self, expert: Expert) -> None:
        self._experts[expert.id] = expert
        logger.info(f"Registered expert: {expert.id} ({expert.name})")
    
    def unregister(self, expert_id: ExpertId) -> None:
        if expert_id in self._experts:
            del self._experts[expert_id]
            logger.info(f"Unregistered expert: {expert_id}")
    
    def get(self, expert_id: ExpertId) -> Expert | None:
        return self._experts.get(expert_id)
    
    def list_registered(self) -> tuple[Expert, ...]:
        return tuple(self._experts.values())
    
    def list_active_in_session(self, session: DebateSession) -> tuple[Expert, ...]:
        active_ids = self._session_active.get(str(session.session_id), set())
        return tuple(self._experts[eid] for eid in active_ids if eid in self._experts)
    
    def suggest_for(self, question: str, *, top_k: int = 5) -> tuple[Expert, ...]:
        scored = []
        for expert in self._experts.values():
            score = sum(1 for kw in expert.trigger_keywords if kw.lower() in question.lower())
            scored.append((score, expert))
        scored.sort(key=lambda x: -x[0])
        return tuple(e for _, e in scored[:top_k])
    
    def apply_roster_change(self, session: DebateSession, change: RosterChange) -> bool:
        session_id = str(session.session_id)
        if session_id not in self._session_active:
            self._session_active[session_id] = set()
        
        if change.action == "add":
            expert = self._experts.get(change.expert_id)
            if expert:
                self._session_active[session_id].add(change.expert_id)
                return True
        elif change.action == "remove":
            self._session_active[session_id].discard(change.expert_id)
            return True
        return False
    
    def active_ids(self, session_id: str) -> tuple[ExpertId, ...]:
        return tuple(self._session_active.get(session_id, set()))
    
    def snapshot(self) -> dict:
        return {
            "registered": [str(eid) for eid in self._experts],
            "sessions": {sid: list(ids) for sid, ids in self._session_active.items()},
        }

__all__ = ["ExpertPool"]
