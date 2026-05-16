"""
Consensus finder - extracts common conclusions from multiple perspectives.

Identifies:
- Strong consensus points (supported by multiple perspectives)
- Weak consensus (similar themes but different conclusions)
- Unique insights (only one perspective identified)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from super_thinking.perspectives._interface import PerspectiveOutput


@dataclass
class ConsensusPoint:
    """A point of consensus among perspectives."""

    content: str  # The consensus content
    support_count: int  # Number of perspectives supporting this
    supporting_perspectives: list[str]  # IDs of supporting perspectives
    consensus_type: str  # "strong", "moderate", "weak"
    source_key_points: list[str]  # Original key points that contributed


@dataclass
class ConsensusReport:
    """Report of consensus findings."""

    strong_consensus: list[ConsensusPoint]  # Supported by 3+ perspectives
    moderate_consensus: list[ConsensusPoint]  # Supported by 2 perspectives
    weak_consensus: list[ConsensusPoint]  # Thematically similar but not identical
    unique_insights: list[ConsensusPoint]  # Only one perspective identified
    total_consensus_points: int
    summary: str


class ConsensusFinder:
    """Finds consensus and unique insights across perspectives."""

    # Theme groups for semantic similarity
    THEME_GROUPS = {
        "risk": ["risk", "danger", "threat", "uncertainty", "volatility"],
        "opportunity": ["opportunity", "potential", "growth", "benefit", "advantage"],
        "cost": ["cost", "expensive", "price", "investment", "resource"],
        "quality": ["quality", "excellence", "superior", "better", "improved"],
        "speed": ["fast", "quick", "speed", "rapid", "efficient"],
        "safety": ["safe", "security", "reliable", "stable", "secure"],
    }

    def find(self, outputs: list[PerspectiveOutput]) -> ConsensusReport:
        """
        Analyze outputs and find consensus points.

        Args:
            outputs: List of PerspectiveOutputs from different perspectives

        Returns:
            ConsensusReport with consensus and unique insights
        """
        if not outputs:
            return ConsensusReport(
                strong_consensus=[],
                moderate_consensus=[],
                weak_consensus=[],
                unique_insights=[],
                total_consensus_points=0,
                summary="No perspectives to compare.",
            )

        all_key_points: list[tuple[str, str, PerspectiveOutput]] = []
        for out in outputs:
            for kp in out.key_points:
                all_key_points.append((kp, self._normalize_text(kp), out))

        # Find strong consensus (exact or near-duplicate key points)
        strong = self._find_exact_matches(all_key_points)

        # Find theme-based consensus
        moderate = self._find_theme_matches(all_key_points, strong)

        # Find weak consensus (similar themes)
        weak = self._find_weak_consensus(all_key_points, strong + moderate)

        # Identify unique insights
        used_points = set()
        for cp in strong + moderate + weak:
            for kp in cp.source_key_points:
                used_points.add(kp)

        unique = []
        for out in outputs:
            for kp in out.key_points:
                if kp not in used_points:
                    unique.append(ConsensusPoint(
                        content=kp,
                        support_count=1,
                        supporting_perspectives=[out.perspective_id],
                        consensus_type="unique",
                        source_key_points=[kp],
                    ))
                    used_points.add(kp)

        # Sort by support count
        strong.sort(key=lambda x: x.support_count, reverse=True)
        moderate.sort(key=lambda x: x.support_count, reverse=True)
        weak.sort(key=lambda x: x.support_count, reverse=True)
        unique.sort(key=lambda x: x.supporting_perspectives[0])

        total = len(strong) + len(moderate) + len(weak) + len(unique)

        return ConsensusReport(
            strong_consensus=strong,
            moderate_consensus=moderate,
            weak_consensus=weak,
            unique_insights=unique,
            total_consensus_points=total,
            summary=self._generate_summary(outputs, strong, moderate),
        )

    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison."""
        return text.lower().strip()

    def _find_exact_matches(
        self, key_points: list[tuple[str, str, PerspectiveOutput]]
    ) -> list[ConsensusPoint]:
        """Find exact or near-duplicate key points."""
        seen: dict[str, list[tuple[str, PerspectiveOutput]]] = {}

        for original, normalized, out in key_points:
            # Use first 50 chars as rough fingerprint
            fingerprint = normalized[:50]
            if fingerprint not in seen:
                seen[fingerprint] = []
            seen[fingerprint].append((original, out))

        results = []
        for fingerprint, items in seen.items():
            if len(items) >= 2:
                results.append(ConsensusPoint(
                    content=items[0][0],  # Use first occurrence as canonical
                    support_count=len(items),
                    supporting_perspectives=[out.perspective_id for _, out in items],
                    consensus_type="strong" if len(items) >= 3 else "moderate",
                    source_key_points=[orig for orig, _ in items],
                ))

        return results

    def _find_theme_matches(
        self,
        key_points: list[tuple[str, str, PerspectiveOutput]],
        exclude: list[ConsensusPoint],
    ) -> list[ConsensusPoint]:
        """Find key points that share themes."""
        results = []
        used = set()

        # Build theme index
        for theme, keywords in self.THEME_GROUPS.items():
            theme_points: list[tuple[str, PerspectiveOutput]] = []
            for original, normalized, out in key_points:
                if any(kw in normalized for kw in keywords):
                    theme_points.append((original, out))

            if len(theme_points) >= 2:
                # Group by perspective
                by_perspective: dict[str, list[str]] = {}
                for original, out in theme_points:
                    pid = out.perspective_id
                    if pid not in by_perspective:
                        by_perspective[pid] = []
                    by_perspective[pid].append(original)

                if len(by_perspective) >= 2:
                    results.append(ConsensusPoint(
                        content=f"[{theme.upper()}] Shared theme across perspectives",
                        support_count=len(by_perspective),
                        supporting_perspectives=list(by_perspective.keys()),
                        consensus_type="moderate",
                        source_key_points=[orig for orig, _ in theme_points],
                    ))
                    for orig, _ in theme_points:
                        used.add(orig)

        return results

    def _find_weak_consensus(
        self,
        key_points: list[tuple[str, str, PerspectiveOutput]],
        exclude: list[ConsensusPoint],
    ) -> list[ConsensusPoint]:
        """Find loosely related insights."""
        # For weak consensus, we look for shared high-level tags
        results = []

        # Group by tags
        tag_to_points: dict[str, list[tuple[str, PerspectiveOutput]]] = {}
        for original, normalized, out in key_points:
            for tag in out.tags:
                if tag not in tag_to_points:
                    tag_to_points[tag] = []
                tag_to_points[tag].append((original, out))

        for tag, items in tag_to_points.items():
            if len(items) >= 2:
                pids = set(out.perspective_id for _, out in items)
                if len(pids) >= 2:
                    results.append(ConsensusPoint(
                        content=f"[TAG: {tag}] Related through categorization",
                        support_count=len(pids),
                        supporting_perspectives=list(pids),
                        consensus_type="weak",
                        source_key_points=[orig for orig, _ in items],
                    ))

        return results

    def _generate_summary(
        self,
        outputs: list[PerspectiveOutput],
        strong: list[ConsensusPoint],
        moderate: list[ConsensusPoint],
    ) -> str:
        """Generate human-readable summary."""
        n = len(outputs)

        if not strong and not moderate:
            return f"No consensus found among {n} perspectives. Each offers unique insights."

        strong_count = sum(cp.support_count for cp in strong)
        moderate_count = sum(cp.support_count for cp in moderate)

        return (
            f"Found {len(strong)} strong and {len(moderate)} moderate consensus points. "
            f"{strong_count} total supporting votes from {n} perspectives."
        )
