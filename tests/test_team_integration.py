"""
Tests for ContextBoard and TeamIntegration.

Internal testing version - not exposed to regular users.
"""

import pytest
import threading
import time

from super_thinking.team.context_board import (
    ContextBoard,
    ExpertStatus,
    ExpertEntry,
    BoardSnapshot,
)
from super_thinking.team.team_integration import TeamIntegration
from super_thinking.core.jury import Jury
from super_thinking.core.registry import Registry
from super_thinking.perspectives._interface import PerspectiveOutput


# ---------------------------------------------------------------------------
# Mock perspectives for testing
# ---------------------------------------------------------------------------


class MockPerspective:
    """Simple mock perspective for testing."""

    id = "mock_perspective"
    name = "Mock Perspective"
    description = "A mock perspective for testing"
    trigger_keywords = ["test", "mock"]

    def think(self, input: str, context: dict) -> PerspectiveOutput:
        # If board insights are present, incorporate them
        board_insights = context.get("_board_insights", {})
        extra = ""
        if board_insights:
            other_ids = list(board_insights.keys())
            extra = f" [saw insights from: {other_ids}]"

        return PerspectiveOutput(
            perspective_id=self.id,
            perspective_name=self.name,
            analysis=f"Mock analysis of: {input[:50]}{extra}",
            key_points=["Mock point 1", "Mock point 2"],
            confidence=0.8,
            tags=["test"],
            warnings=["Mock warning"],
        )


class MockPerspective2:
    """Second mock perspective for testing."""

    id = "mock_perspective_2"
    name = "Mock Perspective 2"
    description = "Another mock perspective for testing"
    trigger_keywords = ["analyze", "review"]

    def think(self, input: str, context: dict) -> PerspectiveOutput:
        return PerspectiveOutput(
            perspective_id=self.id,
            perspective_name=self.name,
            analysis=f"Second mock analysis of: {input[:50]}",
            key_points=["Point A", "Point B"],
            confidence=0.6,
            tags=["analysis"],
        )


# ---------------------------------------------------------------------------
# ContextBoard tests
# ---------------------------------------------------------------------------


class TestContextBoardBasics:
    """Basic ContextBoard functionality tests."""

    def test_register_expert(self):
        board = ContextBoard()
        entry = board.register("expert_a", layer=0)

        assert entry.expert_id == "expert_a"
        assert entry.layer == 0
        assert entry.status == ExpertStatus.THINKING
        assert entry.insight is None

    def test_register_multiple_experts(self):
        board = ContextBoard()
        board.register("a", layer=0)
        board.register("b", layer=0)
        board.register("c", layer=1)

        state = board.get_board_state()
        assert state.total_experts == 3

    def test_publish_insight(self):
        board = ContextBoard()
        board.register("expert_a")

        board.publish_insight("expert_a", "Found X", ExpertStatus.REVIEWING)

        entry = board.get_entry("expert_a")
        assert entry.insight == "Found X"
        assert entry.status == ExpertStatus.REVIEWING

    def test_publish_concluded(self):
        board = ContextBoard()
        board.register("expert_a")

        board.publish_concluded("expert_a", "Final conclusion")

        entry = board.get_entry("expert_a")
        assert entry.insight == "Final conclusion"
        assert entry.status == ExpertStatus.CONCLUDED

    def test_publish_insight_auto_register(self):
        """Can publish insight without prior registration."""
        board = ContextBoard()
        board.publish_insight("new_expert", "Hello", ExpertStatus.THINKING)

        entry = board.get_entry("new_expert")
        assert entry is not None
        assert entry.insight == "Hello"

    def test_get_visible_insights_excludes_self(self):
        board = ContextBoard()
        board.register("a", layer=0)
        board.publish_insight("a", "Insight A", ExpertStatus.CONCLUDED)

        insights = board.get_visible_insights("a", exclude_self=True)
        assert "a" not in insights

    def test_get_visible_insights_includes_concluded(self):
        board = ContextBoard()
        board.register("a", layer=0)
        board.register("b", layer=1)

        board.publish_insight("a", "A's insight", ExpertStatus.CONCLUDED)
        board.publish_insight("b", "B's insight", ExpertStatus.REVIEWING)

        # CONCLUDED insights are visible
        insights = board.get_visible_insights("b", exclude_self=True)
        assert "a" in insights

        # REVIEWING insights are also visible
        assert "b" not in insights  # excluded self

    def test_get_visible_insights_respects_layer(self):
        """Lower layer insights are visible to higher layer, but not vice versa."""
        board = ContextBoard()
        board.register("a", layer=0)
        board.register("b", layer=1)

        board.publish_insight("a", "A insight", ExpertStatus.CONCLUDED)

        # B should see A's insight
        insights = board.get_visible_insights("b")
        assert "a" in insights

    def test_all_concluded_empty(self):
        board = ContextBoard()
        assert board.all_concluded() is True

    def test_all_concluded_partial(self):
        board = ContextBoard()
        board.register("a")
        board.register("b")
        board.publish_concluded("a")

        assert board.all_concluded() is False

    def test_all_concluded_all_done(self):
        board = ContextBoard()
        board.register("a")
        board.register("b")
        board.publish_concluded("a")
        board.publish_concluded("b")

        assert board.all_concluded() is True

    def test_version_increments(self):
        board = ContextBoard()
        v0 = board.version

        board.register("a")
        assert board.version > v0

        v1 = board.version
        board.publish_insight("a", "test")
        assert board.version > v1


class TestContextBoardSnapshot:
    """BoardSnapshot tests."""

    def test_snapshot_contains_expected_fields(self):
        board = ContextBoard()
        board.register("a", layer=0)
        board.publish_insight("a", "X", ExpertStatus.CONCLUDED)

        snap = board.get_board_state()

        assert snap.total_experts == 1
        assert snap.concluded_count == 1
        assert snap.entries["a"].insight == "X"
        assert "a" in snap.entries


class TestContextBoardThreadSafety:
    """Basic thread safety smoke test."""

    def test_concurrent_register(self):
        board = ContextBoard()
        ids = [f"expert_{i}" for i in range(10)]

        def register_batch(expert_ids):
            for eid in expert_ids:
                board.register(eid, layer=0)

        threads = [
            threading.Thread(target=register_batch, args=(ids[i::3],))
            for i in range(3)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        state = board.get_board_state()
        assert state.total_experts == 10


# ---------------------------------------------------------------------------
# TeamIntegration tests
# ---------------------------------------------------------------------------


class TestTeamIntegrationBasics:
    """Basic TeamIntegration functionality tests."""

    def test_register_expert(self):
        integration = TeamIntegration()
        entry = integration.register_expert("buffett", layer=0)

        assert entry.expert_id == "buffett"
        assert entry.layer == 0

    def test_publish_insight_via_integration(self):
        integration = TeamIntegration()
        integration.register_expert("morgan", layer=0)
        integration.publish_insight("morgan", "Bridgewater sees risk X")

        status = integration.get_expert_status("morgan")
        assert status == ExpertStatus.REVIEWING

    def test_publish_concluded_via_integration(self):
        integration = TeamIntegration()
        integration.register_expert("dalio")
        integration.publish_concluded("dalio", "Final: Diversify")

        assert integration.is_concluded("dalio")

    def test_get_insights_for(self):
        board = ContextBoard()
        integration = TeamIntegration(board)

        integration.register_expert("a", layer=0)
        integration.register_expert("b", layer=1)
        integration.publish_insight("a", "A says X", ExpertStatus.CONCLUDED)

        insights = integration.get_insights_for("b")
        assert "a" in insights
        assert insights["a"] == "A says X"

    def test_get_experts_by_layer(self):
        integration = TeamIntegration()
        integration.register_expert("a", layer=0)
        integration.register_expert("b", layer=0)
        integration.register_expert("c", layer=1)
        integration.register_expert("d", layer=2)

        by_layer = integration.get_experts_by_layer()

        assert sorted(by_layer[0]) == ["a", "b"]
        assert by_layer[1] == ["c"]
        assert by_layer[2] == ["d"]

    def test_get_execution_order(self):
        integration = TeamIntegration()
        integration.register_expert("c", layer=1)
        integration.register_expert("a", layer=0)
        integration.register_expert("b", layer=0)
        integration.register_expert("d", layer=2)

        order = integration.get_execution_order()

        assert order.index("a") < order.index("c")
        assert order.index("c") < order.index("d")
        assert order.index("a") < order.index("b")

    def test_all_concluded(self):
        integration = TeamIntegration()
        integration.register_expert("a")
        integration.register_expert("b")

        assert not integration.all_concluded()

        integration.publish_concluded("a")
        assert not integration.all_concluded()

        integration.publish_concluded("b")
        assert integration.all_concluded()


# ---------------------------------------------------------------------------
# Jury with Board tests
# ---------------------------------------------------------------------------


class TestJuryThinkWithBoard:
    """Tests for Jury.think_with_board()."""

    def test_think_with_board_basic(self):
        """Basic execution with board - single layer."""
        registry = Registry()
        registry.register(MockPerspective())

        jury = Jury(registry)
        result = jury.think_with_board(
            "test input",
            mode="force_all",
        )

        assert result.successful == 1
        assert "mock_perspective" in result.outputs
        assert result.outputs["mock_perspective"].analysis.startswith("Mock analysis")

    def test_think_with_board_receives_insights(self):
        """Experts should receive board insights in context."""
        registry = Registry()
        registry.register(MockPerspective())

        # Two mock perspectives in different layers
        jury = Jury(registry)
        board = ContextBoard()

        # First, manually conclude MockPerspective with specific text
        board.register("mock_perspective", layer=0)
        board.publish_concluded("mock_perspective", "Pre-existing insight from mock_perspective")

        # Second perspective in layer 1
        layers = {"mock_perspective": 0}

        result = jury.think_with_board(
            "test input",
            mode="force_all",
            execution_layers=layers,
            board=board,
        )

        assert result.successful >= 1

    def test_think_with_board_respects_layers(self):
        """Later layers execute after earlier layers."""
        registry = Registry()
        registry.register(MockPerspective())
        registry.register(MockPerspective2())

        jury = Jury(registry)

        layers = {
            "mock_perspective": 0,
            "mock_perspective_2": 1,
        }

        result = jury.think_with_board(
            "test input",
            mode="force_all",
            execution_layers=layers,
        )

        assert result.successful == 2

    def test_think_with_board_fallback_to_think(self):
        """When only one layer, behaves like regular think."""
        registry = Registry()
        registry.register(MockPerspective())

        jury = Jury(registry)
        result = jury.think_with_board(
            "test input",
            mode="force_all",
        )

        # Should work without execution_layers
        assert result.successful == 1

    def test_think_with_board_creates_default_board(self):
        """When no board provided, creates one internally."""
        registry = Registry()
        registry.register(MockPerspective())

        jury = Jury(registry)
        result = jury.think_with_board(
            "test input",
            mode="force_all",
        )

        assert result.successful == 1

    def test_think_with_board_handles_errors(self):
        """Errors in one perspective don't crash others."""

        class FailingPerspective:
            id = "failing_perspective"
            name = "Failing Perspective"
            description = "A perspective that fails"
            trigger_keywords = ["fail"]

            def think(self, input: str, context: dict) -> PerspectiveOutput:
                raise RuntimeError("Intentional failure")

        registry = Registry()
        registry.register(MockPerspective())
        registry.register(FailingPerspective())

        jury = Jury(registry)
        result = jury.think_with_board(
            "test input",
            mode="force_all",
        )

        assert result.successful == 1
        assert result.failed == 1
        assert "failing_perspective" in result.errors


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
