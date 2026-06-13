"""
V5PerspectiveAdapter -将 v5 Perspective 适配为 v6 Expert
"""

from typing import Any, TYPE_CHECKING
import logging
import time

from ..types import (
    Expert, ExpertId, ExpertStatement, SpeakPrompt, SpeakRole,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class V5PerspectiveAdapter:
    """
    将 v5 Perspective 包装为 v6 Expert。
    
    用法:
        perspective = SomeV5Perspective()
        expert = V5PerspectiveAdapter(perspective)
        statement = expert.speak(prompt)
    """
    
    def __init__(
        self,
        perspective: Any,
        *,
        role_map: dict[SpeakRole, str] | None = None,
    ):
        self._p = perspective
        self._role_map = role_map or {}
    
    @property
    def id(self) -> ExpertId:
        return ExpertId(getattr(self._p, "id", str(id(self._p))))
    
    @property
    def name(self) -> str:
        return getattr(self._p, "name", "Unknown")
    
    @property
    def description(self) -> str:
        return getattr(self._p, "description", "")
    
    @property
    def domain(self) -> str:
        return getattr(self._p, "domain", "unknown")
    
    @property
    def trigger_keywords(self) -> tuple[str, ...]:
        return tuple(getattr(self._p, "trigger_keywords", []))
    
    @property
    def is_methodology(self) -> bool:
        return getattr(self._p, "is_methodology", False)
    
    def speak(self, prompt: SpeakPrompt) -> ExpertStatement:
        """执行发言。"""
        from ..types import ExpertId, SpeakRole

        input_text = self._compose_input(prompt)
        context = self._compose_context(prompt)

        # 调用 v5 perspective
        start = time.time()
        try:
            out = self._p.think(input_text, context)
        except Exception as e:
            logger.error(f"Perspective {self._p.id} error: {e}")
            out = None

        elapsed = time.time() - start

        return self._convert(out, prompt, elapsed)
    
    def _compose_input(self, prompt: SpeakPrompt) -> str:
        """组合输入文本。"""
        parts = [f"Question: {prompt.question}"]
        
        if prompt.argument_menu:
            parts.append("Previous arguments:")
            for arg in prompt.argument_menu.items:
                parts.append(f"  - [{arg.author_name}] {arg.claim}")
        
        parts.append(f"Your role: {prompt.role.value}")
        
        if prompt.targeted_arguments:
            parts.append("Please address these specific arguments:")
            for ref in prompt.targeted_arguments:
                parts.append(f"  - {ref}")
        
        if prompt.constraints:
            parts.append("Constraints:")
            for c in prompt.constraints:
                parts.append(f"  - {c}")
        
        return "
".join(parts)
    
    def _compose_context(self, prompt: SpeakPrompt) -> dict:
        """组合上下文。"""
        return {
            "session_id": prompt.session_id,
            "round_number": prompt.round_number,
            "role": prompt.role.value,
            "context_summary": prompt.context_summary,
        }
    
    def _convert(
        self,
        out: Any,
        prompt: SpeakPrompt,
        elapsed: float,
    ) -> ExpertStatement:
        """转换输出为 ExpertStatement。"""
        from ..types import ExpertStatement, ExpertId, SpeakRole

        if out is None:
            return ExpertStatement(
                expert_id=self.id,
                expert_name=self.name,
                role=prompt.role,
                content=f"[{self.name} was unable to respond]",
                confidence=0.0,
                elapsed_s=elapsed,
            )

        # 尝试从 v5 输出提取信息
        content = getattr(out, "content", str(out))
        confidence = getattr(out, "confidence", 0.5)

        return ExpertStatement(
            expert_id=self.id,
            expert_name=self.name,
            role=prompt.role,
            content=content,
            confidence=confidence,
            raw=out,
            elapsed_s=elapsed,
        )
