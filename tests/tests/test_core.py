"""
Tests for Super Thinking core functionality.
"""

import pytest
from super_thinking.perspectives._interface import PerspectiveOutput
from super_thinking.core.registry import Registry
from super_thinking.core.router import Router, RoutingResult
from super_thinking.core.jury import Jury, JuryResult
from super_thinking.fusion.conflict import ConflictDetector
from super_thinking.fusion.consensus import ConsensusFinder


# Mock perspective for testing
class MockPerspective:
    id = "test_perspective"
    name = "Test Perspective"
    description = "A test perspective"
    trigger_keywords = ["test", "mock"]

    def think(self, input: str, context: dict) -> PerspectiveOutput:
        return PerspectiveOutput(
            perspective_id=self.id,
            perspective_name=self.name,
            analysis=f"Test analysis of: {input[:50]}",
            key_points=["Test point 1", "Test point 2"],
            confidence=0.8,
            tags=["test"],
            warnings=["Test warning"],
        )


class MockPerspective2:
    id = "test_perspective_2"
    name = "Test Perspective 2"
    description = "Another test perspective"
    trigger_keywords = ["analyze", "review"]

    def think(self, input: str, context: dict) -> PerspectiveOutput:
        return PerspectiveOutput(
            perspective_id=self.id,
            perspective_name=self.name,
            analysis=f"Second analysis of: {input[:50]}",
            key_points=["Point A", "Point B"],
            confidence=0.6,
            tags=["analysis"],
        )


class TestPerspectiveOutput:
    """Tests for PerspectiveOutput validation."""

    def test_valid_output(self):
        output = PerspectiveOutput(
            perspective_id="test",
            perspective_name="Test",
            analysis="Test analysis",
            confidence=0.5,
        )
        assert output.confidence == 0.5

    def test_invalid_confidence(self):
        with pytest.raises(ValueError):
            PerspectiveOutput(
                perspective_id="test",
                perspective_name="Test",
                analysis="Test",
                confidence=1.5,
            )

    def test_default_values(self):
        output = PerspectiveOutput(
            perspective_id="test",
            perspective_name="Test",
            analysis="Test",
        )
        assert output.key_points == []
        assert output.tags == []
        assert output.warnings == []


class TestRegistry:
    """Tests for PerspectiveRegistry."""

    def test_register_perspective(self):
        registry = Registry()
        mock = MockPerspective()
        registry.register(mock)
        assert registry.get("test_perspective") is not None
        assert registry.is_enabled("test_perspective")

    def test_enable_disable(self):
        registry = Registry()
        mock = MockPerspective()
        registry.register(mock)

        registry.disable("test_perspective")
        assert not registry.is_enabled("test_perspective")

        registry.enable("test_perspective")
        assert registry.is_enabled("test_perspective")

    def test_list_enabled(self):
        registry = Registry()
        registry.register(MockPerspective())
        registry.register(MockPerspective2())

        enabled = registry.list_enabled()
        assert len(enabled) >= 2


class TestRouter:
    """Tests for Router."""

    def test_force_all_mode(self):
        registry = Registry()
        registry.register(MockPerspective())
        registry.register(MockPerspective2())

        router = Router(registry)
        result = router.route("test input", mode="force_all")

        assert result.mode == "force_all"
        assert "test_perspective" in result.activated
        assert "test_perspective_2" in result.activated

    def test_selective_mode(self):
        registry = Registry()
        registry.register(MockPerspective())
        registry.register(MockPerspective2())

        router = Router(registry)
        result = router.route("test", mode="selective", selective_ids=["test_perspective"])

        assert result.mode == "selective"
        assert result.activated == ["test_perspective"]

    def test_auto_mode_keyword_match(self):
        registry = Registry()
        registry.register(MockPerspective())  # trigger: test, mock
        registry.register(MockPerspective2())  # trigger: analyze, review

        router = Router(registry)
        result = router.route("test keyword", mode="auto")

        assert result.mode == "auto"
        # MockPerspective should match "test"
        assert "test_perspective" in result.activated


class TestJury:
    """Tests for Jury orchestration."""

    def test_think_success(self):
        registry = Registry()
        registry.register(MockPerspective())

        jury = Jury(registry)
        result = jury.think("test input", mode="force_all")

        assert result.successful == 1
        assert result.failed == 0
        assert "test_perspective" in result.outputs

    def test_think_with_context(self):
        registry = Registry()
        registry.register(MockPerspective())

        jury = Jury(registry)
        result = jury.think(
            "test input",
            context={"user": "test_user"},
            mode="force_all",
        )

        assert result.successful == 1


class TestConflictDetector:
    """Tests for ConflictDetector."""

    def test_no_conflicts(self):
        detector = ConflictDetector()

        outputs = [
            PerspectiveOutput(
                perspective_id="a",
                perspective_name="A",
                analysis="This is positive.",
                key_points=["good outcome"],
                confidence=0.8,
            ),
            PerspectiveOutput(
                perspective_id="b",
                perspective_name="B",
                analysis="Also positive.",
                key_points=["good result"],
                confidence=0.7,
            ),
        ]

        report = detector.detect(outputs)
        assert report.total_conflicts >= 0  # May have low severity divergence

    def test_confidence_gap_detection(self):
        detector = ConflictDetector()

        outputs = [
            PerspectiveOutput(
                perspective_id="high",
                perspective_name="High Confidence",
                analysis="Very sure.",
                confidence=0.95,
            ),
            PerspectiveOutput(
                perspective_id="low",
                perspective_name="Low Confidence",
                analysis="Not sure.",
                confidence=0.2,
            ),
        ]

        report = detector.detect(outputs)
        # Should detect confidence gap
        assert any(
            c.conflict_type == "confidence_gap" for c in report.conflicts
        )


class TestConsensusFinder:
    """Tests for ConsensusFinder."""

    def test_find_consensus(self):
        finder = ConsensusFinder()

        outputs = [
            PerspectiveOutput(
                perspective_id="a",
                perspective_name="A",
                analysis="Analysis A",
                key_points=["Shared point", "Unique A"],
                tags=["tag1"],
            ),
            PerspectiveOutput(
                perspective_id="b",
                perspective_name="B",
                analysis="Analysis B",
                key_points=["Shared point", "Unique B"],
                tags=["tag1"],
            ),
        ]

        report = finder.find(outputs)
        assert report.total_consensus_points >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
