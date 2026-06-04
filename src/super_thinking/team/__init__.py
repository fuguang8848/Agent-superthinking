"""
SuperThinking Team Integration.

Multi-expert collaboration via shared context board.
"""

from .team_integration import ExpertPhase, ExpertContextEntry, TeamIntegration, create_team_session

__all__ = [
    "TeamIntegration",
    "ExpertPhase",
    "ExpertContextEntry",
    "create_team_session",
]
