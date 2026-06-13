"""
LLM-powered Router that intelligently selects perspectives based on input.

Instead of keyword matching, this router uses an LLM to analyze the user's input
and select the most relevant perspectives from the registry.

Security fixes (v0.2.4):
- Prompt injection detection via AgentMemory check_injection
- Input sanitization: escape special chars, length limit 2000
- Recorder hooks for audit trail
"""

from __future__ import annotations

import json
import logging
import re
from typing import Callable, Optional

from super_thinking.core.router import Router, RoutingResult

logger = logging.getLogger(__name__)


# --- Prompt Injection Detection ---

def _get_agentmemory_check():
    """Lazily import and return check_injection from AgentMemory."""
    try:
        import sys
        from pathlib import Path

        # Navigate: llm_router.py -> core/ -> super_thinking/ -> src/ -> Agent-Superthinking/
        base = Path(__file__).resolve().parent.parent.parent.parent
        # AgentMemory is at workspace/AgentMemory/src/
        agentmemory_src = base.parent / "AgentMemory" / "src"

        if str(agentmemory_src) not in sys.path:
            sys.path.insert(0, str(agentmemory_src))

        from agent_memory.utils.injection import check_injection as _check
        return _check
    except Exception as e:
        logger.debug(f"[Security] AgentMemory check_injection unavailable: {e}")
        return None


def _check_prompt_injection(text: str) -> bool:
    """
    Check if text contains prompt injection patterns.
    Returns True if flagged (injection detected).
    """
    _check = _get_agentmemory_check()
    if _check is None:
        return False  # AgentMemory not available, skip check

    try:
        flagged, score, matched = _check(text)
        if flagged:
            logger.warning(f"[Security] Prompt injection detected: score={score}, patterns={matched}")
        return flagged
    except Exception as e:
        logger.debug(f"[Security] Injection check error: {e}")
        return False


def _sanitize_for_prompt(text: str, max_length: int = 2000) -> str:
    """
    Sanitize user input for safe insertion into LLM prompt.
    
    1. Truncate to max_length (prevent DOS)
    2. Escape triple backticks (prevent markdown code injection)
    3. Escape { and } in f-string-like contexts (prevent format injection)
    4. Escape [ and ] slightly (prevent JSON array injection within prompt)
    5. Normalize excessive newlines
    """
    if not text:
        return ""

    # 1. Length limit
    text = text[:max_length]

    # 2. Escape triple backticks (``` → ``` becomes a code fence)
    #    Replace with safe equivalent
    text = text.replace("```", "\u200b```\u200b")  # zero-width space breaks fence

    # 3. Escape { and } to prevent format string injection
    #    The prompt uses .format(), so {user_input} could inject keys
    text = text.replace("{", "{{").replace("}", "}}")

    # 4. Normalize excessive newlines (prevent spacing/truncation attacks)
    text = re.sub(r"\n{5,}", "\n\n\n", text)

    # 5. Strip control characters except newlines/tabs
    text = "".join(c for c in text if c >= " " or c in "\n\t")

    return text.strip()


# --- Recorder Hooks ---

RecorderHook = Callable[[dict], None]
"""Callback signature: called with event dict after each routing step."""


class Recorder:
    """
    Audit trail for routing decisions.
    
    Hooks can be registered to receive events:
    - route_start: when routing begins (input, mode)
    - route_complete: when routing finishes (result, duration_ms)
    - route_fallback: when falling back to auto mode (reason)
    - injection_detected: when prompt injection is flagged
    """

    def __init__(self):
        self._hooks: list[RecorderHook] = []

    def register(self, hook: RecorderHook) -> None:
        """Register a callback hook."""
        self._hooks.append(hook)

    def unregister(self, hook: RecorderHook) -> None:
        """Remove a registered hook."""
        self._hooks.remove(hook)

    def _emit(self, event: dict) -> None:
        """Emit event to all registered hooks."""
        for hook in self._hooks:
            try:
                hook(event)
            except Exception as e:
                logger.warning(f"[Recorder] Hook error: {e}")

    def record_route_start(self, input_text: str, mode: str) -> None:
        self._emit({"type": "route_start", "input_length": len(input_text), "mode": mode})

    def record_route_complete(self, result: RoutingResult, duration_ms: float) -> None:
        self._emit({
            "type": "route_complete",
            "activated_count": len(result.activated),
            "mode": result.mode,
            "duration_ms": round(duration_ms, 2),
        })

    def record_route_fallback(self, reason: str) -> None:
        self._emit({"type": "route_fallback", "reason": reason})

    def record_injection_detected(self, score: float, matched: list) -> None:
        self._emit({"type": "injection_detected", "score": score, "matched": matched})

    def record_jury_start(self, input_text: str, mode: str, selective_ids: Optional[list]) -> None:
        self._emit({
            "type": "jury_start",
            "input_length": len(input_text),
            "mode": mode,
            "selective_ids": selective_ids,
        })

    def record_jury_complete(self, result, duration_ms: float) -> None:
        self._emit({
            "type": "jury_complete",
            "total_perspectives": result.total_perspectives,
            "successful": result.successful,
            "failed": result.failed,
            "duration_ms": round(duration_ms, 2),
        })


# Default global recorder
_default_recorder: Optional[Recorder] = None


def get_recorder() -> Recorder:
    """Get the default recorder instance."""
    global _default_recorder
    if _default_recorder is None:
        _default_recorder = Recorder()
    return _default_recorder


# --- Shared Context ---

def _get_shared_context():
    """Get SharedContext singleton for LLM calls."""
    try:
        import sys
        from pathlib import Path

        # Navigate: llm_router.py -> core/ -> super_thinking/ -> src/ -> Agent-Superthinking/
        # Then up to workspace level, then down to AgentSymphony
        base = Path(__file__).resolve().parent.parent.parent.parent  # -> Agent-Superthinking/src/
        workspace = base.parent  # -> workspace/
        agent_symphony_path = workspace / "AgentSymphony"

        if not agent_symphony_path.exists():
            # Fallback: try same level
            agent_symphony_path = base / "AgentSymphony"

        if not agent_symphony_path.exists():
            return None

        if str(agent_symphony_path) not in sys.path:
            sys.path.insert(0, str(agent_symphony_path))

        from shared.context import get_context
        return get_context()
    except Exception:
        return None


# --- LLMRouter ---

class LLMRouter(Router):
    """
    LLM-powered router that selects perspectives intelligently.
    
    Uses the LLM to:
    1. Understand the user's problem/goal
    2. Select relevant perspectives based on their expertise
    3. Limit to a reasonable number (e.g., 6-9) to avoid overload

    Security (v0.2.4):
    - Prompt injection detection before LLM call
    - Input sanitization to prevent prompt breaking
    - Recorder hooks for audit trail
    """

    # Prompt template for LLM-based routing
    # NOTE: {input_text} is sanitized via _sanitize_for_prompt before insertion
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

    def __init__(
        self,
        registry=None,
        recorder: Optional[Recorder] = None,
        max_input_length: int = 2000,
        skip_injection_check: bool = False,
    ):
        super().__init__(registry)
        self._recorder = recorder
        self._max_input_length = max_input_length
        self._skip_injection_check = skip_injection_check

    @property
    def recorder(self) -> Recorder:
        """Lazy-load recorder."""
        if self._recorder is None:
            self._recorder = get_recorder()
        return self._recorder

    def route(
        self,
        input: str,
        mode: str = "llm",
        selective_ids: Optional[list[str]] = None,
    ) -> RoutingResult:
        """Route input to appropriate perspectives."""
        self.recorder.record_route_start(input, mode)

        if mode == "force_all":
            result = self._route_force_all()
        elif mode == "selective":
            result = self._route_selective(selective_ids or [])
        elif mode == "llm":
            result = self._route_llm(input)
        else:
            result = self._route_auto(input)

        self.recorder.record_route_complete(result, 0.0)  # duration tracked by caller ideally
        return result

    def _route_llm(self, input_text: str) -> RoutingResult:
        """Use LLM to intelligently select perspectives."""
        import time
        start_ms = time.time() * 1000

        # --- Security: Prompt Injection Check ---
        if not self._skip_injection_check:
            _check = _get_agentmemory_check()
            if _check is not None:
                try:
                    flagged, score, matched = _check(input_text)
                    if flagged:
                        logger.warning(
                            f"[Security] Prompt injection in routing input: "
                            f"score={score}, patterns={matched}"
                        )
                        self.recorder.record_injection_detected(score, matched)
                        # Fall back to auto routing instead of using poisoned input
                        self.recorder.record_route_fallback("injection_detected")
                        return self._route_auto(input_text)
                except Exception as e:
                    logger.debug(f"Injection check error: {e}")

        # --- Security: Sanitize input ---
        safe_input = _sanitize_for_prompt(input_text, self._max_input_length)

        ctx = _get_shared_context()

        # Build expert context
        enabled = self._registry.list_enabled()
        experts_context = self._build_experts_context(enabled)

        # Build prompt with sanitized input
        prompt = self.ROUTING_PROMPT.format(
            input_text=safe_input,
            total=len(enabled),
            categories=self.CATEGORY_SUMMARY,
            experts=experts_context,
        )

        # Call LLM
        if ctx is None:
            logger.warning("SharedContext not available, falling back to auto routing")
            self.recorder.record_route_fallback("no_shared_context")
            return self._route_auto(input_text)

        try:
            response = ctx.call_llm(
                prompt=prompt,
                system="你是一个专家选择助手，擅长根据用户需求选择最相关的专家。只返回JSON数组格式的专家ID列表。",
                max_tokens=2048,
            )

            # Parse JSON response
            selected = self._parse_llm_response(response)

            if not selected:
                logger.warning("LLM returned no valid perspectives, falling back to auto")
                self.recorder.record_route_fallback("llm_no_valid_response")
                return self._route_auto(input_text)

            # Validate selected IDs
            enabled_ids = {p.id for p in enabled}
            valid_selected = [pid for pid in selected if pid in enabled_ids]
            invalid = [pid for pid in selected if pid not in enabled_ids]

            if invalid:
                logger.warning(f"LLM selected unknown perspectives (skipping): {invalid}")

            if not valid_selected:
                self.recorder.record_route_fallback("llm_all_invalid")
                return self._route_auto(input_text)

            # Build scores
            scores = {pid: (1.0 if pid in valid_selected else 0.0) for pid in enabled_ids}

            duration_ms = time.time() * 1000 - start_ms
            self.recorder.record_route_complete(
                RoutingResult(
                    activated=valid_selected,
                    mode="llm",
                    reason=f"LLM智能选择：从{len(enabled)}个专家中选出了{len(valid_selected)}个",
                    scores=scores,
                ),
                duration_ms,
            )

            return RoutingResult(
                activated=valid_selected,
                mode="llm",
                reason=f"LLM智能选择：从{len(enabled)}个专家中选出了{len(valid_selected)}个",
                scores=scores,
            )

        except Exception as e:
            logger.warning(f"LLM routing failed ({e}), falling back to auto")
            self.recorder.record_route_fallback(str(e))
            return self._route_auto(input_text)

    def _build_experts_context(self, enabled) -> str:
        """Build expert context for LLM prompt."""
        lines = []

        # Group by category
        python_experts = []
        skill_experts = []

        for p in enabled:
            info = f"- {p.id}: {p.description[:100] if p.description else '无描述'}"
            if hasattr(p, "_skill_path"):
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
            response = response.strip()
            logger.info(f"[LLMRouter] Raw LLM response: {response[:500]}")

            # Handle markdown code blocks
            if response.startswith("```"):
                lines = response.split("\n")
                response = "\n".join(lines[1:-1])

            # Try JSON array first
            start = response.find("[")
            end = response.rfind("]")

            if start != -1 and end != -1 and end > start:
                json_str = response[start : end + 1]
                parsed = json.loads(json_str)
                if isinstance(parsed, list):
                    return [str(pid) for pid in parsed]

            # Fallback: try to extract IDs from plain text
            matches = re.findall(r'["\']?([a-zA-Z_][a-zA-Z0-9_-]*)["\']?', response)
            if matches:
                logger.info(f"[LLMRouter] Extracted IDs via regex: {matches}")
                return matches

            logger.warning(f"[LLMRouter] Could not parse response: {response[:200]}")
            return []
        except Exception as e:
            logger.warning(f"[LLMRouter] Parse error: {e}, response: {response[:200]}")
            return []
