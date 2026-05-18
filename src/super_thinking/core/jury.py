"""
Jury - orchestrates parallel execution of multiple perspectives.

Handles:
- Parallel invocation of all activated perspectives
- Timeout management per perspective
- Exception isolation (single perspective failure doesn't crash the system)
- Result collection and aggregation
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from dataclasses import dataclass
from typing import Optional, Any

from super_thinking.core.registry import Registry, get_registry
from super_thinking.core.router import Router, RoutingResult, get_router
from super_thinking.perspectives._interface import Perspective, PerspectiveOutput

logger = logging.getLogger(__name__)


@dataclass
class JuryResult:
    """Aggregated results from all perspectives."""

    outputs: dict[str, PerspectiveOutput]  # perspective_id -> output
    errors: dict[str, str]  # perspective_id -> error message
    routing_result: RoutingResult
    total_perspectives: int
    successful: int
    failed: int

    def get_outputs(self) -> list[PerspectiveOutput]:
        """Get list of successful outputs."""
        return list(self.outputs.values())

    def has_errors(self) -> bool:
        """Check if any perspective failed."""
        return len(self.errors) > 0

    def get_perspective_ids(self) -> list[str]:
        """Get all perspective IDs that were activated."""
        return list(self.outputs.keys()) + list(self.errors.keys())


class Jury:
    """Expert jury that coordinates multi-perspective analysis."""

    def __init__(
        self,
        registry: Optional[Registry] = None,
        router: Optional[Router] = None,
        timeout_per_perspective: float = 60.0,
        max_workers: int = 4,
    ):
        """
        Initialize the Jury.

        Args:
            registry: PerspectiveRegistry instance (creates default if None)
            router: Router instance (creates default if None)
            timeout_per_perspective: Max seconds per perspective (default 60s)
            max_workers: Max parallel perspective executions (default 4)
        """
        self._registry = registry
        self._router = router
        self.timeout_per_perspective = timeout_per_perspective
        self.max_workers = max_workers

    @property
    def registry(self) -> Registry:
        """Lazy-load registry."""
        if self._registry is None:
            self._registry = get_registry()
        return self._registry

    @property
    def router(self) -> Router:
        """Lazy-load router."""
        if self._router is None:
            self._router = get_router(self._registry)
        return self._router

    def think(
        self,
        input: str,
        context: Optional[dict[str, Any]] = None,
        mode: str = "auto",
        selective_ids: Optional[list[str]] = None,
    ) -> JuryResult:
        """Execute all activated perspectives and aggregate results.

        Args:
            input: User's question or problem statement
            context: Additional context to pass to each perspective
            mode: Routing mode - "auto", "force_all", or "selective"
            selective_ids: Specific perspective IDs to activate (for selective mode)

        Returns:
            JuryResult with all perspective outputs and error info
        """
        context = context or {}

        # Route to determine which perspectives to activate
        routing_result = self.router.route(
            input=input,
            mode=mode,
            selective_ids=selective_ids,
        )

        logger.info(
            f"Jury: {len(routing_result.activated)} perspectives activated "
            f"({routing_result.mode}): {routing_result.activated}"
        )

        # Collect perspectives
        perspectives: list[Perspective] = []
        for pid in routing_result.activated:
            p = self.registry.get(pid)
            if p is not None:
                perspectives.append(p)
            else:
                logger.warning(f"Perspective not found: {pid}")

        # Execute in parallel with timeout and error isolation
        outputs: dict[str, PerspectiveOutput] = {}
        errors: dict[str, str] = {}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_pid = {
                executor.submit(self._execute_perspective, p, input, context): p.id
                for p in perspectives
            }

            for future in future_to_pid:
                pid = future_to_pid[future]
                try:
                    result = future.result(timeout=self.timeout_per_perspective)
                    if result is not None:
                        outputs[pid] = result
                except FuturesTimeoutError:
                    errors[pid] = f"Timeout after {self.timeout_per_perspective}s"
                    logger.warning(f"Perspective {pid} timed out")
                except Exception as e:
                    errors[pid] = str(e)
                    logger.warning(f"Perspective {pid} failed: {e}")

        return JuryResult(
            outputs=outputs,
            errors=errors,
            routing_result=routing_result,
            total_perspectives=len(perspectives),
            successful=len(outputs),
            failed=len(errors),
        )

    def _execute_perspective(
        self,
        perspective: Perspective,
        input: str,
        context: dict[str, Any],
    ) -> PerspectiveOutput:
        """Execute a single perspective (wrapped for error handling)."""
        return perspective.think(input, context)

    def convene(
        self,
        perspective_ids: list[str],
        input: str,
        context: Optional[dict[str, Any]] = None,
    ) -> list[PerspectiveOutput]:
        """Execute specified perspectives and return their outputs.

        Args:
            perspective_ids: List of perspective IDs to activate
            input: User's question or problem statement
            context: Additional context to pass to each perspective

        Returns:
            List of PerspectiveOutput from each perspective
        """
        context = context or {}
        outputs: list[PerspectiveOutput] = []

        for pid in perspective_ids:
            p = self.registry.get(pid)
            if p is not None:
                try:
                    output = p.think(input, context)
                    outputs.append(output)
                except Exception as e:
                    logger.warning(f"Perspective {pid} failed during convene: {e}")

        return outputs


def get_jury(
    registry: Optional[Registry] = None,
    router: Optional[Router] = None,
) -> Jury:
    """Get a Jury instance."""
    return Jury(registry=registry, router=router)


# Convenience function for simple usage
def think(
    input: str,
    context: Optional[dict[str, Any]] = None,
    mode: str = "auto",
    selective_ids: Optional[list[str]] = None,
) -> JuryResult:
    """
    One-shot jury thinking.

    Example:
        result = think("Should I invest in AI?", mode="force_all")
        for output in result.get_outputs():
            print(f"{output.perspective_name}: {output.analysis}")
    """
    jury = get_jury()
    return jury.think(input, context, mode, selective_ids)
