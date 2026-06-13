"""Prompt templates for v6 debate system."""

from pathlib import Path

PROMPTS_DIR = Path(__file__).parent


def load_prompt(name: str) -> str:
    """Load prompt template by filename (without .md extension).

    Args:
        name: Prompt template name (e.g., "MODERATOR_SYSTEM", "EXPERT_SYSTEM")

    Returns:
        The prompt template content as a string.

    Raises:
        FileNotFoundError: If the prompt template does not exist.
    """
    return (PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8")


__all__ = ["PROMPTS_DIR", "load_prompt"]
