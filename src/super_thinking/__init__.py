"""
Super Thinking - Jury of Experts Thinking System

A multi-perspective analysis system that leverages multiple expert viewpoints
to provide comprehensive, balanced thinking on complex problems.
"""

__version__ = "0.1.0"

from super_thinking.core.registry import PerspectiveRegistry
from super_thinking.core.router import Router
from super_thinking.core.jury import Jury
from super_thinking.fusion.formatter import Formatter

__all__ = [
    "PerspectiveRegistry",
    "Router",
    "Jury",
    "Formatter",
]
