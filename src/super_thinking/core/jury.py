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
from datetime import datetime
from typing import Optional, Any

from super_thinking.core.registry import Registry, get_registry
from super_thinking.core.router import Router, RoutingResult, get_router
from super_thinking.perspectives._interface import Perspective, PerspectiveOutput

# v6 新增组件
from super_thinking.orchestrator import SupervisorAdapter, DecomposedQuestion
from super_thinking.team import TeamIntegration
from super_thinking.learnings import LearningsIntegration

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
    followup_prompt: Optional[str] = None  # Feedback collection prompt
    analysis_metadata: Optional[dict] = None  # Experts used, question type, etc.
    team_context: Optional[str] = None  # Team collaboration context from TeamIntegration

    def get_outputs(self) -> list[PerspectiveOutput]:
        """Get list of successful outputs."""
        return list(self.outputs.values())

    def has_errors(self) -> bool:
        """Check if any perspective failed."""
        return len(self.errors) > 0

    def get_perspective_ids(self) -> list[str]:
        """Get all perspective IDs that were activated."""
        return list(self.outputs.keys()) + list(self.errors.keys())

    def get_experts_used(self) -> list[str]:
        """Extract expert names from all perspective outputs."""
        experts = []
        for output in self.outputs.values():
            if hasattr(output, "perspective_name") and output.perspective_name:
                experts.append(output.perspective_name)
        return experts


class Jury:
    """Expert jury that coordinates multi-perspective analysis."""

    def __init__(
        self,
        registry: Optional[Registry] = None,
        router: Optional[Router] = None,
        profile_manager: Optional[Any] = None,
        feedback_collector: Optional[Any] = None,
        team_integration: Optional[Any] = None,
        timeout_per_perspective: float = 60.0,
        max_workers: int = 4,
    ):
        """
        Initialize the Jury.

        Args:
            registry: PerspectiveRegistry instance (creates default if None)
            router: Router instance (creates default if None)
            profile_manager: ProfileManager instance for user profile support (default: None)
            feedback_collector: FeedbackCollector instance for feedback collection (default: None)
            team_integration: TeamIntegration instance for multi-expert collaboration (default: None)
            timeout_per_perspective: Max seconds per perspective (default 60s)
            max_workers: Max parallel perspective executions (default 4)
        """
        self._registry = registry
        self._router = router
        self._profile_manager = profile_manager
        self._feedback_collector = feedback_collector
        self._team_integration = team_integration
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
            self._router = get_router(self._registry, self._profile_manager)
        return self._router

    @property
    def team(self) -> Any:
        """Lazy-load or create team integration."""
        if self._team_integration is None:
            from super_thinking.team.team_integration import TeamIntegration
            self._team_integration = TeamIntegration()
        return self._team_integration

    def think(
        self,
        input: str,
        context: Optional[dict[str, Any]] = None,
        mode: str = "auto",
        selective_ids: Optional[list[str]] = None,
        user_id: Optional[str] = None,
    ) -> JuryResult:
        """Execute all activated perspectives and aggregate results.

        Args:
            input: User's question or problem statement
            context: Additional context to pass to each perspective
            mode: Routing mode - "auto", "force_all", or "selective"
            selective_ids: Specific perspective IDs to activate (for selective mode)
            user_id: Optional user ID for profile-aware routing and feedback tracking

        Returns:
            JuryResult with all perspective outputs, error info, followup prompt, and team context
        """
        context = context or {}

        # Route to determine which perspectives to activate
        routing_result = self.router.route(
            input=input,
            mode=mode,
            selective_ids=selective_ids,
            user_id=user_id,
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

        # Register with team integration (for collaboration tracking)
        if self._team_integration is not None:
            expert_names = [p.name for p in perspectives]
            self.team.register_experts(expert_names)
            self.team.publish_start(
                expert_name="SYSTEM",
                perspective_id="jury",
                title=f"分析开始：{input[:50]}...",
            )

        # Execute in parallel with timeout and error isolation
        outputs: dict[str, PerspectiveOutput] = {}
        errors: dict[str, str] = {}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_pid = {
                executor.submit(
                    self._execute_perspective_team,
                    p, input, context, self.team if self._team_integration else None
                ): p.id
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

        # Build analysis metadata
        analysis_metadata = self._build_analysis_metadata(
            routing_result, outputs, input, user_id
        )

        # Generate followup feedback prompt
        followup_prompt = None
        if self._feedback_collector is not None:
            try:
                followup_prompt = self._feedback_collector.get_prompt_template()
            except Exception:
                pass

        # Team context for synthesis
        team_context = None
        if self._team_integration is not None:
            self.team.publish_concluded(
                "SYSTEM",
                [f"分析完成：{len(outputs)}/{len(perspectives)} 视角成功"]
            )
            team_context = self.team.get_full_context()

        return JuryResult(
            outputs=outputs,
            errors=errors,
            routing_result=routing_result,
            total_perspectives=len(perspectives),
            successful=len(outputs),
            failed=len(errors),
            followup_prompt=followup_prompt,
            analysis_metadata=analysis_metadata,
            team_context=team_context,
        )

    def _build_analysis_metadata(
        self,
        routing_result: RoutingResult,
        outputs: dict[str, PerspectiveOutput],
        input: str,
        user_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Build metadata about the analysis for feedback tracking."""
        # Extract expert names from outputs
        experts_used = []
        for output in outputs.values():
            if hasattr(output, "perspective_name") and output.perspective_name:
                experts_used.append(output.perspective_name)

        # Classify question type if profile manager is available
        question_type = "通用问题"
        if self._profile_manager is not None and user_id:
            try:
                question_type = self._profile_manager.classify_question(input)
            except Exception:
                pass

        return {
            "question": input,
            "question_type": question_type,
            "experts_used": experts_used,
            "routing_mode": routing_result.mode,
            "profile_applied": (
                routing_result.routing_recommendation.get("profile_applied", False)
                if routing_result.routing_recommendation
                else False
            ),
        }

    def submit_feedback(
        self,
        user_id: str,
        feedback_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Submit user feedback and update profile.

        Args:
            user_id: User ID
            feedback_data: Feedback data from user

        Returns:
            Updated profile summary
        """
        if self._profile_manager is None or self._feedback_collector is None:
            return {"updated": False, "reason": "Profile system not initialized"}

        try:
            # Ensure profile exists
            profile = self._profile_manager.get_profile(user_id)

            # Collect and validate feedback
            analysis_result = feedback_data.get("analysis_metadata", {})
            user_response = feedback_data.get("user_response", "")

            feedback = self._feedback_collector.collect(analysis_result, user_response)

            if not self._feedback_collector.validate(feedback):
                return {"updated": False, "reason": "Invalid feedback data"}

            # Update profile
            updated_profile = self._profile_manager.update_profile(user_id, feedback)

            return {
                "updated": True,
                "question_type": feedback.get("question_type"),
                "rating": feedback.get("rating"),
                "experts_useful": feedback.get("useful_experts", []),
                "experts_missing": feedback.get("missing_experts", []),
            }
        except Exception as e:
            logger.warning(f"Failed to submit feedback: {e}")
            return {"updated": False, "reason": str(e)}

    def _execute_perspective(
        self,
        perspective: Perspective,
        input: str,
        context: dict[str, Any],
    ) -> PerspectiveOutput:
        """Execute a single perspective (wrapped for error handling)."""
        return perspective.think(input, context)

    def _execute_perspective_team(
        self,
        perspective: Perspective,
        input: str,
        context: dict[str, Any],
        team: Any,
    ) -> PerspectiveOutput:
        """Execute a single perspective with team collaboration awareness."""
        from super_thinking.team.team_integration import ExpertPhase

        if team is not None:
            # Publish that this expert is thinking
            team.publish_start(
                expert_name=perspective.name,
                perspective_id=perspective.id,
                title=f"{perspective.name} 视角分析中...",
            )

            # Inject other experts' conclusions into context (if any)
            other_insights = team.get_other_insights(
                exclude=perspective.name,
                phases=[ExpertPhase.CONCLUDED],
            )
            if other_insights:
                # Add other insights to context for collaborative deepending
                context = {**context, "_other_insights": other_insights}

            try:
                output = perspective.think(input, context)
                # Publish conclusions
                conclusions = []
                if hasattr(output, "analysis") and output.analysis:
                    # Extract key sentences as conclusions
                    lines = output.analysis.split("\n")
                    for line in lines:
                        if line.startswith("**") or line.startswith("##"):
                            conclusions.append(line.strip("#* "))
                    conclusions = conclusions[:5]  # Top 5 conclusions
                team.publish_concluded(
                    perspective.name,
                    conclusions if conclusions else [output.analysis[:200]] if hasattr(output, "analysis") else [],
                )
                return output
            except Exception as e:
                team.publish_concluded(perspective.name, [f"分析失败: {str(e)}"])
                raise
        else:
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

    # ==================== v6: Complex Problem Solving ====================

    def think_complex(
        self,
        question: str,
        user_id: Optional[str] = None,
        team: Optional[TeamIntegration] = None,
        learnings: Optional[LearningsIntegration] = None,
    ) -> dict[str, Any]:
        """
        Solve complex problems using Supervisor decomposition + Team collaboration.

        This is the v6 "Super Brain" mode:
        1. SupervisorAdapter decomposes the problem into expert subtask DAG
        2. TeamIntegration enables multi-expert collaboration
        3. LearningsIntegration captures experience for future optimization

        Args:
            question: The complex question to analyze
            user_id: Optional user ID for profile-aware routing
            team: Optional TeamIntegration instance (creates new one if None)
            learnings: Optional LearningsIntegration instance (creates new one if None)

        Returns:
            dict with keys: decomposed_plan, team_session, synthesis, learnings_summary
        """
        # 1. Decompose using SupervisorAdapter
        supervisor = SupervisorAdapter(self._profile_manager)
        plan = supervisor.decompose(question, user_id=user_id)

        # 2. Setup team collaboration
        if team is None:
            expert_names = [st.expert_name for st in plan.subtasks]
            team = TeamIntegration(session_id=f"supthink_{datetime.now().strftime('%H%M%S')}")
            team.register_experts(expert_names)

        # 3. Execute each layer in parallel
        all_outputs = {}
        for layer_ids in plan.execution_layers:
            # Get subtasks for this layer
            layer_subtasks = {st.id: st for st in plan.subtasks if st.id in layer_ids}

            # Execute all subtasks in this layer concurrently
            layer_pids = [st.expert_id for st in layer_subtasks.values()]

            # Use convene to execute specific perspectives
            outputs = self.convene(layer_pids, question)

            # Map outputs to subtask IDs
            for output in outputs:
                if hasattr(output, "perspective_name"):
                    # Find matching subtask
                    for st in layer_subtasks.values():
                        if st.expert_name == output.perspective_name:
                            all_outputs[st.id] = output
                            team.publish_concluded(
                                st.expert_name,
                                [output.analysis[:200] if hasattr(output, "analysis") else ""],
                            )
                            break

        # 4. Synthesize results
        synthesis = self._synthesize_results(plan, all_outputs, team)

        # 5. Capture learnings (if available)
        learnings_result = None
        if learnings is not None:
            experts_used = [st.expert_name for st in plan.subtasks]
            # Get rating from analysis_metadata if available
            # For now, use a default and let user update later
            learnings_result = {
                "captured": True,
                "combo": "+".join(sorted(experts_used)),
                "tip": learnings.get_tips_for_question_type(plan.question_type),
            }

        return {
            "decomposed_plan": {
                "original_question": plan.original,
                "complexity": plan.complexity.value,
                "question_type": plan.question_type,
                "subtasks": [
                    {
                        "id": st.id,
                        "expert": st.expert_name,
                        "focus": st.focus,
                        "priority": st.priority,
                    }
                    for st in plan.subtasks
                ],
                "execution_layers": plan.execution_layers,
                "key_angles": plan.key_angles,
                "warnings": plan.warnings,
            },
            "team_session": team.get_board_summary(),
            "synthesis": synthesis,
            "learnings": learnings_result,
        }

    def _synthesize_results(
        self,
        plan: DecomposedQuestion,
        outputs: dict[str, Any],
        team: TeamIntegration,
    ) -> dict[str, Any]:
        """Synthesize results from all expert perspectives."""
        expert_insights = []

        for st in plan.subtasks:
            if st.id in outputs:
                output = outputs[st.id]
                insight = {
                    "expert": st.expert_name,
                    "focus": st.focus,
                    "analysis": output.analysis if hasattr(output, "analysis") else str(output),
                    "key_findings": [],
                }
                # Extract key findings if available
                if hasattr(output, "key_findings"):
                    insight["key_findings"] = output.key_findings
                expert_insights.append(insight)

        return {
            "question": plan.original,
            "question_type": plan.question_type,
            "complexity": plan.complexity.value,
            "key_angles": plan.key_angles,
            "warnings": plan.warnings,
            "expert_insights": expert_insights,
            "concluded_count": team.get_board_summary()["concluded_count"],
            "total_experts": team.get_board_summary()["total_experts"],
        }


def get_jury(
    registry: Optional[Registry] = None,
    router: Optional[Router] = None,
    profile_manager: Optional[Any] = None,
    feedback_collector: Optional[Any] = None,
    team_integration: Optional[Any] = None,
) -> Jury:
    """Get a Jury instance with optional profile, feedback, and team support."""
    return Jury(
        registry=registry,
        router=router,
        profile_manager=profile_manager,
        feedback_collector=feedback_collector,
        team_integration=team_integration,
    )


# Convenience function for simple usage
def think(
    input: str,
    context: Optional[dict[str, Any]] = None,
    mode: str = "auto",
    selective_ids: Optional[list[str]] = None,
    user_id: Optional[str] = None,
) -> JuryResult:
    """
    One-shot jury thinking.

    Example:
        result = think("Should I invest in AI?", mode="force_all")
        for output in result.get_outputs():
            print(f"{output.perspective_name}: {output.analysis}")

        # With profile support:
        result = think("职业选择建议", user_id="user123")
        print(result.followup_prompt)  # Ask user for feedback
    """
    jury = get_jury()
    return jury.think(
        input, context, mode, selective_ids, user_id=user_id
    )
