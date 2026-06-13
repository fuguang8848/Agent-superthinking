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
    routing_recommendation: Optional[dict] = None  # Profile-aware recommendation data


class Router:
    """Routes input to appropriate perspectives with optional profile awareness."""

    def __init__(
        self,
        registry: Optional["Registry"] = None,
        profile_manager: Optional["ProfileManager"] = None,
    ):
        self._registry = registry
        self._profile_manager = profile_manager

    @property
    def _reg(self) -> "Registry":
        from super_thinking.core.registry import Registry as RegClass

        if self._registry is None:
            self._registry = RegClass()
            self._registry.discover()  # 确保专家被加载
        return self._registry

    def route(
        self,
        input: str,
        mode: str = "auto",
        selective_ids: Optional[list[str]] = None,
        user_id: Optional[str] = None,
    ) -> RoutingResult:
        """Determine which perspectives to activate.

        Args:
            input: User's question or problem statement
            mode: Routing mode - "auto", "force_all", or "selective"
            selective_ids: List of perspective IDs (for selective mode)
            user_id: Optional user ID for profile-aware routing

        Returns:
            RoutingResult with activated perspectives and metadata
        """
        # Input validation: truncate very long inputs
        if len(input) > 5000:
            input = input[:5000]
            logger.warning("Router: input truncated to 5000 chars")

        if mode == "force_all":
            return self._route_force_all()
        elif mode == "selective":
            return self._route_selective(selective_ids or [])
        else:
            return self._route_auto(input, user_id)

    def _route_auto(self, input: str, user_id: Optional[str] = None) -> RoutingResult:
        """Auto-route based on trigger keyword matching + optional profile weighting."""
        input_lower = input.lower()
        scores: dict[str, float] = {}
        matched_keywords: dict[str, list[str]] = {}

        enabled = self._reg.list_enabled()

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

        # Profile-aware weight adjustment
        recommendation = None
        if user_id and self._profile_manager is not None:
            recommendation = self._apply_profile_adjustment(
                input, user_id, scores
            )

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
            if recommendation:
                reason += f" | Profile-adjusted"

        return RoutingResult(
            activated=activated,
            mode="auto",
            reason=reason,
            scores=scores,
            routing_recommendation=recommendation,
        )

    def _apply_profile_adjustment(
        self, input: str, user_id: str, scores: dict[str, float]
    ) -> Optional[dict]:
        """Apply profile-based weight adjustment to routing scores."""
        try:
            from src.learning import ProfileManager, RoutingOptimizer

            if self._profile_manager is None:
                return None

            profile = self._profile_manager.get_profile(user_id)
            if not profile or profile.get("statistics", {}).get("total_questions", 0) == 0:
                # No profile data yet, skip adjustment
                return None

            optimizer = RoutingOptimizer(profile)
            question_type = self._profile_manager.classify_question(input)

            # Get adjusted weights from optimizer
            adjusted = optimizer.adjust_weights(question_type)

            # Boost scores for highly-weighted experts in profile
            for expert_name, weight_boost in adjusted.items():
                # Match expert name to perspective ID via trigger keywords
                for pid, score in scores.items():
                    perspective = self._reg.get(pid)
                    if perspective and hasattr(perspective, "trigger_keywords"):
                        # If expert name appears in any trigger keyword, boost that perspective
                        for kw in perspective.trigger_keywords:
                            if expert_name in kw or kw in expert_name:
                                scores[pid] = min(1.0, scores[pid] + weight_boost * 0.5)

            # Re-sort activated by adjusted scores
            return {
                "question_type": question_type,
                "adjusted_weights": adjusted,
                "profile_applied": True,
            }
        except Exception:
            return None

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


def get_router(
    registry: Optional[Registry] = None,
    profile_manager: Optional[Any] = None,
) -> Router:
    """Get a Router instance with optional profile manager."""
    return Router(registry=registry, profile_manager=profile_manager)


def get_registry(registry: Optional[Registry] = None) -> Registry:
    """Get a Registry instance."""
    if registry is None:
        from super_thinking.core.registry import Registry as RegClass
        return RegClass()
    return registry
