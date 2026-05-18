"""
LLM-powered Router that intelligently selects perspectives based on input.

Instead of keyword matching, this router uses an LLM to analyze the user's input
and select the most relevant perspectives from the registry.
"""

from __future__ import annotations

import json
import logging
from typing import Optional

from super_thinking.core.router import Router, RoutingResult

logger = logging.getLogger(__name__)


def _get_shared_context():
    """Get SharedContext singleton for LLM calls."""
    try:
        import sys
        from pathlib import Path
        
        agent_symphony_path = Path(__file__).parent.parent.parent.parent / "agent-symphony"
        if str(agent_symphony_path) not in sys.path:
            sys.path.insert(0, str(agent_symphony_path))
        
        from shared.context import get_context
        return get_context()
    except Exception:
        return None


class LLMRouter(Router):
    """
    LLM-powered router that selects perspectives intelligently.
    
    Uses the LLM to:
    1. Understand the user's problem/goal
    2. Select relevant perspectives based on their expertise
    3. Limit to a reasonable number (e.g., 6-9) to avoid overload
    """
    
    # Prompt template for LLM-based routing
    ROUTING_PROMPT = """你是一个专家选择助手。用户的需求如下：

---
{input_text}
---

专家库中有 {total} 个专家，分布在以下类别：
{categories}

专家详情：
{experts}

请选择最相关的专家来帮助分析这个需求。

要求：
1. 选择 6-9 个专家，确保覆盖不同思维角度
2. 优先选择与需求高度相关的专家
3. 至少包含一个批判性/风险类专家
4. 返回格式：JSON数组，只包含专家ID

只返回JSON数组，不要其他内容。格式示例：
["expert_id_1", "expert_id_2", "expert_id_3"]
"""

    CATEGORY_SUMMARY = """- philosophy: 苏格拉底、柏拉图、亚里士多德、康德等哲学家
- science: 达尔文、爱因斯坦、波尔、居里夫人等科学家  
- psychology: 弗洛伊德、荣格、罗杰斯等心理学家
- economics: 哈耶克、凯恩斯、斯密、稻盛和夫等经济学家
- literature: 莎士比亚、托尔斯泰、海明威等文学家
- military: 克劳塞维茨、孙子等军事家
- methods: 贝叶斯、复杂性、设计思维、系统思维、信息论等方法论
- frameworks: 博弈论、网络效应等框架
- python_experts: stakeholder(利益相关者)、meta_thinking(元思考)、risk_detail(风险)、magi_debate(辩论)、doubt(怀疑)、past_experience(过往经验)、verification(验证)等内置专家"""

    def route(self, input: str, mode: str = "llm", selective_ids: Optional[list[str]] = None) -> RoutingResult:
        """
        Route input to appropriate perspectives.
        
        Args:
            input: User's question or problem statement
            mode: Routing mode - "llm", "auto", "force_all", or "selective"
            selective_ids: List of perspective IDs (for selective mode)
        
        Returns:
            RoutingResult with activated perspectives and metadata
        """
        if mode == "force_all":
            return self._route_force_all()
        elif mode == "selective":
            return self._route_selective(selective_ids or [])
        elif mode == "llm":
            return self._route_llm(input)
        else:
            # Fallback to auto keyword matching
            return self._route_auto(input)
    
    def _route_llm(self, input_text: str) -> RoutingResult:
        """
        Use LLM to intelligently select perspectives.
        
        This method:
        1. Builds context with all available perspectives
        2. Calls LLM to select the most relevant ones
        3. Returns RoutingResult with selected perspective IDs
        """
        ctx = _get_shared_context()
        
        # Build expert context
        enabled = self._registry.list_enabled()
        experts_context = self._build_experts_context(enabled)
        
        # Build prompt
        prompt = self.ROUTING_PROMPT.format(
            input_text=input_text,
            total=len(enabled),
            categories=self.CATEGORY_SUMMARY,
            experts=experts_context
        )
        
        # Call LLM
        if ctx is None:
            logger.warning("SharedContext not available, falling back to auto routing")
            return self._route_auto(input_text)
        
        try:
            response = ctx.call_llm(
                prompt=prompt,
                system="你是一个专家选择助手，擅长根据用户需求选择最相关的专家。只返回JSON数组格式的专家ID列表。",
                max_tokens=512
            )
            
            # Parse JSON response
            selected = self._parse_llm_response(response)
            
            if not selected:
                logger.warning("LLM returned no valid perspectives, falling back to auto")
                return self._route_auto(input_text)
            
            # Validate selected IDs
            enabled_ids = {p.id for p in enabled}
            valid_selected = [pid for pid in selected if pid in enabled_ids]
            invalid = [pid for pid in selected if pid not in enabled_ids]
            
            if invalid:
                logger.warning(f"LLM selected unknown perspectives (skipping): {invalid}")
            
            if not valid_selected:
                return self._route_auto(input_text)
            
            # Build scores
            scores = {pid: (1.0 if pid in valid_selected else 0.0) for pid in enabled_ids}
            
            return RoutingResult(
                activated=valid_selected,
                mode="llm",
                reason=f"LLM智能选择：从{len(enabled)}个专家中选出了{len(valid_selected)}个",
                scores=scores
            )
            
        except Exception as e:
            logger.warning(f"LLM routing failed ({e}), falling back to auto")
            return self._route_auto(input_text)
    
    def _build_experts_context(self, enabled) -> str:
        """Build expert context for LLM prompt."""
        lines = []
        
        # Group by category
        python_experts = []
        skill_experts = []
        
        for p in enabled:
            info = f"- {p.id}: {p.description[:100] if p.description else '无描述'}"
            if hasattr(p, '_skill_path'):
                skill_experts.append(info)
            else:
                python_experts.append(info)
        
        if python_experts:
            lines.append("【内置专家（Python）】")
            lines.extend(python_experts[:20])  # Limit to avoid too long prompt
        
        if skill_experts:
            lines.append("\n【SKILL.md专家】")
            lines.extend(skill_experts)
        
        return "\n".join(lines)
    
    def _parse_llm_response(self, response: str) -> list[str]:
        """Parse LLM response to extract perspective IDs."""
        try:
            # Try to find JSON array in response
            response = response.strip()
            
            # Handle cases where LLM wraps JSON in markdown code blocks
            if response.startswith("```"):
                lines = response.split("\n")
                response = "".join(lines[1:-1])  # Remove ```json and ```
            
            # Find JSON array
            start = response.find("[")
            end = response.rfind("]")
            
            if start != -1 and end != -1 and end > start:
                json_str = response[start:end+1]
                parsed = json.loads(json_str)
                if isinstance(parsed, list):
                    return [str(pid) for pid in parsed]
            
            return []
        except Exception as e:
            logger.warning(f"Failed to parse LLM response: {e}")
            return []
