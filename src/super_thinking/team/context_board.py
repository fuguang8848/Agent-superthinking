"""
ContextBoard - Shared collaboration board for expert insights.

Provides a shared state where experts publish intermediate conclusions
that other experts can read to deepen their own analysis.

Collaboration stages:
- THINKING: Expert is actively analyzing
- WAITING: Expert is waiting for other experts' insights
- REVIEWING: Expert is reviewing other experts' conclusions
- CONCLUDED: Expert has published final conclusion

Internal testing version - not exposed to regular users.
"""

from __future__ import annotations

import threading
import time
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any

logger = logging.getLogger(__name__)


class ExpertStatus(str, Enum):
    """Collaboration status for an expert on the board."""

    THINKING = "THINKING"  # Actively analyzing
    WAITING = "WAITING"  # Waiting for other experts' insights
    REVIEWING = "REVIEWING"  # Reviewing other experts' conclusions
    CONCLUDED = "CONCLUDED"  # Final conclusion published


@dataclass
class ExpertEntry:
    """An expert's state and insights on the board."""

    expert_id: str
    status: ExpertStatus = ExpertStatus.THINKING
    insight: Optional[str] = None  # Intermediate or final conclusion
    timestamp: float = field(default_factory=time.time)
    layer: int = 0  # Execution layer (0 = first, 1 = second, etc.)

    def is_visible(self) -> bool:
        """Whether this expert's insight is visible to others."""
        return self.status in (ExpertStatus.REVIEWING, ExpertStatus.CONCLUDED)


@dataclass
class BoardSnapshot:
    """Point-in-time view of the board."""

    entries: dict[str, ExpertEntry]
    total_experts: int
    concluded_count: int
    timestamp: float


class ContextBoard:
    """
    Shared collaboration board for expert insights.

    Thread-safe board where experts publish intermediate conclusions.
    Other experts can read conclusions from earlier layers to
    deepen their own analysis.

    Usage:
        board = ContextBoard()

        # Expert A publishes
        board.register("expert_a")
        board.publish_insight("expert_a", "Initial finding: X")
        board.publish_concluded("expert_a")

        # Expert B reads A's conclusion, then publishes
        board.register("expert_b")
        board.publish_insight("expert_b", "Based on A: Y")
        board.publish_concluded("expert_b")
    """

    def __init__(self):
        self._entries: dict[str, ExpertEntry] = {}
        self._lock = threading.RLock()
        self._version = 0  # Incremented on each change

    # -------------------------------------------------------------------------
    # Expert lifecycle
    # -------------------------------------------------------------------------

    def register(self, expert_id: str, layer: int = 0) -> ExpertEntry:
        """
        Register an expert on the board.

        Args:
            expert_id: Unique identifier for the expert
            layer: Execution layer (0 = first wave, 1 = second wave, etc.)
                   Experts in higher layers can read insights from lower layers.

        Returns:
            The expert's board entry
        """
        with self._lock:
            entry = ExpertEntry(expert_id=expert_id, layer=layer)
            self._entries[expert_id] = entry
            self._version += 1
            logger.debug(f"[ContextBoard] Registered expert: {expert_id} (layer {layer})")
            return entry

    def unregister(self, expert_id: str) -> None:
        """Remove an expert from the board."""
        with self._lock:
            self._entries.pop(expert_id, None)
            self._version += 1

    # -------------------------------------------------------------------------
    # Status transitions
    # -------------------------------------------------------------------------

    def publish_insight(
        self,
        expert_id: str,
        insight: str,
        status: ExpertStatus = ExpertStatus.REVIEWING,
    ) -> None:
        """
        Publish an intermediate insight.

        Args:
            expert_id: Expert's ID
            insight: Intermediate conclusion text
            status: New status (defaults to REVIEWING)
        """
        with self._lock:
            if expert_id not in self._entries:
                self.register(expert_id)

            entry = self._entries[expert_id]
            entry.insight = insight
            entry.status = status
            entry.timestamp = time.time()
            self._version += 1
            logger.debug(f"[ContextBoard] {expert_id} published insight: {insight[:80]}...")

    def publish_concluded(self, expert_id: str, final_insight: Optional[str] = None) -> None:
        """
        Mark expert as concluded with final conclusion.

        Args:
            expert_id: Expert's ID
            final_insight: Final conclusion text (overrides current insight if provided)
        """
        with self._lock:
            if expert_id not in self._entries:
                self.register(expert_id)

            entry = self._entries[expert_id]
            if final_insight is not None:
                entry.insight = final_insight
            entry.status = ExpertStatus.CONCLUDED
            entry.timestamp = time.time()
            self._version += 1
            logger.debug(f"[ContextBoard] {expert_id} concluded")

    def set_waiting(self, expert_id: str) -> None:
        """Mark expert as waiting for other experts' insights."""
        with self._lock:
            if expert_id not in self._entries:
                self.register(expert_id)
            self._entries[expert_id].status = ExpertStatus.WAITING
            self._version += 1

    # -------------------------------------------------------------------------
    # Read operations
    # -------------------------------------------------------------------------

    def get_entry(self, expert_id: str) -> Optional[ExpertEntry]:
        """Get a specific expert's entry."""
        with self._lock:
            return self._entries.get(expert_id)

    def get_visible_insights(
        self,
        expert_id: str,
        exclude_self: bool = True,
    ) -> dict[str, str]:
        """
        Get all visible insights from other experts.

        Args:
            expert_id: Requesting expert (typically excluded)
            exclude_self: Whether to exclude the requesting expert's own insight

        Returns:
            Dict of expert_id -> insight text for all visible insights
        """
        with self._lock:
            my_layer = self._entries.get(expert_id, ExpertEntry(expert_id=expert_id)).layer
            result = {}

            for eid, entry in self._entries.items():
                if exclude_self and eid == expert_id:
                    continue
                if not entry.is_visible():
                    continue
                # By default, only show insights from earlier or same layer
                # (experts can read from same layer if already concluded)
                if entry.layer > my_layer and entry.status != ExpertStatus.CONCLUDED:
                    continue
                if entry.insight:
                    result[eid] = entry.insight

            return result

    def get_board_state(self) -> BoardSnapshot:
        """Get a point-in-time snapshot of the entire board."""
        with self._lock:
            concluded = sum(1 for e in self._entries.values() if e.status == ExpertStatus.CONCLUDED)
            return BoardSnapshot(
                entries=dict(self._entries),
                total_experts=len(self._entries),
                concluded_count=concluded,
                timestamp=time.time(),
            )

    def wait_for_insights(
        self,
        expert_id: str,
        timeout: float = 30.0,
        min_insights: int = 1,
    ) -> dict[str, str]:
        """
        Wait for other experts to publish insights.

        Args:
            expert_id: Waiting expert's ID
            timeout: Max seconds to wait
            min_insights: Minimum number of insights to wait for

        Returns:
            Dict of available insights (may be empty if timeout)
        """
        start = time.time()
        with self._lock:
            my_entry = self._entries.get(expert_id)
            my_layer = my_entry.layer if my_entry else 0

        while time.time() - start < timeout:
            insights = self.get_visible_insights(expert_id)
            if len(insights) >= min_insights:
                return insights

            time.sleep(0.5)

        # Return whatever is available on timeout
        return self.get_visible_insights(expert_id)

    def all_concluded(self) -> bool:
        """Check if all registered experts have concluded."""
        with self._lock:
            if not self._entries:
                return True
            return all(e.status == ExpertStatus.CONCLUDED for e in self._entries.values())

    @property
    def version(self) -> int:
        """Current board version (increments on every change)."""
        with self._lock:
            return self._version
