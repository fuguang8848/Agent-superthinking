"""
Dynamic registry for perspective modules.

Automatically discovers and loads perspectives from the perspectives/ directory.
Validates interface compliance and provides enable/disable functionality.
Persists configuration to config.yaml.
"""

from __future__ import annotations

import importlib
import sys
import logging
from pathlib import Path
from typing import Optional
import yaml

from super_thinking.perspectives._interface import Perspective

logger = logging.getLogger(__name__)


class Registry:
    """Dynamic perspective registry with auto-discovery."""

    def __init__(self, config_path: Optional[Path] = None):
        self._perspectives: dict[str, Perspective] = {}
        self._enabled: set[str] = set()
        self._package_root = Path(__file__).parent.parent
        self._config_path = config_path or self._get_default_config_path()
        self._load_config()

    def _get_default_config_path(self) -> Path:
        """Get the default config.yaml path."""
        return self._package_root.parent.parent / "config.yaml"

    def _load_config(self) -> None:
        """Load configuration from config.yaml."""
        if self._config_path.exists():
            try:
                with open(self._config_path, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f) or {}
                self._enabled = set(config.get("enabled_perspectives", []))
            except Exception as e:
                logger.warning(f"Failed to load config: {e}. Using defaults.")
                self._enabled = set()
        else:
            self._enabled = set()

    def _save_config(self) -> None:
        """Persist enabled perspectives to config.yaml."""
        try:
            self._config_path.parent.mkdir(parents=True, exist_ok=True)
            config = {"enabled_perspectives": sorted(list(self._enabled))}
            with open(self._config_path, "w", encoding="utf-8") as f:
                yaml.dump(config, f, allow_unicode=True)
        except Exception as e:
            logger.warning(f"Failed to save config: {e}")

    def _validate_perspective(self, perspective: Perspective, module_name: str) -> bool:
        """Validate that a perspective implements the required interface."""
        required_attrs = ["id", "name", "description", "trigger_keywords", "think"]
        missing = []
        for attr in required_attrs:
            try:
                value = getattr(perspective, attr, None)
                if value is None:
                    missing.append(attr)
            except (AttributeError, TypeError):
                missing.append(attr)

        if missing:
            logger.warning(
                f"Perspective '{module_name}' missing required attributes: {missing}"
            )
            return False

        try:
            trigger_keywords = getattr(perspective, "trigger_keywords")
            if not isinstance(trigger_keywords, list):
                logger.warning(
                    f"Perspective '{module_name}.trigger_keywords' must be a list"
                )
                return False
        except (AttributeError, TypeError):
            logger.warning(
                f"Perspective '{module_name}.trigger_keywords' must be a list"
            )
            return False

        return True

    def discover(self) -> None:
        """Scan perspectives/ directory and auto-load valid modules."""
        perspectives_dir = self._package_root / "perspectives"

        if not perspectives_dir.exists():
            logger.info(f"Perspectives directory not found: {perspectives_dir}")
            return

        for py_file in perspectives_dir.glob("*.py"):
            if py_file.name.startswith("_"):
                continue

            module_name = py_file.stem

            # Import the module
            try:
                # Handle both package import and direct execution
                if str(perspectives_dir.parent) not in sys.path:
                    sys.path.insert(0, str(perspectives_dir.parent))

                module = importlib.import_module(f"super_thinking.perspectives.{module_name}")

                # Track which perspective IDs we've already processed to avoid duplicates
                processed_ids: set[str] = set()

                # Find perspective classes and instantiate exactly once
                for attr_name in dir(module):
                    if attr_name.startswith("_"):
                        continue
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and attr is not Perspective:
                        # Skip if it doesn't look like a perspective (no 'think' method)
                        if not hasattr(attr, 'think'):
                            continue
                        try:
                            # Instantiate and validate once
                            instance = attr()
                            if self._validate_perspective(instance, module_name):
                                if instance.id not in processed_ids:
                                    self._perspectives[instance.id] = instance
                                    if instance.id not in self._enabled:
                                        self._enabled.add(instance.id)
                                    processed_ids.add(instance.id)
                                    logger.info(f"Loaded perspective: {instance.id}")
                        except TypeError:
                            # Not instantiable, skip
                            pass

                # Also check for already-instantiated perspective objects (singletons)
                for attr_name in dir(module):
                    if attr_name.startswith("_"):
                        continue
                    attr = getattr(module, attr_name)
                    # Skip if it's a class (already handled above)
                    if isinstance(attr, type):
                        continue
                    # Skip primitives and other non-perspective objects
                    if not hasattr(attr, 'think'):
                        continue
                    if self._validate_perspective(attr, module_name):
                        if attr.id not in processed_ids:
                            self._perspectives[attr.id] = attr
                            if attr.id not in self._enabled:
                                self._enabled.add(attr.id)
                            processed_ids.add(attr.id)
                            logger.info(f"Loaded perspective: {attr.id}")

            except Exception as e:
                logger.warning(f"Failed to load perspective '{module_name}': {e}")

    def register(self, perspective: Perspective) -> None:
        """Manually register a perspective instance."""
        if not self._validate_perspective(perspective, perspective.id):
            raise ValueError(f"Perspective '{perspective.id}' does not implement required interface")

        self._perspectives[perspective.id] = perspective
        self._enabled.add(perspective.id)
        self._save_config()

    def unregister(self, perspective_id: str) -> None:
        """Remove a perspective from the registry."""
        self._perspectives.pop(perspective_id, None)
        self._enabled.discard(perspective_id)
        self._save_config()

    def enable(self, perspective_id: str) -> bool:
        """Enable a perspective by ID."""
        if perspective_id not in self._perspectives:
            logger.warning(f"Cannot enable unknown perspective: {perspective_id}")
            return False
        self._enabled.add(perspective_id)
        self._save_config()
        return True

    def disable(self, perspective_id: str) -> bool:
        """Disable a perspective by ID."""
        self._enabled.discard(perspective_id)
        self._save_config()
        return True

    def is_enabled(self, perspective_id: str) -> bool:
        """Check if a perspective is currently enabled."""
        return perspective_id in self._enabled

    def list_all(self) -> list[Perspective]:
        """List all registered perspectives."""
        return list(self._perspectives.values())

    def list_enabled(self) -> list[Perspective]:
        """List all currently enabled perspectives."""
        return [p for p in self._perspectives.values() if p.id in self._enabled]

    def get(self, perspective_id: str) -> Optional[Perspective]:
        """Get a specific perspective by ID."""
        return self._perspectives.get(perspective_id)


# Alias for backwards compatibility
PerspectiveRegistry = Registry


def get_registry(config_path: Optional[Path] = None) -> Registry:
    """Get or create the singleton registry instance."""
    return Registry(config_path)
