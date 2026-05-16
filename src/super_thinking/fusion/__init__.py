"""Fusion layer for integrating multiple perspectives."""

from super_thinking.fusion.conflict import ConflictDetector
from super_thinking.fusion.consensus import ConsensusFinder
from super_thinking.fusion.formatter import Formatter

__all__ = ["ConflictDetector", "ConsensusFinder", "Formatter"]
