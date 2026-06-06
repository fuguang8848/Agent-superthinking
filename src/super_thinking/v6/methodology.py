"""
v6 Methodology Module

Methodology providers and registry.
"""

from __future__ import annotations
from typing import Protocol, runtime_checkable, TYPE_CHECKING
from .types import MethodId, MethodologyCall, MethodologyResult

if TYPE_CHECKING:
    from .types import DebateSession

@runtime_checkable
class MethodologyProvider(Protocol):
    @property
    def method_id(self) -> MethodId: ...
    @property
    def display_name(self) -> str: ...
    @property
    def summary(self) -> str: ...
    @property
    def when_to_use(self) -> str: ...
    @property
    def keywords(self): ...
    def is_applicable(self, claim: str, context: dict) -> tuple[bool, str]: ...
    def call(self, call: MethodologyCall) -> MethodologyResult: ...

class BaseMethodology:
    def __init__(self, method_id: str, display_name: str, summary: str, when_to_use: str, keywords: list[str]):
        self._method_id = MethodId(method_id)
        self._display_name = display_name
        self._summary = summary
        self._when_to_use = when_to_use
        self._keywords = tuple(keywords)
    
    @property
    def method_id(self) -> MethodId:
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
        return True, "Applicable"
    
    def call(self, call: MethodologyCall) -> MethodologyResult:
        return MethodologyResult(
            method_id=call.method_id,
            output=f"Analysis from {self._display_name}",
            validity="ok",
            elapsed_s=0.1,
        )

# ─── 1. EthicsMethodology ────────────────────────────────────────────────────
class EthicsMethodology(BaseMethodology):
    def __init__(self):
        super().__init__(
            method_id="ethics",
            display_name="Ethics",
            summary="Ethical analysis of claims",
            when_to_use="When moral considerations are relevant",
            keywords=["ethics", "moral", "right", "wrong", "justice", "fairness", "rights"],
        )

# ─── 2. EconomicsMethodology ─────────────────────────────────────────────────
class EconomicsMethodology(BaseMethodology):
    def __init__(self):
        super().__init__(
            method_id="economics",
            display_name="Economics",
            summary="Economic analysis of claims",
            when_to_use="When economic factors are relevant",
            keywords=["cost", "benefit", "market", "incentive", "utility", "equilibrium", "supply"],
        )

# ─── 3. GameTheoryMethodology ─────────────────────────────────────────────────
class GameTheoryMethodology(BaseMethodology):
    def __init__(self):
        super().__init__(
            method_id="gametheory",
            display_name="Game Theory",
            summary="Game theoretic analysis",
            when_to_use="When strategic interactions are relevant",
            keywords=["strategy", "game", "Nash", "equilibrium", "payoff", "cooperate", "defect"],
        )

# ─── 4. JurisprudenceMethodology ─────────────────────────────────────────────
class JurisprudenceMethodology(BaseMethodology):
    def __init__(self):
        super().__init__(
            method_id="jurisprudence",
            display_name="Jurisprudence",
            summary="Legal analysis of claims",
            when_to_use="When legal provisions, liability, rights, or obligations are involved",
            keywords=["law", "legal", "statute", "liability", "rights", "obligation", "jurisdiction"],
        )

# ─── 5. SociologyMethodology ─────────────────────────────────────────────────
class SociologyMethodology(BaseMethodology):
    def __init__(self):
        super().__init__(
            method_id="sociology",
            display_name="Sociology",
            summary="Sociological analysis of claims",
            when_to_use="When group behavior, social norms, or cultural influences are relevant",
            keywords=["society", "norm", "culture", "institution", "social", "群体", "行为模式"],
        )

# ─── 6. PsychologyMethodology ────────────────────────────────────────────────
class PsychologyMethodology(BaseMethodology):
    def __init__(self):
        super().__init__(
            method_id="psychology",
            display_name="Psychology",
            summary="Psychological analysis of claims",
            when_to_use="When motivations, cognitive biases, or emotional factors are relevant",
            keywords=["motivation", "bias", "cognition", "emotion", "behavior", "perception", "heuristic"],
        )

# ─── 7. OperationsResearchMethodology ─────────────────────────────────────────
class OperationsResearchMethodology(BaseMethodology):
    def __init__(self):
        super().__init__(
            method_id="operations_research",
            display_name="Operations Research",
            summary="Operations research and optimization analysis",
            when_to_use="When optimization, queuing, or resource allocation problems are involved",
            keywords=["optimize", "queue", "linear", "integer", "scheduling", "allocation", "efficiency"],
        )

# ─── 8. ManagementMethodology ────────────────────────────────────────────────
class ManagementMethodology(BaseMethodology):
    def __init__(self):
        super().__init__(
            method_id="management",
            display_name="Management",
            summary="Management and organizational analysis",
            when_to_use="When organizational structure, strategy, or leadership issues are involved",
            keywords=["strategy", "organization", "leadership", "management", "stakeholder", "vision", "culture"],
        )

# ─── 9. SystemsThinkingMethodology ───────────────────────────────────────────
class SystemsThinkingMethodology(BaseMethodology):
    def __init__(self):
        super().__init__(
            method_id="systems_thinking",
            display_name="Systems Thinking",
            summary="Systems dynamics and feedback analysis",
            when_to_use="When feedback loops, delays, or emergent behaviors are central to the problem",
            keywords=["feedback", "loop", "delay", "emergence", "leverage", "stock", "flow", "nonlinear"],
        )

# ─── 10. HistoryMethodology ─────────────────────────────────────────────────
class HistoryMethodology(BaseMethodology):
    def __init__(self):
        super().__init__(
            method_id="history",
            display_name="History",
            summary="Historical analysis and case parallels",
            when_to_use="When historical analogies or cyclical patterns provide insight",
            keywords=["history", "historical", "analogy", "pattern", "century", "era", "precedent"],
        )

# ─── 11. PhilosophyMethodology ───────────────────────────────────────────────
class PhilosophyMethodology(BaseMethodology):
    def __init__(self):
        super().__init__(
            method_id="philosophy",
            display_name="Philosophy",
            summary="Philosophical analysis of claims",
            when_to_use="When ontological, epistemological, or existential questions arise",
            keywords=["truth", "belief", "knowledge", "existence", "meaning", "ontology", "epistemology"],
        )

# ─── 12. MathematicsMethodology ───────────────────────────────────────────────
class MathematicsMethodology(BaseMethodology):
    def __init__(self):
        super().__init__(
            method_id="mathematics",
            display_name="Mathematics",
            summary="Mathematical analysis and formal reasoning",
            when_to_use="When probability, statistics, or logical deduction are needed",
            keywords=["probability", "statistic", "theorem", "proof", "distribution", "variance", "correlation"],
        )

# ─── 13. EngineeringMethodology ───────────────────────────────────────────────
class EngineeringMethodology(BaseMethodology):
    def __init__(self):
        super().__init__(
            method_id="engineering",
            display_name="Engineering",
            summary="Engineering design and trade-off analysis",
            when_to_use="When design decisions, trade-offs, or fault tolerance are discussed",
            keywords=["design", "tradeoff", "tolerance", "reliability", "specification", "constraint", "failure"],
        )

# ─── 14. BiologyMethodology ───────────────────────────────────────────────────
class BiologyMethodology(BaseMethodology):
    def __init__(self):
        super().__init__(
            method_id="biology",
            display_name="Biology",
            summary="Biological and evolutionary analysis",
            when_to_use="When evolution, adaptation, or ecosystem dynamics are relevant",
            keywords=["evolution", "adaptation", "ecosystem", "species", "fitness", "selection", "mutation"],
        )

# ─── 15. PhysicsMethodology ───────────────────────────────────────────────────
class PhysicsMethodology(BaseMethodology):
    def __init__(self):
        super().__init__(
            method_id="physics",
            display_name="Physics",
            summary="Physical laws and conservation analysis",
            when_to_use="When energy, conservation, or symmetry arguments apply",
            keywords=["energy", "conservation", "symmetry", "force", "entropy", "equilibrium", "field"],
        )

# ─── 16. LinguisticsMethodology ───────────────────────────────────────────────
class LinguisticsMethodology(BaseMethodology):
    def __init__(self):
        super().__init__(
            method_id="linguistics",
            display_name="Linguistics",
            summary="Linguistic and discourse analysis",
            when_to_use="When meaning, pragmatics, or discourse patterns are central",
            keywords=["semantic", "pragmatic", "discourse", "syntax", "language", "meaning", "utterance"],
        )

# ─── 17. PoliticalScienceMethodology ──────────────────────────────────────────
class PoliticalScienceMethodology(BaseMethodology):
    def __init__(self):
        super().__init__(
            method_id="political_science",
            display_name="Political Science",
            summary="Political analysis of power and institutions",
            when_to_use="When power structures, policy conflicts, or institutional design are involved",
            keywords=["power", "policy", "governance", "institution", "democracy", "vote", "legislation"],
        )

# ─── 18. ComplexityMethodology ────────────────────────────────────────────────
class ComplexityMethodology(BaseMethodology):
    def __init__(self):
        super().__init__(
            method_id="complexity",
            display_name="Complexity Science",
            summary="Complex systems and emergence analysis",
            when_to_use="When emergence, self-organization, or critical phase transitions are discussed",
            keywords=["emergence", "self-organization", "complexity", "phase", "critical", "adaptive", "nonlinear"],
        )

@runtime_checkable
class MethodologyRegistry(Protocol):
    def register(self, provider: MethodologyProvider) -> None: ...
    def unregister(self, method_id: MethodId) -> None: ...
    def get(self, method_id: MethodId) -> MethodologyProvider | None: ...
    def list_all(self) -> tuple[MethodologyProvider, ...]: ...
    def suggest_for(self, claim: str, *, top_k: int = 3) -> tuple[MethodologyProvider, ...]: ...
    def call(self, call: MethodologyCall) -> MethodologyResult: ...

class DefaultMethodologyRegistry:
    def __init__(self):
        self._providers: dict[MethodId, MethodologyProvider] = {}
        self._register_defaults()
    
    def _register_defaults(self):
        self.register(EthicsMethodology())
        self.register(EconomicsMethodology())
        self.register(GameTheoryMethodology())
        self.register(JurisprudenceMethodology())
        self.register(SociologyMethodology())
        self.register(PsychologyMethodology())
        self.register(OperationsResearchMethodology())
        self.register(ManagementMethodology())
        self.register(SystemsThinkingMethodology())
        self.register(HistoryMethodology())
        self.register(PhilosophyMethodology())
        self.register(MathematicsMethodology())
        self.register(EngineeringMethodology())
        self.register(BiologyMethodology())
        self.register(PhysicsMethodology())
        self.register(LinguisticsMethodology())
        self.register(PoliticalScienceMethodology())
        self.register(ComplexityMethodology())
    
    def register(self, provider: MethodologyProvider) -> None:
        self._providers[provider.method_id] = provider
    
    def unregister(self, method_id: MethodId) -> None:
        if method_id in self._providers:
            del self._providers[method_id]
    
    def get(self, method_id: MethodId) -> MethodologyProvider | None:
        return self._providers.get(method_id)
    
    def list_all(self) -> tuple[MethodologyProvider, ...]:
        return tuple(self._providers.values())
    
    def suggest_for(self, claim: str, *, top_k: int = 3) -> tuple[MethodologyProvider, ...]:
        scored = []
        for provider in self._providers.values():
            score = sum(1 for kw in provider.keywords if kw.lower() in claim.lower())
            scored.append((score, provider))
        scored.sort(key=lambda x: -x[0])
        return tuple(p for _, p in scored[:top_k])
    
    def call(self, call: MethodologyCall) -> MethodologyResult:
        provider = self._providers.get(call.method_id)
        if provider:
            return provider.call(call)
        return MethodologyResult(method_id=call.method_id, output="Methodology not found", validity="inconclusive")

    def validate_methodology_usage(
        self, method_id: MethodId, claim: str
    ) -> tuple[bool, str]:
        """
        验证方法论是否适用于当前论点（乱用检测）。

        基于关键词匹配：claim 中包含 >=1 个方法论关键词 = 适用。
        子类可重写 is_applicable() 提供更精确的判断。

        Args:
            method_id: 方法论 ID
            claim: 专家的论点内容

        Returns:
            (is_valid, reason) - is_valid=True 表示适用，False 表示乱用
        """
        provider = self._providers.get(method_id)
        if not provider:
            return False, f"方法论 {method_id} 未注册"

        # 关键词匹配判断适用性
        claim_lower = claim.lower()
        matched = [kw for kw in provider.keywords if kw.lower() in claim_lower]
        if matched:
            return True, f"适用（匹配：{', '.join(matched[:3])})"

        return False, (
            f"论点中未发现 {provider.display_name} 相关关键词 "
            f"（期望包含：{', '.join(provider.keywords[:5])}）"
        )

    def get_methodology_prompt_block(self) -> str:
        """
        生成方法论工具池的提示文本块，供注入到专家 prompt。
        列出所有可用方法论及其适用场景。
        """
        lines = ["\n【可用方法论工具池】"]
        for p in self._providers.values():
            lines.append(f"- [{p.method_id}] {p.display_name}: {p.when_to_use}")
        lines.append("使用方法论时，格式：\"我用[方法论]检验：<检验内容>\"")
        lines.append("主持人有权判断方法论是否适用于当前论点。\n")
        return "\n".join(lines)

__all__ = ["MethodologyProvider", "MethodologyRegistry", "DefaultMethodologyRegistry", "BaseMethodology"]
