"""
OpenAI-compatible LLM Provider

Provides a drop-in OpenAI-compatible LLM provider.
"""

from __future__ import annotations

import os
import logging
from typing import Any

from .provider import LLMProvider

logger = logging.getLogger(__name__)


class OpenAICompatProvider:
    """
    OpenAI-compatible LLM provider.

    Supports any OpenAI-compatible API endpoint (local or hosted).
    Automatically uses environment variables for configuration.

    Environment variables:
        OPENAI_API_KEY     - API key (default: "dummy" for local servers)
        OPENAI_BASE_URL    - Base URL (default: "http://localhost:8000")
        OPENAI_MODEL       - Model name (default: "gpt-4o-mini")
        OPENAI_TIMEOUT_S   - Request timeout in seconds (default: 60.0)

    Implements the LLMProvider protocol.
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout_s: float = 60.0,
        default_temperature: float = 0.2,
        default_max_tokens: int = 2000,
    ):
        try:
            import openai
        except ImportError:
            raise ImportError(
                "openai package is required for OpenAICompatProvider. "
                "Install it with: pip install openai"
            )

        self._api_key = api_key or os.environ.get("OPENAI_API_KEY", "dummy")
        self._base_url = base_url or os.environ.get("OPENAI_BASE_URL", "http://localhost:8000")
        self._model = model or os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        self._timeout_s = float(os.environ.get("OPENAI_TIMEOUT_S", timeout_s))
        self._default_temperature = default_temperature
        self._default_max_tokens = default_max_tokens

        self._client = openai.OpenAI(
            api_key=self._api_key,
            base_url=self._base_url,
            timeout=self._timeout_s,
        )
        logger.info(f"OpenAICompatProvider initialized: model={self._model}, base_url={self._base_url}")

    def complete(
        self,
        prompt: str,
        *,
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """
        Send a completion request to the LLM.

        Args:
            prompt: The user prompt
            system: Optional system prompt
            temperature: Sampling temperature (0.0–2.0), or None for default
            max_tokens: Maximum tokens to generate, or None for default

        Returns:
            The generated text response.
        """
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=temperature if temperature is not None else self._default_temperature,
            max_tokens=max_tokens if max_tokens is not None else self._default_max_tokens,
        )
        return response.choices[0].message.content or ""

    def complete_json(
        self,
        prompt: str,
        *,
        system: str | None = None,
        schema: dict | None = None,
    ) -> dict:
        """
        Send a JSON-mode completion request.

        Args:
            prompt: The user prompt
            system: Optional system prompt
            schema: Optional JSON schema to enforce (provider-specific)

        Returns:
            Parsed JSON response as a dict.
        """
        import json

        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        extra_kwargs: dict[str, Any] = {}
        if schema:
            extra_kwargs["response_format"] = schema

        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=0.1,
            max_tokens=1500,
            **extra_kwargs,
        )
        raw = response.choices[0].message.content or "{}"
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON response, returning empty dict")
            return {}

    def __repr__(self) -> str:
        return f"OpenAICompatProvider(model={self._model!r}, base_url={self._base_url!r})"


# Make it available from the llm package
from .provider import LLMProvider

__all__ = ["OpenAICompatProvider", "LLMProvider"]
