"""
Conflict detection - identifies contradictions between perspectives.

Analyzes multiple PerspectiveOutputs to detect:
- Direct contradictions (opposite conclusions)
- Significant disagreements in confidence
- Diverging key points
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from super_thinking.perspectives._interface import PerspectiveOutput


@dataclass
class Conflict:
    """Represents a conflict between perspectives."""

    perspective_a: str  # First perspective ID
    perspective_b: str  # Second perspective ID
    conflict_type: str  # "contradiction", "confidence_gap", "divergence"
    severity: str  # "high", "medium", "low"
    description: str
    detail: str


@dataclass
class ConflictReport:
    """Report of all detected conflicts."""

    conflicts: list[Conflict]
    total_conflicts: int
    high_severity: int
    medium_severity: int
    low_severity: int
    summary: str


class ConflictDetector:
    """Detects conflicts between perspective outputs."""

    # Keywords that indicate opposite positions
    CONTRADICTION_KEYWORDS = [
        ("yes", "no"),
        ("good", "bad"),
        ("should", "should not"),
        ("increase", "decrease"),
        ("positive", "negative"),
        ("support", "oppose"),
        ("agree", "disagree"),
        ("enable", "disable"),
        ("invest", "divest"),
        ("expand", "contract"),
    ]

    def detect(self, outputs: list[PerspectiveOutput]) -> ConflictReport:
        """
        Analyze outputs and detect conflicts.

        Args:
            outputs: List of PerspectiveOutputs from different perspectives

        Returns:
            ConflictReport with all detected conflicts
        """
        conflicts: list[Conflict] = []

        if len(outputs) < 2:
            return ConflictReport(
                conflicts=[],
                total_conflicts=0,
                high_severity=0,
                medium_severity=0,
                low_severity=0,
                summary="Not enough perspectives to detect conflicts",
            )

        # Check for direct contradictions in key points
        conflicts.extend(self._check_contradictions(outputs))

        # Check for confidence gaps
        conflicts.extend(self._check_confidence_gaps(outputs))

        # Check for conclusion divergence
        conflicts.extend(self._check_divergence(outputs))

        # Count severity levels
        high = sum(1 for c in conflicts if c.severity == "high")
        medium = sum(1 for c in conflicts if c.severity == "medium")
        low = sum(1 for c in conflicts if c.severity == "low")

        # Generate summary
        summary = self._generate_summary(conflicts, len(outputs))

        return ConflictReport(
            conflicts=conflicts,
            total_conflicts=len(conflicts),
            high_severity=high,
            medium_severity=medium,
            low_severity=low,
            summary=summary,
        )

    def _check_contradictions(self, outputs: list[PerspectiveOutput]) -> list[Conflict]:
        """Check for direct keyword contradictions in key points."""
        conflicts = []

        for i, out_a in enumerate(outputs):
            for out_b in outputs[i + 1:]:
                for kw_a, kw_b in self.CONTRADICTION_KEYWORDS:
                    # Check if out_a has keyword A and out_b has keyword B (or vice versa)
                    a_has_a = self._contains_keyword(out_a.key_points, kw_a)
                    a_has_b = self._contains_keyword(out_a.key_points, kw_b)
                    b_has_a = self._contains_keyword(out_b.key_points, kw_a)
                    b_has_b = self._contains_keyword(out_b.key_points, kw_b)

                    # Direct contradiction: A has kw_a, B has kw_b, and vice versa
                    if (a_has_a and b_has_b) and (b_has_a and a_has_b):
                        conflicts.append(Conflict(
                            perspective_a=out_a.perspective_id,
                            perspective_b=out_b.perspective_id,
                            conflict_type="contradiction",
                            severity="high",
                            description=f"Contradictory positions on: {kw_a} vs {kw_b}",
                            detail=f"'{out_a.perspective_name}' supports {kw_a}, "
                                   f"while '{out_b.perspective_name}' supports {kw_b}",
                        ))

        return conflicts

    def _contains_keyword(self, points: list[str], keyword: str) -> bool:
        """Check if any point contains the keyword."""
        keyword_lower = keyword.lower()
        return any(keyword_lower in point.lower() for point in points)

    def _check_confidence_gaps(self, outputs: list[PerspectiveOutput]) -> list[Conflict]:
        """Check for significant confidence level differences."""
        conflicts = []

        for i, out_a in enumerate(outputs):
            for out_b in outputs[i + 1:]:
                gap = abs(out_a.confidence - out_b.confidence)

                if gap >= 0.6:  # Very different confidence
                    severity = "high" if gap >= 0.8 else "medium"
                    conflicts.append(Conflict(
                        perspective_a=out_a.perspective_id,
                        perspective_b=out_b.perspective_id,
                        conflict_type="confidence_gap",
                        severity=severity,
                        description=f"Confidence gap of {gap:.1f}",
                        detail=f"'{out_a.perspective_name}' confidence: {out_a.confidence:.2f}, "
                               f"'{out_b.perspective_name}' confidence: {out_b.confidence:.2f}",
                    ))

        return conflicts

    def _check_divergence(self, outputs: list[PerspectiveOutput]) -> list[Conflict]:
        """Check for overall conclusion divergence."""
        conflicts = []

        # Compare main analysis conclusions
        for i, out_a in enumerate(outputs):
            for out_b in outputs[i + 1:]:
                # Extract first sentence as "conclusion"
                conclusion_a = self._extract_conclusion(out_a.analysis)
                conclusion_b = self._extract_conclusion(out_b.analysis)

                # Simple heuristic: check for opposite sentiment markers
                markers_a = self._get_sentiment_markers(conclusion_a)
                markers_b = self._get_sentiment_markers(conclusion_b)

                # If they have opposing sentiment markers
                if markers_a and markers_b and markers_a != markers_b:
                    if all(m in conclusion_b.lower() for m in markers_a) == False:
                        continue  # Not actually opposite
                    conflicts.append(Conflict(
                        perspective_a=out_a.perspective_id,
                        perspective_b=out_b.perspective_id,
                        conflict_type="divergence",
                        severity="low",
                        description="Divergent conclusions detected",
                        detail=f"'{out_a.perspective_name}': {conclusion_a[:100]}... "
                               f"vs '{out_b.perspective_name}': {conclusion_b[:100]}...",
                    ))

        return conflicts

    def _extract_conclusion(self, analysis: str) -> str:
        """Extract the first sentence as the main conclusion."""
        sentences = analysis.split("。")
        return sentences[0].strip() if sentences else analysis[:200]

    def _get_sentiment_markers(self, text: str) -> tuple[str, ...]:
        """Get sentiment markers from text."""
        text_lower = text.lower()
        positive = ["positive", "good", "support", "agree", "should", "benefit"]
        negative = ["negative", "bad", "oppose", "disagree", "should not", "risk"]

        if any(m in text_lower for m in positive):
            return tuple(m for m in positive if m in text_lower)
        if any(m in text_lower for m in negative):
            return tuple(m for m in negative if m in text_lower)
        return ()

    def _generate_summary(self, conflicts: list[Conflict], total_perspectives: int) -> str:
        """Generate a human-readable summary."""
        if not conflicts:
            return f"No significant conflicts detected among {total_perspectives} perspectives."

        high = sum(1 for c in conflicts if c.severity == "high")
        medium = sum(1 for c in conflicts if c.severity == "medium")

        if high > 0:
            return f"⚠️ HIGH ALERT: {high} critical contradictions found. "
        elif medium > 0:
            return f"⚡ {medium} moderate disagreements detected."
        else:
            return f"Minor divergences noted among {total_perspectives} perspectives."
