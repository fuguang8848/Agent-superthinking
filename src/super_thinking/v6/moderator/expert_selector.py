"""
moderator/expert_selector.py - LLM驱动的专家选择

§2.5 动态专家池：主持人（LLM）根据问题语义选择专家，
而非关键词匹配。
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

from ..types import Expert, ExpertPool, ExpertId

if TYPE_CHECKING:
    from ..llm.provider import LLMProvider

logger = logging.getLogger(__name__)


# Expert domain taxonomy for LLM to reason about
_EXPERT_DOMAIN_PROMPT = """
## 专家池领域分类

可用专家（id | name | domain | keywords）：
{expert_list}

## 任务

用户问题是：「{question}」

请分析这个问题涉及哪些领域，选择最合适的2-4位专家参与辩论。

输出格式（JSON）：
{{
  "selected_experts": ["expert_id1", "expert_id2", ...],
  "reasoning": "简短说明为什么选择这些专家",
  "missing_perspectives": ["如果有缺失的视角，在这里说明"]
}}
"""


class LLMExpertSelector:
    """
    LLM驱动的专家选择器。

    替代 expert_pool.suggest_for() 的关键词匹配，
    改用LLM理解问题语义后选择专家。
    """

    def __init__(self, expert_pool: ExpertPool, llm: LLMProvider):
        self._pool = expert_pool
        self._llm = llm

    def select(
        self,
        question: str,
        *,
        min_experts: int = 2,
        max_experts: int = 6,
    ) -> tuple[Expert, ...]:
        """
        用LLM为给定问题选择最合适的专家组合。

        Args:
            question: 用户问题
            min_experts: 最少专家数（不够时用关键词补足）
            max_experts: 最多专家数

        Returns:
            选中的专家 tuple
        """
        registered = self._pool.list_registered()
        if not registered:
            return ()

        # 构建专家列表描述
        expert_lines = []
        for e in registered:
            expert_lines.append(
                f"- {e.id} | {e.name} | {getattr(e, 'domain', 'unknown')} | "
                f"keywords: {', '.join(getattr(e, 'trigger_keywords', []))}"
            )
        expert_list_text = "\n".join(expert_lines)

        # 请求LLM选择
        prompt = _EXPERT_DOMAIN_PROMPT.format(
            question=question,
            expert_list=expert_list_text,
        )

        try:
            response = self._llm.complete_json(
                prompt,
                system="你是一个专家选择助手。输出严格JSON格式。",
                schema={
                    "type": "object",
                    "properties": {
                        "selected_experts": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "reasoning": {"type": "string"},
                        "missing_perspectives": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["selected_experts"],
                },
            )
            selected_ids = response.get("selected_experts", [])
            reasoning = response.get("reasoning", "")
            logger.info(f"LLM expert selection: {selected_ids} — {reasoning}")

        except Exception as e:
            logger.warning(f"LLM expert selection failed, falling back to keyword: {e}")
            return self._fallback_keyword(question, min_experts, max_experts)

        # 映射ID到专家对象
        selected: list[Expert] = []
        id_to_expert = {str(e.id): e for e in registered}

        for eid in selected_ids:
            expert = id_to_expert.get(ExpertId(eid)) or id_to_expert.get(eid)
            if expert and expert not in selected:
                selected.append(expert)

        # 数量保护
        selected = selected[:max_experts]

        # 数量不足时用关键词补足
        if len(selected) < min_experts:
            fallback = self._fallback_keyword(question, min_experts, max_experts)
            for e in fallback:
                if e not in selected:
                    selected.append(e)
                    if len(selected) >= min_experts:
                        break

        return tuple(selected[:max_experts])

    def _fallback_keyword(
        self, question: str, min_experts: int, max_experts: int
    ) -> tuple[Expert, ...]:
        """关键词兜底选择"""
        scored: list[tuple[int, Expert]] = []
        question_lower = question.lower()
        for expert in self._pool.list_registered():
            score = sum(
                1 for kw in getattr(expert, "trigger_keywords", ())
                if kw.lower() in question_lower
            )
            scored.append((score, expert))
        scored.sort(key=lambda x: -x[0])
        return tuple(e for _, e in scored[:max_experts])


__all__ = ["LLMExpertSelector"]
