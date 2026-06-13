"""
TeamIntegration - ContextBoard-based expert collaboration.

Provides layer-based expert execution where:
- Experts in layer 0 execute first and publish insights
- Experts in layer 1+ can read layer 0 insights before executing
- Each expert can see others' intermediate conclusions

Internal testing version - not exposed to regular users.

Usage:
    board = ContextBoard()
    integration = TeamIntegration(board)

    # Register experts
    integration.register_expert("morgan", layer=0)
    integration.register_expert("dalio", layer=1)
    integration.register_expert("buffett", layer=1)

    # Execute layer by layer
    integration.publish_insight("morgan", "Bridgewater: Markets are X")
    integration.publish_concluded("morgan")

    # Later layers read Morgan's insight
    insights = integration.get_board_state().insights  # includes Morgan's
"""

from __future__ import annotations

import logging
import time
from typing import Optional, Any

from super_thinking.team.context_board import (
    ContextBoard,
    ExpertStatus,
    ExpertEntry,
    BoardSnapshot,
)

logger = logging.getLogger(__name__)


class TeamIntegration:
    """
    ContextBoard-backed expert collaboration coordinator.

    Manages expert registration, insight publishing, and cross-expert
    visibility. Designed for layer-based execution where later layers
    benefit from earlier layers' insights.
    """

    def __init__(self, board: Optional[ContextBoard] = None):
        """
        Initialize TeamIntegration.

        Args:
            board: Shared ContextBoard instance.
                   Creates a new one if None.
        """
        self._board = board or ContextBoard()

    # -------------------------------------------------------------------------
    # Board access
    # -------------------------------------------------------------------------

    @property
    def board(self) -> ContextBoard:
        """The underlying ContextBoard."""
        return self._board

    # -------------------------------------------------------------------------
    # Expert management
    # -------------------------------------------------------------------------

    def register_expert(self, expert_id: str, layer: int = 0) -> ExpertEntry:
        """
        Register an expert on the board.

        Args:
            expert_id: Unique identifier for the expert
            layer: Execution layer (0 = first, higher = later)

        Returns:
            ExpertEntry for the registered expert
        """
        return self._board.register(expert_id, layer=layer)

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
            status: Collaboration status (defaults to REVIEWING)
        """
        self._board.publish_insight(expert_id, insight, status)

    def publish_concluded(
        self,
        expert_id: str,
        final_insight: Optional[str] = None,
    ) -> None:
        """
        Mark expert as concluded.

        Args:
            expert_id: Expert's ID
            final_insight: Final conclusion (overrides intermediate if given)
        """
        self._board.publish_concluded(expert_id, final_insight)

    def set_waiting(self, expert_id: str) -> None:
        """Mark expert as waiting for other experts' insights."""
        self._board.set_waiting(expert_id)

    # -------------------------------------------------------------------------
    # State queries
    # -------------------------------------------------------------------------

    def get_board_state(self) -> BoardSnapshot:
        """Get current board state snapshot."""
        return self._board.get_board_state()

    def get_insights_for(self, expert_id: str) -> dict[str, str]:
        """
        Get all visible insights for a given expert.

        Args:
            expert_id: The expert to get insights for

        Returns:
            Dict of expert_id -> insight text
        """
        return self._board.get_visible_insights(expert_id)

    def wait_for_insights(
        self,
        expert_id: str,
        timeout: float = 30.0,
        min_insights: int = 1,
    ) -> dict[str, str]:
        """
        Wait for other experts' insights to become available.

        Args:
            expert_id: Waiting expert's ID
            timeout: Max seconds to wait
            min_insights: Minimum number of insights to collect

        Returns:
            Dict of available insights (may be empty on timeout)
        """
        return self._board.wait_for_insights(expert_id, timeout, min_insights)

    def get_expert_status(self, expert_id: str) -> Optional[ExpertStatus]:
        """Get an expert's current status."""
        entry = self._board.get_entry(expert_id)
        return entry.status if entry else None

    def is_concluded(self, expert_id: str) -> bool:
        """Check if an expert has concluded."""
        return self.get_expert_status(expert_id) == ExpertStatus.CONCLUDED

    def all_concluded(self) -> bool:
        """Check if all registered experts have concluded."""
        return self._board.all_concluded()

    # -------------------------------------------------------------------------
    # Layer helpers
    # -------------------------------------------------------------------------

    def get_experts_by_layer(self) -> dict[int, list[str]]:
        """
        Group registered expert IDs by their layer.

        Returns:
            Dict mapping layer number to list of expert IDs
        """
        state = self._board.get_board_state()
        layers: dict[int, list[str]] = {}
        for expert_id, entry in state.entries.items():
            layers.setdefault(entry.layer, []).append(expert_id)
        return layers

    def get_execution_order(self) -> list[str]:
        """
        Get flattened execution order (layer by layer).

        Returns:
            List of expert IDs in execution order
        """
        by_layer = self.get_experts_by_layer()
        order = []
        for layer in sorted(by_layer.keys()):
            order.extend(by_layer[layer])
        return order
