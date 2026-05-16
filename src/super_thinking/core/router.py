"""
Router - determines which perspectives to activate based on input.

Supports three routing modes:
- auto: Match perspectives by trigger_keywords
- force_all: Activate all enabled perspectives
- selective: Use only specified perspective IDs
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from super_thinking.core.registry import Registry

logger = logging.getLogger(__name__)


@dataclass
class RoutingResult:
    """Result of routing decision."""

    activated: list[str]  # List of perspective IDs to activate
    mode: str  # auto, force_all, selective
    reason: str  # Explanation of routing decision
    scores: dict[str, float]  # Match scores for each perspective


class Router:
    """Routes input to appropriate perspectives."""

    def __init__(self, registry: Optional[Registry] = None):
        self._registry = registry or get_registry()

    def route(
        self,
        input: str,
        mode: str = "auto",
        selective_ids: Optional[list[str]] = None,
    ) -> RoutingResult:
        """Determine which perspectives to activate.

        Args:
            input: User's question or problem statement
            mode: Routing mode - "auto", "force_all", or "selective"
            selective_ids: List of perspective IDs (for selective mode)

        Returns:
            RoutingResult with activated perspectives and metadata
        """
        if mode == "force_all":
            return self._route_force_all()
        elif mode == "selective":
            return self._route_selective(selective_ids or [])
        else:
            return self._route_auto(input)

    def _route_auto(self, input: str) -> RoutingResult:
        """Auto-route based on trigger keyword matching."""
        input_lower = input.lower()
        scores: dict[str, float] = {}
        matched_keywords: dict[str, list[str]] = {}

        enabled = self._registry.list_enabled()

        for perspective in enabled:
            keywords = perspective.trigger_keywords
            if not keywords:
                scores[perspective.id] = 0.0
                continue

            # Count keyword matches
            matches = [kw for kw in keywords if kw.lower() in input_lower]
            if matches:
                # Score = matched / total keywords (normalized)
                score = len(matches) / len(keywords)
                scores[perspective.id] = score
                matched_keywords[perspective.id] = matches

        # Activate perspectives with score > 0 (at least one keyword match)
        # Or at least the top scoring ones if no matches
        activated = [pid for pid, score in scores.items() if score > 0]

        # If nothing matched, use all enabled (default behavior)
        if not activated:
            activated = [p.id for p in enabled]
            reason = "No keyword matches - using all enabled perspectives"
        else:
            matched = [
                f"{pid}({', '.join(matched_keywords[pid])})"
                for pid in activated
                if pid in matched_keywords
            ]
            reason = f"Keyword matches: {', '.join(matched)}"

        return RoutingResult(
            activated=activated,
            mode="auto",
            reason=reason,
            scores=scores,
        )

    def _route_force_all(self) -> RoutingResult:
        """Activate all enabled perspectives."""
        enabled = self._registry.list_enabled()
        activated = [p.id for p in enabled]

        return RoutingResult(
            activated=activated,
            mode="force_all",
            reason="Force all mode - activating all enabled perspectives",
            scores={pid: 1.0 for pid in activated},
        )

    def _route_selective(self, selective_ids: list[str]) -> RoutingResult:
        """Activate only specified perspectives."""
        enabled = self._registry.list_enabled()
        enabled_ids = {p.id for p in enabled}

        # Validate requested IDs
        invalid = [pid for pid in selective_ids if pid not in enabled_ids]
        if invalid:
            logger.warning(f"Unknown perspective IDs (skipping): {invalid}")

        activated = [pid for pid in selective_ids if pid in enabled_ids]

        if not activated:
            # Fallback to all enabled if none valid
            activated = list(enabled_ids)
            reason = f"No valid IDs in selection - using all enabled. Invalid: {invalid}"
        else:
            reason = f"Selective mode - activated: {activated}"

        return RoutingResult(
            activated=activated,
            mode="selective",
            reason=reason,
            scores={pid: 1.0 if pid in activated else 0.0 for pid in enabled_ids},
        )


def get_router(registry: Optional[Registry] = None) -> Router:
    """Get a Router instance."""
    return Router(registry)


def get_registry(registry: Optional[Registry] = None) -> Registry:
    """Get a Registry instance."""
    if registry is None:
        from super_thinking.core.registry import Registry as RegClass
        return RegClass()
    return registry
