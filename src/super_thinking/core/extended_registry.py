"""
Extended Registry that discovers both Python perspectives and SKILL.md perspectives.

SKILL.md perspectives are loaded from the Agent-superthinking/experts/ directory,
enabling domain experts to be defined as markdown files without writing Python code.
"""

from __future__ import annotations

import importlib
import sys
import logging
from pathlib import Path
from typing import Optional

from super_thinking.core.registry import Registry as BaseRegistry
from super_thinking.perspectives._interface import Perspective

logger = logging.getLogger(__name__)


class ExtendedRegistry(BaseRegistry):
    """
    Extended registry that discovers both Python perspectives and SKILL.md perspectives.
    
    SKILL.md perspectives are defined in Agent-superthinking/experts/ directory
    with the following structure:
    
        experts/
        ├── methods/
        │   ├── bayesian-perspective/SKILL.md
        │   ├── complexity-perspective/SKILL.md
        │   └── ...
        ├── frameworks/
        │   ├── gametheory-perspective/SKILL.md
        │   └── ...
        ├── people/
        │   ├── philosophy/socrates-perspective/SKILL.md
        │   └── ...
        └── ...
    """
    
    def __init__(self, config_path=None, experts_root: Optional[Path] = None):
        super().__init__(config_path)
        
        # Find the Agent-superthinking root (src/ is at Agent-superthinking/src/)
        # __file__ = .../Agent-superthinking/src/super_thinking/core/extended_registry.py
        src_root = Path(__file__).parent.parent.parent  # = Agent-superthinking/src/
        self._experts_root = experts_root or (src_root.parent / "experts")
        
        self._skill_perspectives_loaded = False
    
    def discover(self, include_skill_perspectives: bool = True) -> None:
        """
        Discover perspectives from both Python modules and SKILL.md files.
        
        Args:
            include_skill_perspectives: Whether to also discover SKILL.md perspectives
        """
        # First, do the standard Python perspective discovery
        super().discover()
        
        # Then discover SKILL.md perspectives
        if include_skill_perspectives and not self._skill_perspectives_loaded:
            self._discover_skill_perspectives()
            self._skill_perspectives_loaded = True
    
    def _discover_skill_perspectives(self) -> None:
        """Scan experts/ directory and load all SKILL.md perspectives."""
        if not self._experts_root.exists():
            logger.info(f"Experts directory not found: {self._experts_root}")
            return
        
        try:
            from super_thinking.perspectives.skill_perspective import load_skill_perspectives
        except ImportError as e:
            logger.warning(f"Could not import skill_perspective module: {e}")
            return
        
        try:
            perspectives = load_skill_perspectives(self._experts_root)
            logger.info(f"Found {len(perspectives)} SKILL.md perspectives")
            
            for perspective in perspectives:
                # Validate basic interface
                if not hasattr(perspective, 'id') or not hasattr(perspective, 'think'):
                    logger.warning(f"SKILL.md perspective missing required interface: {perspective}")
                    continue
                
                # Check if already registered (avoid duplicates with Python perspectives)
                if perspective.id in self._perspectives:
                    logger.info(f"Skipping duplicate perspective: {perspective.id} (already registered as Python perspective)")
                    continue
                
                self._perspectives[perspective.id] = perspective
                if perspective.id not in self._enabled:
                    self._enabled.add(perspective.id)
                logger.info(f"Loaded SKILL.md perspective: {perspective.id}")
                
        except Exception as e:
            logger.warning(f"Failed to discover SKILL.md perspectives: {e}")


def get_extended_registry(experts_root: Optional[Path] = None) -> ExtendedRegistry:
    """Get or create an extended registry instance."""
    return ExtendedRegistry(experts_root=experts_root)
