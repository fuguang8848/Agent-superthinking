"""
v6 CLI Commands Package

Contains subcommands for the superthink CLI.
"""

from .debate import debate_cmd
from .consult import consult_cmd
from .list_experts import list_cmd

__all__ = ["debate_cmd", "consult_cmd", "list_cmd"]
