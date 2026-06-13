"""
v6 Distillation Pipeline

Loads SKILL.md files (from nuwa-skill distillation output) and registers
the extracted Expert/Methodology into the corresponding pools.

Data flow:
    SKILL.md (file)
        ↓
    DistillationPipeline.load_skill(skill_path)
        ↓
    SkillMetadata (dataclass)
        ↓
    pipeline.register_to(expert_pool, methodology_registry)
        ↓
    DistilledExpert / DistilledMethodology → hot-swapped into pool
"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Literal

logger = logging.getLogger(__name__)

# =============================================================================
# SkillMetadata dataclass
# =============================================================================

@dataclass
class SkillMetadata:
    skill_id: str                          # filename as ID
    name: str                               # person / topic name
    description: str                        # frontmatter description
    type: Literal["person", "topic", "hybrid"]  # auto-detected type

    # Expert-related
    trigger_keywords: list[str] = field(default_factory=list)
    mental_models: list[dict] = field(default_factory=list)   # [{name, evidence, application, limitation}]
    decision_heuristics: list[dict] = field(default_factory=list)  # [{scenario, rule, example}]
    expression_dna: dict = field(default_factory=dict)         # {句式偏好, 词汇特征, ...}
    values: list[str] = field(default_factory=list)
    anti_patterns: list[str] = field(default_factory=list)
    honest_boundaries: list[str] = field(default_factory=list)
    intellectual_lineage: dict = field(default_factory=dict)   # {influenced_by, influenced, position}

    # Methodology-related (for topic/hybrid types)
    core_questions: list[str] = field(default_factory=list)
    application_scenarios: list[str] = field(default_factory=list)

    # Source tracking
    source_file: Path | None = None
    created_at: str = ""
    source_quality: dict = field(default_factory=dict)  # {一手占比, 主要来源, ...}

# =============================================================================
# Registration Result
# =============================================================================

@dataclass
class RegistrationResult:
    skill_id: str
    expert_id: str | None = None
    method_id: str | None = None
    type: Literal["person", "topic", "hybrid", "none"] = "none"
    registered_to_pool: bool = False
    pool_name: str | None = None
    warnings: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return self.registered_to_pool


# =============================================================================
# DistillationPipeline
# =============================================================================

class DistillationPipeline:
    """
    Loads SKILL.md files and registers extracted experts/methodologies
    into the appropriate pools.
    """

    def __init__(self) -> None:
        self._skills: dict[str, SkillMetadata] = {}

    # -------------------------------------------------------------------------
    # Loading
    # -------------------------------------------------------------------------

    def load_skill(self, skill_path: Path) -> SkillMetadata:
        """
        Parse a SKILL.md file and extract structured metadata.

        The file is expected to follow nuwa-skill's distillation format:
          - YAML frontmatter (--- ... ---)
          - Markdown body with named sections
        """
        skill_path = Path(skill_path).expanduser().resolve()
        if not skill_path.exists():
            raise FileNotFoundError(f"SKILL.md not found: {skill_path}")

        raw = skill_path.read_text(encoding="utf-8")
        meta = self._parse_skill_md(raw, skill_path)
        self._skills[meta.skill_id] = meta
        logger.info(f"Loaded skill: {meta.skill_id} ({meta.type}) - {meta.name}")
        return meta

    def _parse_skill_md(self, raw: str, source_file: Path) -> SkillMetadata:
        """Parse raw SKILL.md text into SkillMetadata."""

        # --- Extract frontmatter ---
        frontmatter: dict = {}
        fm_match = re.match(r"^---\s*\n(.*?)\n---", raw, re.DOTALL)
        if fm_match:
            frontmatter = self._parse_frontmatter(fm_match.group(1))

        body = re.sub(r"^---\s*\n.*?\n---\s*\n", "", raw, count=1, flags=re.DOTALL).strip()

        # --- Basic identity ---
        skill_id = source_file.stem  # filename without extension
        name = frontmatter.get("name", skill_id)
        description = frontmatter.get("description", "").strip()

        # --- Trigger keywords from frontmatter ---
        raw_triggers = frontmatter.get("triggers", "")
        if isinstance(raw_triggers, list):
            trigger_keywords = [str(t).strip() for t in raw_triggers if t]
        elif isinstance(raw_triggers, str):
            trigger_keywords = [t.strip() for t in re.split(r"[,，/｜|]", raw_triggers) if t.strip()]
        else:
            trigger_keywords = []

        # --- Auto-detect type ---
        skill_type = self.auto_detect_type_from_content(name, body, frontmatter)

        # --- Parse named body sections ---
        mental_models = self._extract_mental_models(body)
        decision_heuristics = self._extract_decision_heuristics(body)
        expression_dna = self._extract_expression_dna(body)
        values, anti_patterns = self._extract_values_and_anti(body)
        honest_boundaries = self._extract_honest_boundaries(body)
        intellectual_lineage = self._extract_intellectual_lineage(body)
        core_questions, application_scenarios = self._extract_methodology_meta(body)
        source_quality = self._extract_source_quality(body)

        # Fallback: extract triggers from description text (nuwa-skill embeds them inline)
        if not trigger_keywords:
            trigger_keywords = self._extract_trigger_keywords_from_body(body)
        if not trigger_keywords and description:
            trigger_keywords = self._extract_trigger_keywords_from_text(description)

        created_at = frontmatter.get("created_at", datetime.now().isoformat())

        return SkillMetadata(
            skill_id=skill_id,
            name=name,
            description=description,
            type=skill_type,
            trigger_keywords=trigger_keywords,
            mental_models=mental_models,
            decision_heuristics=decision_heuristics,
            expression_dna=expression_dna,
            values=values,
            anti_patterns=anti_patterns,
            honest_boundaries=honest_boundaries,
            intellectual_lineage=intellectual_lineage,
            core_questions=core_questions,
            application_scenarios=application_scenarios,
            source_file=source_file,
            created_at=created_at,
            source_quality=source_quality,
        )

    def _parse_frontmatter(self, text: str) -> dict:
        """Parse YAML-like frontmatter into a dict."""
        result: dict = {}
        current_key: str | None = None
        current_value: list[str] = field(default_factory=list)

        for line in text.splitlines():
            line = line.rstrip()
            # Key: value  or  key: |
            match = re.match(r"^(\w+)\s*:\s*(.*)$", line)
            if match:
                # Flush previous key
                if current_key is not None:
                    result[current_key] = "\n".join(current_value).strip()

                key = match.group(1)
                val = match.group(2).strip()

                if val in ("", "|", ">"):
                    current_key = key
                    current_value = []
                elif val.startswith('"') or val.startswith("'"):
                    result[key] = val.strip('"\'')
                else:
                    result[key] = val
                    current_key = None
            elif current_key is not None and line.strip():
                current_value.append(line)

        if current_key is not None:
            result[current_key] = "\n".join(current_value).strip()

        return result

    # -------------------------------------------------------------------------
    # Section extractors
    # -------------------------------------------------------------------------

    def _extract_mental_models(self, body: str) -> list[dict]:
        """Extract mental models section."""
        models = []
        section = self._extract_section(body, "心智模型")
        if not section:
            return models

        # Each model is a `### N. Name` subsection
        pattern = r"###\s+\d+\.\s+(.+?)\s*\n(.*?)(?=\n###\s+\d+\.|\n## |\Z)"
        for match in re.finditer(pattern, section, re.DOTALL):
            name = match.group(1).strip()
            content = match.group(2).strip()

            model: dict = {"name": name}
            # Try to parse sub-fields from content
            evidence = re.search(r"\*\*证据\*\*[:：]?\s*(.+?)(?:\n|$)", content, re.DOTALL)
            if evidence:
                model["evidence"] = evidence.group(1).strip()
            application = re.search(r"\*\*应用\*\*[:：]?\s*(.+?)(?:\n|$)", content, re.DOTALL)
            if application:
                model["application"] = application.group(1).strip()
            limitation = re.search(r"\*\*局限\*\*[:：]?\s*(.+?)(?:\n|$)", content, re.DOTALL)
            if limitation:
                model["limitation"] = limitation.group(1).strip()

            if "evidence" not in model:
                model["evidence"] = content[:200]  # Fallback: first 200 chars

            models.append(model)

        return models

    def _extract_decision_heuristics(self, body: str) -> list[dict]:
        """Extract decision heuristics section."""
        heuristics = []
        section = self._extract_section(body, "决策启发式")
        if not section:
            return heuristics

        pattern = r"###\s+\d+\.\s+(.+?)\s*\n(.*?)(?=\n###\s+\d+\.|\n## |\Z)"
        for match in re.finditer(pattern, section, re.DOTALL):
            name = match.group(1).strip()
            content = match.group(2).strip()

            h: dict = {"name": name}
            scenario = re.search(r"\*\*场景\*\*[:：]?\s*(.+?)(?:\n|$)", content, re.DOTALL)
            if scenario:
                h["scenario"] = scenario.group(1).strip()
            rule = re.search(r"\*\*规则\*\*[:：]?\s*(.+?)(?:\n|$)", content, re.DOTALL)
            if rule:
                h["rule"] = rule.group(1).strip()
            example = re.search(r"\*\*案例\*\*[:：]?\s*(.+?)(?:\n|$)", content, re.DOTALL)
            if example:
                h["example"] = example.group(1).strip()

            if len(h) == 1:  # Only name, no sub-fields
                h["description"] = content[:200]

            heuristics.append(h)

        return heuristics

    def _extract_expression_dna(self, body: str) -> dict:
        """Extract expression DNA section."""
        section = self._extract_section(body, "表达DNA")
        if not section:
            return {}

        dna: dict = {}
        # Try key: value pattern
        for line in section.splitlines():
            line = line.strip()
            m = re.match(r"^\*\*([^：:]+)：?\*\*\s*(.+)$", line)
            if m:
                key = m.group(1).strip()
                val = m.group(2).strip()
                dna[key] = val
        return dna

    def _extract_values_and_anti(self, body: str) -> tuple[list[str], list[str]]:
        """Extract values and anti-patterns."""
        values: list[str] = []
        anti_patterns: list[str] = []

        section = self._extract_section(body, "价值观")
        if section:
            for line in section.splitlines():
                m = re.match(r"^\d+[.、]\s*(.+)$", line.strip())
                if m:
                    values.append(m.group(1).strip())
                m2 = re.match(r"^\*\*(.+?)\*\*[:：]", line)
                if m2 and "反模式" not in m2.group(1):
                    values.append(m2.group(1).strip())

        anti_section = self._extract_section(body, "反模式")
        if anti_section:
            for line in anti_section.splitlines():
                m = re.match(r"^\d+[.、]\s*(.+)$", line.strip())
                if m:
                    anti_patterns.append(m.group(1).strip())

        return values, anti_patterns

    def _extract_honest_boundaries(self, body: str) -> list[str]:
        """Extract honest boundaries / limitations."""
        section = self._extract_section(body, "诚实边界")
        if not section:
            section = self._extract_section(body, "局限")
        if not section:
            return []

        boundaries = []
        for line in section.splitlines():
            line = line.strip()
            m = re.match(r"^[-*]\s*(.+)$", line)
            if m:
                boundaries.append(m.group(1).strip())
            m2 = re.match(r"^\d+[.、]\s*(.+)$", line)
            if m2:
                boundaries.append(m2.group(1).strip())
        return boundaries

    def _extract_intellectual_lineage(self, body: str) -> dict:
        """Extract intellectual lineage."""
        section = self._extract_section(body, "智识谱系")
        if not section:
            return {}

        lineage: dict = {}
        for line in section.splitlines():
            m = re.match(r"^\*\*([^：:]+)：?\*\*\s*(.+)$", line)
            if m:
                key = m.group(1).strip()
                val = m.group(2).strip()
                lineage[key] = val
        return lineage

    def _extract_methodology_meta(self, body: str) -> tuple[list[str], list[str]]:
        """Extract core questions and application scenarios (for topic/hybrid skills)."""
        core_q: list[str] = []
        app_scenarios: list[str] = []

        q_section = self._extract_section(body, "核心问题")
        if q_section:
            for line in q_section.splitlines():
                m = re.match(r"^\d+[.、]\s*(.+)$", line.strip())
                if m:
                    core_q.append(m.group(1).strip())

        scenario_section = self._extract_section(body, "应用场景")
        if scenario_section:
            for line in scenario_section.splitlines():
                m = re.match(r"^\d+[.、]\s*(.+)$", line.strip())
                if m:
                    app_scenarios.append(m.group(1).strip())

        return core_q, app_scenarios

    def _extract_source_quality(self, body: str) -> dict:
        """Extract source quality info from调研来源 section."""
        quality: dict = {}
        section = self._extract_section(body, "调研来源")
        if not section:
            return quality

        primary = re.search(r"\*\*一手来源\*\*[:：]?\s*([\d%]+)", section)
        if primary:
            quality["primary_source_ratio"] = primary.group(1)
        return quality

    def _extract_trigger_keywords_from_body(self, body: str) -> list[str]:
        """Fallback: extract triggers from ### 触发词 subsection in body."""
        section = self._extract_section(body, "触发词")
        if not section:
            return []

        keywords = []
        for line in section.splitlines():
            line = line.strip().strip("-*")
            if line and len(line) < 50:  # Filter out long lines
                keywords.append(line)
        return keywords

    def _extract_trigger_keywords_from_text(self, text: str) -> list[str]:
        """
        Extract trigger keywords from inline text.

        Handles nuwa-skill format: 触发词：「造skill」「蒸馏XX」「女娲」...
        Also handles: 触发词: 「XX」, 触发词：「XX」等多种变体。
        """
        keywords = []
        # Match trigger section marker followed by 「」 or 「」 quoted items
        # Pattern: 触发词： or 触发词: followed by 「...」「...」...
        trigger_section = re.search(r"触发词[：:]*[\s「\n]*(.+?)(?=\n\n|$)", text, re.DOTALL)
        if trigger_section:
            trigger_text = trigger_section.group(1)
            # Extract all 「」 quoted items
            for match in re.finditer(r"[「『]([^」』]+)[」』]", trigger_text):
                kw = match.group(1).strip()
                if kw and len(kw) < 30:
                    keywords.append(kw)
        return keywords

    def _extract_section(self, body: str, heading: str) -> str:
        """Extract the content under a ## Heading section."""
        # Match ## heading name (allowing Chinese, English, punctuation)
        pattern = rf"(?:^|\n)##\s+[^\n]*{re.escape(heading)}[^\n]*\n(.*?)(?=\n##\s|\Z)"
        match = re.search(pattern, body, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""

    # -------------------------------------------------------------------------
    # Type detection
    # -------------------------------------------------------------------------

    def auto_detect_type(self, meta: SkillMetadata) -> Literal["person", "topic", "hybrid"]:
        """
        Auto-detect skill type based on metadata.

        - person: explicitly named individual (e.g. "芒格", "费曼")
        - topic: framework/theme without personal identity (e.g. "价值投资")
        - hybrid: blends person style with topic framework
        """
        return self.auto_detect_type_from_content(meta.name, "", {})

    def auto_detect_type_from_content(
        self, name: str, body: str, frontmatter: dict
    ) -> Literal["person", "topic", "hybrid"]:
        """
        Detect type from name and content clues.

        Person indicators:
          - First/last name of a known person
          - "的思维方式", "视角", "perspective" in name
          - "人物" or "person" keyword

        Topic indicators:
          - Framework, methodology, strategy in name
          - "主题", "topic" keyword
          - No personal identity in content

        Hybrid: blends personal voice with topic framework.
        """

        name_lower = name.lower()

        # Explicit person markers
        person_markers = [
            "的思维方式", "视角", "perspective", "-perspective",
            "人物", "person", "大师", "思想家",
        ]
        # Explicit topic markers
        topic_markers = [
            "框架", "framework", "方法论", "methodology",
            "策略", "strategy", "体系", "系统",
            "主题", "topic", "指南", "guide",
        ]

        has_person_marker = any(m in name_lower for m in person_markers)
        has_topic_marker = any(m in name_lower for m in topic_markers)

        # Check body for role-playing rules (indicates person-type)
        has_role_playing = "角色扮演" in body or "role play" in body.lower()
        has_identity_card = "身份卡" in body

        if has_person_marker or has_role_playing or has_identity_card:
            if has_topic_marker:
                return "hybrid"
            return "person"

        if has_topic_marker:
            return "topic"

        # Fallback: look for personal pronouns and first-person voice in body
        personal_pronouns = ["我", "我们", "我认为", "我相信", "I ", "my "]
        if any(p in body[:500] for p in personal_pronouns):
            return "person"

        return "topic"

    # -------------------------------------------------------------------------
    # Registration
    # -------------------------------------------------------------------------

    def register_to(
        self,
        skill_path: Path,
        expert_pool=None,
        methodology_registry=None,
        force_methodology: bool = False,
    ) -> RegistrationResult:
        """
        Load a SKILL.md and register the extracted expert/methodology
        into the appropriate pools.

        Parameters
        ----------
        skill_path : Path
            Path to SKILL.md file
        expert_pool : ExpertPool | None
            Expert pool to register person/hybrid types
        methodology_registry : MethodologyRegistry | None
            Methodology registry to register topic/hybrid types
        force_methodology : bool
            Force registration as methodology (for topic skills)

        Returns
        -------
        RegistrationResult
            Summary of what was registered
        """
        meta = self.load_skill(skill_path)
        result = RegistrationResult(skill_id=meta.skill_id, type=meta.type)

        if force_methodology or meta.type in ("topic", "hybrid"):
            if methodology_registry is not None:
                self._register_as_methodology(meta, methodology_registry)
                result.method_id = meta.skill_id
                result.registered_to_pool = True
                result.pool_name = "methodology_registry"

        if not force_methodology and meta.type in ("person", "hybrid"):
            if expert_pool is not None:
                self._register_as_expert(meta, expert_pool)
                result.expert_id = meta.skill_id
                result.registered_to_pool = True
                result.pool_name = "expert_pool"
                if meta.type == "hybrid":
                    # Hybrid also registers to methodology if available
                    if methodology_registry is not None:
                        self._register_as_methodology(meta, methodology_registry)
                        result.method_id = meta.skill_id
                        logger.info(f"Hybrid skill {meta.skill_id} also registered to methodology_registry")

        if not result.registered_to_pool:
            result.warnings.append(
                f"No suitable pool found for type '{meta.type}'. "
                f"Provide expert_pool for person/hybrid, methodology_registry for topic/hybrid."
            )

        return result

    def _register_as_expert(self, meta: SkillMetadata, pool) -> None:
        """Register a SkillMetadata as a DistilledExpert in the expert pool."""
        expert = DistilledExpert(meta)
        pool.register(expert)
        logger.info(f"Registered expert '{expert.name}' (id={expert.id}) to pool")

    def _register_as_methodology(self, meta: SkillMetadata, registry) -> None:
        """Register a SkillMetadata as a DistilledMethodology in the registry."""
        methodology = DistilledMethodology(meta)
        registry.register(methodology)
        logger.info(f"Registered methodology '{methodology.display_name}' (id={methodology.method_id}) to registry")


# =============================================================================
# DistilledExpert
# =============================================================================

class DistilledExpert:
    """
    Expert implementation backed by a distilled SKILL.md.

    Implements the Expert protocol from types.py.
    """

    def __init__(self, meta: SkillMetadata) -> None:
        from .types import ExpertId

        self._meta = meta
        self._id = ExpertId(meta.skill_id)
        self._name = meta.name
        self._description = meta.description
        self._domain = self._infer_domain(meta)
        self._trigger_keywords = tuple(meta.trigger_keywords)
        self._mental_models = meta.mental_models
        self._decision_heuristics = meta.decision_heuristics
        self._expression_dna = meta.expression_dna
        self._values = tuple(meta.values)
        self._anti_patterns = tuple(meta.anti_patterns)
        self._honest_boundaries = tuple(meta.honest_boundaries)
        self._intellectual_lineage = meta.intellectual_lineage

    def _infer_domain(self, meta: SkillMetadata) -> str:
        """Infer domain from name and type."""
        if meta.type == "person":
            return f"思维模型 / {meta.name}"
        return meta.name

    @property
    def id(self):
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def domain(self) -> str:
        return self._domain

    @property
    def trigger_keywords(self) -> tuple[str, ...]:
        return self._trigger_keywords

    @property
    def is_methodology(self) -> bool:
        return False

    def speak(self, prompt) -> "ExpertStatement":
        """
        Generate a statement using mental models and expression DNA.

        In a full implementation this would call an LLM with the skill's
        mental models and expression_dna as system context.
        For now we return a placeholder that can be filled in with LLM integration.
        """
        from .types import ExpertStatement, SpeakRole

        content = (
            f"[{self._name}] 基于心智模型和决策启发式生成的分析。\n"
            f"触发词匹配: {', '.join(self._trigger_keywords[:3])}\n"
            f"(LLM integration needed for full generation)"
        )

        return ExpertStatement(
            expert_id=self._id,
            expert_name=self._name,
            role=prompt.role if hasattr(prompt, "role") else SpeakRole.INITIAL,
            content=content,
            confidence=0.5,
        )

    def __repr__(self) -> str:
        return f"DistilledExpert(id={self._id}, name={self._name}, type={self._meta.type})"


# =============================================================================
# DistilledMethodology
# =============================================================================

class DistilledMethodology:
    """
    Methodology provider backed by a distilled SKILL.md (topic/hybrid type).

    Implements the MethodologyProvider protocol from types.py.
    """

    def __init__(self, meta: SkillMetadata) -> None:
        from .types import MethodId

        self._meta = meta
        self._method_id = MethodId(meta.skill_id)
        self._display_name = meta.name
        self._summary = meta.description
        self._when_to_use = ", ".join(meta.application_scenarios[:3]) if meta.application_scenarios else "General purpose"
        self._keywords = tuple(meta.trigger_keywords)
        self._core_questions = meta.core_questions
        self._mental_models = meta.mental_models
        self._decision_heuristics = meta.decision_heuristics

    @property
    def method_id(self):
        return self._method_id

    @property
    def display_name(self) -> str:
        return self._display_name

    @property
    def summary(self) -> str:
        return self._summary

    @property
    def when_to_use(self) -> str:
        return self._when_to_use

    @property
    def keywords(self):
        return self._keywords

    def is_applicable(self, claim: str, context: dict) -> tuple[bool, str]:
        """Check if this methodology is applicable to the given claim."""
        claim_lower = claim.lower()
        score = sum(1 for kw in self._keywords if kw.lower() in claim_lower)
        applicable = score > 0 or len(self._keywords) == 0
        reason = f"Matched {score} keyword(s)" if applicable else "No keyword match"
        return applicable, reason

    def call(self, call) -> "MethodologyResult":
        """Execute the methodology on the given call."""
        from .types import MethodologyResult

        output_parts = [f"## {self._display_name} 分析\n"]

        if self._mental_models:
            output_parts.append("**心智模型：**")
            for m in self._mental_models[:3]:
                output_parts.append(f"- {m.get('name', 'Unknown')}: {m.get('application', m.get('evidence', ''))[:100]}")

        if self._decision_heuristics:
            output_parts.append("\n**决策启发式：**")
            for h in self._decision_heuristics[:3]:
                output_parts.append(f"- {h.get('name', 'Unknown')}: {h.get('rule', h.get('description', ''))[:100]}")

        return MethodologyResult(
            method_id=call.method_id,
            output="\n".join(output_parts),
            validity="ok",
            elapsed_s=0.0,
        )

    def __repr__(self) -> str:
        return f"DistilledMethodology(id={self._method_id}, name={self._display_name})"


# =============================================================================
# Convenience API
# =============================================================================

def load_and_register(
    skill_path: Path,
    expert_pool=None,
    methodology_registry=None,
    force_methodology: bool = False,
) -> RegistrationResult:
    """
    One-liner: load a SKILL.md and register to the appropriate pool(s).

    Example
    -------
    >>> from super_thinking.v6 import ExpertPool, DefaultMethodologyRegistry
    >>> from super_thinking.v6.distillation import load_and_register
    >>> pool = ExpertPool()
    >>> registry = DefaultMethodologyRegistry()
    >>> result = load_and_register(
    ...     Path("~/skills/芒格.md"),
    ...     expert_pool=pool,
    ...     methodology_registry=registry,
    ... )
    >>> print(f"Registered {result.expert_id} as {result.type}")
    """
    pipeline = DistillationPipeline()
    return pipeline.register_to(
        skill_path=skill_path,
        expert_pool=expert_pool,
        methodology_registry=methodology_registry,
        force_methodology=force_methodology,
    )


__all__ = [
    "SkillMetadata",
    "RegistrationResult",
    "DistillationPipeline",
    "DistilledExpert",
    "DistilledMethodology",
    "load_and_register",
]
