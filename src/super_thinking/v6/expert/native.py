"""
expert/native.py - 原生 v6 Expert 抽象基类

§3.1 Expert 子系统：提供 BaseExpert 抽象基类和 TemplateExpert 实现。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import ExpertId, ExpertStatement, SpeakPrompt


class BaseExpert(ABC):
    """
    原生 v6 Expert 抽象基类。

    所有 v6 原生专家实现必须继承此类。
    """

    @property
    @abstractmethod
    def id(self) -> "ExpertId":
        """专家唯一标识。"""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """专家显示名。"""
        ...

    @property
    def description(self) -> str:
        """专家描述，默认为 name + domain。"""
        return self.name

    @property
    def trigger_keywords(self) -> tuple[str, ...]:
        """触发关键词，用于专家池匹配。"""
        return ()

    @property
    def is_methodology(self) -> bool:
        """是否为方法论专家。"""
        return False

    @abstractmethod
    def speak(self, prompt: "SpeakPrompt") -> "ExpertStatement":
        """
        让专家根据 prompt 发言。

        Args:
            prompt: 发言上下文，包含轮次角色、问题等信息

        Returns:
            ExpertStatement: 专家发言内容
        """
        ...


class TemplateExpert(BaseExpert):
    """
    基于模板的专家实现，供快速原型使用。

    使用格式字符串生成发言内容，支持 {question}、{role} 等占位符。
    """

    def __init__(
        self,
        expert_id: str,
        name: str,
        description: str | None = None,
        template: str = "关于「{question}」，我的观点是……",
        trigger_keywords: list[str] | None = None,
        confidence: float = 0.7,
        is_methodology: bool = False,
    ):
        from ..types import ExpertId

        self._id = ExpertId(expert_id)
        self._name = name
        self._description = description or f"{name}专家"
        self._template = template
        self._trigger_keywords = tuple(trigger_keywords or [])
        self._confidence = confidence
        self._is_methodology = is_methodology

    @property
    def id(self) -> "ExpertId":
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def trigger_keywords(self) -> tuple[str, ...]:
        return self._trigger_keywords

    @property
    def is_methodology(self) -> bool:
        return self._is_methodology

    def speak(self, prompt: "SpeakPrompt") -> "ExpertStatement":
        from ..types import ExpertStatement, SpeakRole

        try:
            content = self._template.format(
                question=prompt.question,
                role=prompt.role.value if hasattr(prompt.role, "value") else prompt.role,
            )
        except Exception:
            content = self._template

        return ExpertStatement(
            expert_id=self._id,
            expert_name=self._name,
            role=prompt.role,
            content=content,
            confidence=self._confidence,
            elapsed_s=0.0,
        )


__all__ = ["BaseExpert", "TemplateExpert"]