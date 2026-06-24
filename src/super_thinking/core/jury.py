"""
Jury - orchestrates parallel execution of multiple perspectives.

Handles:
- Parallel invocation of all activated perspectives
- Timeout management per perspective
- Exception isolation (single perspective failure doesn't crash the system)
- Result collection and aggregation
- ContextBoard-based layered collaboration (think_with_board)
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from dataclasses import dataclass, field
from typing import Optional, Any

from super_thinking.core.registry import Registry, get_registry
from super_thinking.core.router import Router, RoutingResult, get_router
from super_thinking.core.llm_router import Recorder, get_recorder
from super_thinking.perspectives._interface import Perspective, PerspectiveOutput
from super_thinking.team import ContextBoard, TeamIntegration, ExpertStatus

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
    # 2026-06-18 V 修: 加 analysis_metadata 字段 (报告 P0 bug: super_brain.py:174 调用 .get('experts_used') AttributeError)
    analysis_metadata: dict[str, Any] = field(default_factory=dict)

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
        recorder: Optional[Recorder] = None,
    ):
        """
        Initialize the Jury.

        Args:
            registry: PerspectiveRegistry instance (creates default if None)
            router: Router instance (creates default if None)
            timeout_per_perspective: Max seconds per perspective (default 60s)
            max_workers: Max parallel perspective executions (default 4)
            recorder: Recorder instance for audit hooks (creates default if None)
        """
        self._registry = registry
        self._router = router
        self.timeout_per_perspective = timeout_per_perspective
        self.max_workers = max_workers
        self._recorder = recorder

    @property
    def registry(self) -> Registry:
        """Lazy-load registry with auto-discovery."""
        if self._registry is None:
            self._registry = get_registry()
            self._registry.discover()  # 确保专家被加载
        return self._registry

    @property
    def router(self) -> Router:
        """Lazy-load router."""
        if self._router is None:
            self._router = get_router(self._registry)
        return self._router

    @property
    def recorder(self) -> Recorder:
        """Lazy-load recorder."""
        if self._recorder is None:
            self._recorder = get_recorder()
        return self._recorder

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
        import time
        start_ms = time.time() * 1000
        context = context or {}

        # Input validation
        if len(input) > 10000:
            input = input[:10000]
            logger.warning("Jury: input truncated to 10000 chars")

        self.recorder.record_jury_start(input, mode, selective_ids)

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

        result = JuryResult(
            outputs=outputs,
            errors=errors,
            routing_result=routing_result,
            total_perspectives=len(perspectives),
            successful=len(outputs),
            failed=len(errors),
            # 2026-06-18 V 修: 填 experts_used (从 routing_result.activated 取视角 ID 列表)
            analysis_metadata={"experts_used": list(routing_result.activated)},
        )
        duration_ms = time.time() * 1000 - start_ms
        self.recorder.record_jury_complete(result, duration_ms)
        return result

    def _execute_perspective(
        self,
        perspective: Perspective,
        input: str,
        context: dict[str, Any],
    ) -> PerspectiveOutput:
        """Execute a single perspective (wrapped for error handling)."""
        return perspective.think(input, context)

    def think_with_board(
        self,
        input: str,
        context: Optional[dict[str, Any]] = None,
        mode: str = "auto",
        selective_ids: Optional[list[str]] = None,
        execution_layers: Optional[dict[str, int]] = None,
        board: Optional[ContextBoard] = None,
    ) -> JuryResult:
        """Execute perspectives with ContextBoard collaboration.

        Experts execute layer by layer. Later layers can read insights
        published by earlier layers before publishing their own.

        Args:
            input: User's question or problem statement
            context: Additional context to pass to each perspective
            mode: Routing mode - "auto", "force_all", or "selective"
            selective_ids: Specific perspective IDs to activate
            execution_layers: Optional mapping of perspective_id -> layer number.
                              Lower layers execute first. Defaults to all layer 0.
            board: Optional shared ContextBoard. Creates new one if None.

        Returns:
            JuryResult with all perspective outputs and error info

        Example:
            jury = Jury()
            board = ContextBoard()
            layers = {"meta_thinking": 0, "risk_detail": 0, "buffett": 1}
            result = jury.think_with_board(
                "Should I invest in Tesla?",
                execution_layers=layers,
                board=board
            )
        """
        context = context or {}

        # Route to determine which perspectives to activate
        routing_result = self.router.route(
            input=input,
            mode=mode,
            selective_ids=selective_ids,
        )

        if not routing_result.activated:
            logger.warning("No perspectives activated in think_with_board")
            return JuryResult(
                outputs={},
                errors={},
                routing_result=routing_result,
                total_perspectives=0,
                successful=0,
                failed=0,
            )

        # Use provided board or create new one
        collaboration_board = board or ContextBoard()
        integration = TeamIntegration(collaboration_board)

        # Determine layers
        if execution_layers is None:
            execution_layers = {pid: 0 for pid in routing_result.activated}

        # Group perspectives by layer
        layers: dict[int, list[str]] = {}
        for pid in routing_result.activated:
            layer = execution_layers.get(pid, 0)
            layers.setdefault(layer, []).append(pid)

        layer_order = sorted(layers.keys())
        logger.info(
            f"[think_with_board] {len(routing_result.activated)} perspectives in "
            f"{len(layer_order)} layers: {layers}"
        )

        # Collect perspectives
        perspective_map: dict[str, Perspective] = {}
        for pid in routing_result.activated:
            p = self.registry.get(pid)
            if p is not None:
                perspective_map[pid] = p
            else:
                logger.warning(f"Perspective not found: {pid}")

        # Register all experts on the board
        for pid, layer in execution_layers.items():
            if pid in perspective_map:
                integration.register_expert(pid, layer=layer)

        outputs: dict[str, PerspectiveOutput] = {}
        errors: dict[str, str] = {}

        # Execute layer by layer
        for layer in layer_order:
            pids_this_layer = layers[layer]
            logger.info(f"[think_with_board] Executing layer {layer}: {pids_this_layer}")

            # Build context with previous layers' insights
            layer_context = dict(context)
            layer_context["_board_insights"] = integration.get_insights_for("_synthetic")
            layer_context["_board_version"] = collaboration_board.version

            # Execute all perspectives in this layer in parallel
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_pid = {
                    executor.submit(
                        self._execute_perspective_with_board,
                        perspective_map[pid],
                        pid,
                        input,
                        layer_context,
                        collaboration_board,
                    ): pid
                    for pid in pids_this_layer
                    if pid in perspective_map
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

            # Mark concluded perspectives in this layer
            for pid in pids_this_layer:
                if pid in outputs:
                    integration.publish_concluded(pid)
                elif pid not in errors:
                    # Error already recorded
                    pass

        return JuryResult(
            outputs=outputs,
            errors=errors,
            routing_result=routing_result,
            total_perspectives=len(perspective_map),
            successful=len(outputs),
            failed=len(errors),
        )

    def _execute_perspective_with_board(
        self,
        perspective: Perspective,
        pid: str,
        input: str,
        context: dict[str, Any],
        board: ContextBoard,
    ) -> PerspectiveOutput:
        """Execute a single perspective with board awareness."""
        # Get current insights before executing
        insights_before = board.get_visible_insights(pid)

        # Add board context to perspective context
        exec_context = dict(context)
        exec_context["_board_insights"] = insights_before
        exec_context["_board_expert_id"] = pid

        # Mark as reviewing other insights
        board.publish_insight(pid, "", status=ExpertStatus.REVIEWING)

        # Execute the perspective
        output = perspective.think(input, exec_context)

        # If the perspective returned useful analysis, publish it
        if output and output.analysis:
            board.publish_insight(pid, output.analysis, status=ExpertStatus.REVIEWING)

        return output

    def think_complex(
        self,
        question: str,
        user_id: str = "default",
        team: Optional[Any] = None,
        learnings: Optional[Any] = None,
    ) -> dict[str, Any]:
        """复合 API: 问题分解 + 多专家评审 + 团队/学习集成。

        v6 升级补充 (V 2026-06-24):
        - 问题分解走 SupervisorAdapter (生成子任务 DAG)
        - 多专家评审走 think_with_board (ContextBoard 协作)
        - team / learnings 集成: 接到 profile 信号 (如果提供)

        Args:
            question: 用户问题
            user_id: 用户身份 (用于 ProfileManager 选择专家)
            team: TeamIntegration 实例 (可选, 用于 ContextBoard 协作)
            learnings: LearningsIntegration 实例 (可选, 用于历史经验)

        Returns:
            {
                "decomposed_plan": {
                    "subtasks": [ExpertSubTask, ...],
                    "question_type": str,
                    "complexity": str,
                    "execution_layers": [[pid, ...], ...],
                    "key_angles": [str, ...],
                    "warnings": [str, ...],
                    "synthesis_prompt": str,
                },
                "perspective_outputs": {pid: PerspectiveOutput, ...},
                "synthesis": str,  # 预留接口, 当前未实现综合
                "meta": {
                    "user_id": str,
                    "timestamp": str,
                    "method": "think_complex",
                }
            }

        Note:
            这是 v6 接口, 之前仅在 Jury.think_with_board 单独路径上。
            test_v6_smoke.py 的 test_02 / test_04 依赖此方法存在。
        """
        from datetime import datetime
        from super_thinking.orchestrator import SupervisorAdapter

        # 1. 问题分解
        adapter = SupervisorAdapter()
        decomposed = adapter.decompose(question, user_id=user_id)

        # 2. 提取专家 ID + 构建 layers
        expert_ids = [t.expert_id for t in decomposed.subtasks if hasattr(t, 'expert_id')]
        if not expert_ids:
            # fallback: 从 key_angles 提取
            expert_ids = decomposed.key_angles[:5] if decomposed.key_angles else ["meta_thinking"]

        execution_layers = decomposed.execution_layers
        if not execution_layers:
            # fallback: 单层
            execution_layers = [expert_ids]

        # 3. ContextBoard 协作评审
        from super_thinking.team import ContextBoard
        board = team.board if team and hasattr(team, 'board') else ContextBoard()

        result = self.think_with_board(
            input=question,
            board=board,
            execution_layers={pid: layer_idx for layer_idx, layer in enumerate(execution_layers) for pid in layer},
        )

        # 4. learnings 信号 (如果提供)
        learnings_signal = None
        if learnings and hasattr(learnings, 'get_recommendation'):
            try:
                learnings_signal = learnings.get_recommendation(
                    question=question,
                    question_type=decomposed.question_type,
                )
            except Exception as e:
                logger.debug(f"[think_complex] learnings 集成跳过: {e}")

        # 5. 返回结构
        return {
            "decomposed_plan": {
                "subtasks": [
                    {
                        "id": t.id,
                        "expert_id": getattr(t, 'expert_id', None),
                        "focus": getattr(t, 'focus', ''),
                        "depends_on": getattr(t, 'depends_on', []),
                        "priority": getattr(t, 'priority', 0),
                    }
                    for t in decomposed.subtasks
                ],
                "question_type": decomposed.question_type,
                "complexity": decomposed.complexity.value if hasattr(decomposed.complexity, 'value') else str(decomposed.complexity),
                "execution_layers": execution_layers,
                "key_angles": decomposed.key_angles,
                "warnings": decomposed.warnings,
                "synthesis_prompt": decomposed.synthesis_prompt,
            },
            "perspective_outputs": {
                pid: {
                    "analysis": out.analysis if out else "",
                    "confidence": getattr(out, 'confidence', 0.0) if out else 0.0,
                }
                for pid, out in (result.outputs.items() if result else {})
            },
            "synthesis": "",  # 预留: 后续可加综合阶段
            "learnings_signal": learnings_signal,
            "meta": {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "method": "think_complex",
            },
        }

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
