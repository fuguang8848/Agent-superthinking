"""
Team collaboration module for ContextBoard-based expert coordination.

Internal testing version - not exposed to regular users.

Classes:
- ContextBoard: Shared board for expert insights and status
- TeamIntegration: Coordination layer for board-based expert execution

Usage:
    from super_thinking.team import ContextBoard, TeamIntegration

    board = ContextBoard()
    integration = TeamIntegration(board)

    # Register and execute
    integration.register_expert("morgan", layer=0)
    integration.publish_insight("morgan", "Markets are X")
    integration.publish_concluded("morgan")

    # Read insights
    insights = integration.get_insights_for("dalio")
"""

from super_thinking.team.context_board import (
    ContextBoard,
    ExpertStatus,
    ExpertEntry,
    BoardSnapshot,
)
from super_thinking.team.team_integration import TeamIntegration

__all__ = [
    "ContextBoard",
    "ExpertStatus",
    "ExpertEntry",
    "BoardSnapshot",
    "TeamIntegration",
]
