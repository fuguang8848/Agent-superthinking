"""
Standard interface for perspective modules.

To add a new perspective:
1. Create a new file in perspectives/ directory (e.g., my_perspective.py)
2. Implement the Perspective protocol
3. The registry will auto-discover and load it

Example:
    from dataclasses import dataclass
    from super_thinking.perspectives._interface import Perspective, PerspectiveOutput

    @dataclass
    class MyPerspectiveOutput(PerspectiveOutput):
        pass

    class MyPerspective:
        id = "my_perspective"
        name = "My Perspective"
        description = "What this perspective does"
        trigger_keywords = ["keyword1", "keyword2"]

        def think(self, input: str, context: dict) -> PerspectiveOutput:
            # Your analysis logic here
            return MyPerspectiveOutput(...)
"""

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable, Any


@dataclass
class PerspectiveOutput:
    """Standard output format for all perspectives."""

    perspective_id: str
    perspective_name: str
    analysis: str  # Detailed analysis content
    confidence: float = 0.5  # 0-1 confidence level
    key_points: list[str] = field(default_factory=list)  # Key findings
    tags: list[str] = field(default_factory=list)  # Categorization tags
    warnings: list[str] = field(default_factory=list)  # Limitations/risks
    metadata: dict[str, Any] = field(default_factory=dict)  # Additional data

    def __post_init__(self):
        if not 0 <= self.confidence <= 1:
            raise ValueError(f"confidence must be between 0 and 1, got {self.confidence}")


@runtime_checkable
class Perspective(Protocol):
    """Protocol that all perspective modules must implement.

    The registry validates compliance at load time using hasattr checks.
    """

    @property
    def id(self) -> str:
        """Unique identifier for this perspective."""
        ...

    @property
    def name(self) -> str:
        """Human-readable name."""
        ...

    @property
    def description(self) -> str:
        """Brief description of this perspective's focus."""
        ...

    @property
    def trigger_keywords(self) -> list[str]:
        """Keywords that trigger this perspective (for auto mode)."""
        ...

    def think(self, input: str, context: dict) -> PerspectiveOutput:
        """Analyze the input from this perspective's viewpoint.

        Args:
            input: The user's question or problem statement
            context: Additional context (can include previous results, user info, etc.)

        Returns:
            PerspectiveOutput with analysis and metadata
        """
        ...
