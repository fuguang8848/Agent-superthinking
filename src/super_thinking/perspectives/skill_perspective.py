"""
Skill-based perspective that wraps a SKILL.md file.

Allows perspectives to be defined as SKILL.md files instead of Python classes,
making it easy to add new experts without writing code.
"""

from __future__ import annotations

import re
import yaml
from pathlib import Path
from typing import Any, Optional

from super_thinking.perspectives._interface import Perspective, PerspectiveOutput


def _get_shared_context():
    """
    Get or create SharedContext singleton.
    This avoids circular imports with the thinking skill.
    """
    try:
        # Try to import from agent-symphony's shared context
        import sys
        from pathlib import Path
        
        # agent-symphony is at: .../compound-engineering/agent-symphony/
        agent_symphony_path = Path(__file__).parent.parent.parent.parent / "agent-symphony"
        if str(agent_symphony_path) not in sys.path:
            sys.path.insert(0, str(agent_symphony_path))
        
        from shared.context import get_context
        return get_context()
    except Exception:
        return None


class SkillBasedPerspective(Perspective):
    """
    A perspective defined by a SKILL.md file.
    
    The SKILL.md should have YAML frontmatter with:
    - name: perspective ID
    - description: description
    
    The markdown content is used as the system prompt for LLM-based thinking.
    """
    
    _shared_context = None  # Lazy singleton
    
    def __init__(self, skill_path: Path):
        self._skill_path = skill_path
        self._frontmatter: dict = {}
        self._content: str = ""
        self._llm = None
        self._load()
    
    @classmethod
    def _get_context(cls):
        """Lazy-load SharedContext singleton."""
        if cls._shared_context is None:
            cls._shared_context = _get_shared_context()
        return cls._shared_context
    
    def _load(self) -> None:
        """Load and parse the SKILL.md file."""
        with open(self._skill_path, encoding="utf-8") as f:
            content = f.read()
        
        # Parse YAML frontmatter
        fm_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
        if fm_match:
            try:
                self._frontmatter = yaml.safe_load(fm_match.group(1)) or {}
            except Exception:
                self._frontmatter = {}
            self._content = content[fm_match.end():]
        else:
            self._frontmatter = {}
            self._content = content
        
        # Set perspective attributes from frontmatter
        self._id = self._frontmatter.get("name", self._skill_path.stem.replace("-perspective", ""))
        self._name = self._id.replace("_", " ").replace("-", " ").title()
        self._description = self._frontmatter.get("description", "")[:200]
        
        # Extract trigger keywords from description
        desc = self._description.lower()
        self._trigger_keywords = self._extract_keywords(desc)
    
    def _extract_keywords(self, text: str) -> list[str]:
        """Extract simple keywords from description."""
        # Remove common Chinese stopwords
        stopwords = {"的", "是", "在", "和", "与", "或", "了", "于", "为", "以", "及", "等", "当", "该", "可", "能", "会"}
        words = re.findall(r'[\u4e00-\u9fa5a-zA-Z0-9]+', text)
        keywords = [w for w in words if len(w) >= 2 and w not in stopwords]
        # Deduplicate while preserving order
        seen = set()
        unique = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique.append(kw)
        return unique[:10]  # Limit to 10 keywords
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def trigger_keywords(self) -> list[str]:
        return self._trigger_keywords
    
    def think(self, input_text: str, context: Optional[dict[str, Any]] = None) -> PerspectiveOutput:
        """
        Execute this perspective using the LLM with the SKILL.md content as system prompt.
        
        Returns a PerspectiveOutput with the LLM's analysis.
        """
        ctx = self._get_context()
        
        # Build the prompt
        system_prompt = self._content.strip()
        user_prompt = f"问题/需求：{input_text}\n\n请用你的专业知识分析这个问题。"
        
        try:
            if ctx is None:
                return PerspectiveOutput(
                    perspective_id=self.id,
                    perspective_name=self.name,
                    analysis=f"[SharedContext not available for {self.id}]",
                    key_points=[],
                    confidence=0.0,
                    metadata={"source": "SKILL.md", "path": str(self._skill_path)}
                )
            
            # Use SharedContext.call_llm() - handles API type detection automatically
            text = ctx.call_llm(
                prompt=user_prompt,
                system=system_prompt,
                max_tokens=1024
            )
            
            return PerspectiveOutput(
                perspective_id=self.id,
                perspective_name=self.name,
                analysis=text or f"[Empty response from {self.id}]",
                key_points=self._extract_key_points(text) if text else [],
                confidence=0.8,
                metadata={"source": "SKILL.md", "path": str(self._skill_path)}
            )
            
        except Exception as e:
            return PerspectiveOutput(
                perspective_id=self.id,
                perspective_name=self.name,
                analysis=f"[Error in {self.id}: {str(e)}]",
                key_points=[],
                confidence=0.0,
                metadata={"source": "SKILL.md", "path": str(self._skill_path), "error": str(e)}
            )
    
    def _extract_key_points(self, text: str) -> list[str]:
        """Extract key points from LLM response."""
        # Simple extraction: look for bullet points or numbered items
        points = []
        for line in text.split("\n"):
            line = line.strip()
            # Match bullet points or numbered items
            if re.match(r"^[-•*]\s+", line) or re.match(r"^\d+[.、)\s]+", line):
                # Remove the bullet/number prefix
                clean = re.sub(r"^[-•*]\s+", "", line)
                clean = re.sub(r"^\d+[.、)\s]+", "", clean)
                if clean and len(clean) > 5:
                    points.append(clean[:100])
        return points[:5]  # Limit to 5 key points
    
    def matches(self, text: str) -> float:
        """Check if text matches this perspective's keywords."""
        text_lower = text.lower()
        score = 0.0
        for kw in self._trigger_keywords:
            if kw.lower() in text_lower:
                score += 1.0
        return min(score / max(len(self._trigger_keywords), 1), 1.0)


def load_skill_perspectives(experts_root: Path) -> list[SkillBasedPerspective]:
    """
    Load all SKILL.md perspectives from the experts directory.
    
    Args:
        experts_root: Path to the experts/ directory containing category subdirectories
        
    Returns:
        List of SkillBasedPerspective instances
    """
    perspectives = []
    
    if not experts_root.exists():
        return perspectives
    
    # Find all SKILL.md files
    for skill_file in experts_root.rglob("SKILL.md"):
        try:
            perspective = SkillBasedPerspective(skill_file)
            perspectives.append(perspective)
        except Exception as e:
            print(f"Warning: Failed to load {skill_file}: {e}")
    
    return perspectives
