"""
LLM Provider - LLM 调用接口
"""

from typing import Protocol, runtime_checkable, Any
import logging

logger = logging.getLogger(__name__)

@runtime_checkable
class LLMProvider(Protocol):
    """LLM 调用协议。"""
    
    def complete(self, prompt: str, *, system: str | None = None,
                 temperature: float = 0.2, max_tokens: int = 2000) -> str:
        """完成文本生成。"""
        ...
    
    def complete_json(self, prompt: str, *, system: str | None = None,
                      schema: dict | None = None) -> dict:
        """完成 JSON 结构化生成。"""
        ...


class DeterministicLLM:
    """确定性 LLM Provider，用于测试。"""
    
    def __init__(self, responses: dict[str, str] | None = None):
        self._responses = responses or {}
        self._call_count = 0
    
    def complete(self, prompt: str, *, system: str | None = None,
                 temperature: float = 0.2, max_tokens: int = 2000) -> str:
        self._call_count += 1
        if prompt in self._responses:
            return self._responses[prompt]
        return f"[Deterministic response {self._call_count}] {prompt[:50]}..."
    
    def complete_json(self, prompt: str, *, system: str | None = None,
                      schema: dict | None = None) -> dict:
        return {"result": "mock_json_response"}


class MockLLM:
    """Mock LLM Provider，返回预设响应。"""
    
    def __init__(self, default_response: str = "Mock response"):
        self._default = default_response
        self._call_history: list[dict] = []
    
    def complete(self, prompt: str, *, system: str | None = None,
                 temperature: float = 0.2, max_tokens: int = 2000) -> str:
        self._call_history.append({"prompt": prompt, "system": system})
        return self._default
    
    def complete_json(self, prompt: str, *, system: str | None = None,
                      schema: dict | None = None) -> dict:
        self._call_history.append({"prompt": prompt, "system": system, "schema": schema})
        return {"mock": True}
