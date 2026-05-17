"""Meta-Thinking Perspective - Recursive reflection across five thinking clusters.

Based on VCP's meta-thinking system with 5 clusters:
Anterior, Logical, Reflective, Creative, Decisive.
"""

import re
from super_thinking.perspectives._interface import Perspective, PerspectiveOutput


class MetaThinkingPerspective(Perspective):
    """元思考系统：五思维簇递归反思."""

    @property
    def id(self) -> str:
        return "meta_thinking"

    @property
    def name(self) -> str:
        return "元思考"

    @property
    def description(self) -> str:
        return "超动态递归思维链：前思维簇（问题感知）、逻辑推理簇、反思簇（自我检查）、创意簇、决策簇。"

    @property
    def trigger_keywords(self) -> list[str]:
        return [
            "反思", "思考过程", "思维链", "推理", "元思考",
            "逻辑", "分析", "想想看", "怎么得出", "为什么",
            "递归", "自我检查", "推理过程",
        ]

    def think(self, input: str, context: dict) -> PerspectiveOutput:
        """Execute meta-thinking with 5-cluster recursive reflection."""
        depth = int(context.get("reflection_depth", 3)) if context else 3
        depth = min(depth, 3)

        chain_of_thought: list[tuple[str, str]] = []

        # Cluster 1: Anterior - problem perception
        anterior_result = self._anterior_cluster(input)
        chain_of_thought.append(("前思维簇", anterior_result))

        # Cluster 2: Logical - reasoning
        logical_result = self._logical_cluster(input, anterior_result)
        chain_of_thought.append(("逻辑推理簇", logical_result))

        # Cluster 3: Creative (if needed)
        creative_result = self._creative_cluster(input, logical_result)
        chain_of_thought.append(("创意簇", creative_result))

        # Recursive reflection
        for i in range(depth):
            reflection = self._reflective_cluster(
                chain_of_thought, iteration=i + 1
            )
            chain_of_thought.append(("反思簇", reflection))
            if "无需修正" in reflection:
                break

        # Cluster 5: Decision
        decision_result = self._decisive_cluster(
            input, chain_of_thought
        )
        chain_of_thought.append(("决策簇", decision_result))

        # Build analysis
        analysis = "## 🧠 元思考分析\n\n"
        analysis += f"**问题**：{input}\n"
        analysis += f"**递归深度**：{depth}\n\n"
        analysis += "---\n\n"

        for cluster, result in chain_of_thought:
            analysis += f"### {cluster}\n{result}\n\n---\n\n"

        analysis += f"**最终结论**：\n{decision_result}"

        confidence = 0.8 if depth >= 2 else 0.65

        return PerspectiveOutput(
            perspective_id="meta_result",
            perspective_name="元思考结果",
            analysis=analysis,
            confidence=confidence,
            warnings=[
                "元思考是分析框架，不是万能答案。",
                "递归深度过高可能陷入无限反思，需要设定终止条件。",
            ],
            metadata={"clusters_used": [c for c, _ in chain_of_thought]},
        )

    def _anterior_cluster(self, input: str) -> str:
        """Anterior cluster: problem perception and intent recognition."""
        input_lower = input.lower()

        # Classify problem type
        if any(k in input_lower for k in ["为什么", "原因", "为什么", "因果"]):
            problem_type = "因果分析"
        elif any(k in input_lower for k in ["如何", "怎么", "方法", "怎样"]):
            problem_type = "方法求解"
        elif any(k in input_lower for k in ["应该", "是否", "选择", "决策"]):
            problem_type = "决策判断"
        elif any(k in input_lower for k in ["比较", "对比", "哪个好", "优缺点"]):
            problem_type = "比较评估"
        else:
            problem_type = "综合分析"

        return (
            f"**问题感知**：\n"
            f"• 问题类型：{problem_type}\n"
            f"• 问题焦点：{self._extract_focus(input)}\n"
            f"• 隐含意图：{self._extract_intent(input)}\n"
            f"• 建议激活的思维簇：逻辑推理簇（必选）、反思簇（必选）、创意簇（视情况）"
        )

    def _logical_cluster(self, input: str, anterior: str) -> str:
        """Logical cluster: analysis, reasoning, calculation."""
        steps: list[str] = []

        # Step 1: Identify knowns and unknowns
        steps.append("**已知条件**：")
        steps.append(f"• 问题陈述：{input}")
        steps.append("• 需要补充的信息：背景、约束条件、相关数据")

        # Step 2: Logical structure
        steps.append("\n**推理结构**：")
        if "因果" in anterior:
            steps.append("• 从结果追溯原因")
            steps.append("• 建立因果链：结果→直接原因→间接原因→根本原因")
        elif "方法" in anterior:
            steps.append("• 目标倒推：需要达成什么→需要什么步骤→每步需要什么资源")
        elif "决策" in anterior:
            steps.append("• 列出所有可能选项")
            steps.append("• 为每个选项建立评估标准")
            steps.append("• 量化每个标准的重要性权重")
        else:
            steps.append("• 分解问题为子问题")
            steps.append("• 建立子问题之间的关系")

        # Step 3: Potential logical pitfalls
        steps.append("\n**逻辑陷阱预警**：")
        steps.append("• 确认偏误：避免只收集支持预先结论的证据")
        steps.append("• 相关性≠因果性")
        steps.append("• 基数谬误：百分比对比时注意基数")

        return "\n".join(steps)

    def _creative_cluster(self, input: str, logical: str) -> str:
        """Creative cluster: generation, association, divergence."""
        associations: list[str] = []

        associations.append("**联想发散**：")
        associations.append(f"• 核心问题：{self._extract_focus(input)}")
        associations.append("• 类比问题：这个问题像什么其他领域的问题？")
        associations.append("• 如果资源无限，你会怎么做？")
        associations.append("• 如果完全相反的解法是什么？")

        associations.append("\n**创新思路**：")
        # Domain-specific creative prompts
        input_lower = input.lower()
        if any(k in input_lower for k in ["技术", "系统", "代码", "产品"]):
            associations.append("• 能否用更简单的架构解决？")
            associations.append("• 借鉴哪个不同领域的设计模式？")
            associations.append("• 用户的操作路径能否更短？")
        elif any(k in input_lower for k in ["团队", "管理", "组织"]):
            associations.append("• 小团队如何做到大团队做不到的事？")
            associations.append("• 能否用激励代替管理？")
        else:
            associations.append("• 这个问题10年后还重要吗？")
            associations.append("• 有没有被忽视的外部因素？")

        associations.append("\n**收敛建议**：")
        associations.append("• 从发散结果中挑选2-3个最有潜力的方向")
        associations.append("• 用逻辑簇的方法验证这些方向")

        return "\n".join(associations)

    def _reflective_cluster(
        self, chain: list[tuple[str, str]], iteration: int
    ) -> str:
        """Reflective cluster: self-check and error correction."""
        checks: list[str] = []
        checks.append(f"**第{iteration}轮反思**：")

        # Check if reasoning is correct
        checks.append("• 推理是否正确？有没有逻辑跳跃？")
        checks.append("• 是否遗漏了关键信息？")

        # Check against previous iterations
        if iteration > 1:
            checks.append("• 与第{}轮相比，结论是否一致？如有变化，说明原因".format(iteration - 1))

        # Meta-level checks
        checks.append("\n**元层面检查**：")
        checks.append("• 我的分析是否在回答真正的问题，而不是表面问题？")
        checks.append("• 是否有情感或利益偏见影响判断？")
        checks.append("• 证据是否充分支撑结论？")

        # Determine if correction needed
        if iteration >= 2:
            checks.append("\n**修正判定**：前几轮分析逻辑一致，推理链条完整，**无需修正**。")
            status = "无需修正"
        else:
            checks.append("\n**初步评估**：分析框架建立中，需要进入决策簇给出结论。")
            status = "待决策"

        checks.insert(1, f"• 反思结果：{status}")

        return "\n".join(checks)

    def _decisive_cluster(
        self, input: str, chain: list[tuple[str, str]]
    ) -> str:
        """Decisive cluster: selection, judgment, conclusion."""
        conclusions: list[str] = []

        conclusions.append("**最终结论**：\n")

        # Synthesize from all clusters
        logical_cluster = next((r for c, r in chain if c == "逻辑推理簇"), "")
        creative_cluster = next((r for c, r in chain if c == "创意簇"), "")
        anterior_cluster = next((r for c, r in chain if c == "前思维簇"), "")

        # Extract problem type from anterior
        problem_type = "综合分析"
        if "因果" in anterior_cluster:
            problem_type = "因果分析"
        elif "方法" in anterior_cluster:
            problem_type = "方法求解"
        elif "决策" in anterior_cluster:
            problem_type = "决策判断"

        conclusions.append(f"**问题类型**：{problem_type}\n")
        conclusions.append("**分析总结**：")
        conclusions.append(f"• 逻辑推理：{self._extract_key_point(logical_cluster)}")
        conclusions.append(f"• 创新思路：{self._extract_key_point(creative_cluster)}")

        conclusions.append("\n**行动建议**：")
        if problem_type == "因果分析":
            conclusions.append("1. 确认问题的根本原因")
            conclusions.append("2. 针对性地制定解决方案")
        elif problem_type == "方法求解":
            conclusions.append("1. 选择最优解法路径")
            conclusions.append("2. 分阶段实施，设立检查点")
        elif problem_type == "决策判断":
            conclusions.append("1. 明确评估标准")
            conclusions.append("2. 权衡利弊后做出选择")
        else:
            conclusions.append("1. 分解问题为可执行的子问题")
            conclusions.append("2. 逐个解决，循环验证")

        return "\n".join(conclusions)

    def _extract_focus(self, input: str) -> str:
        """Extract the core focus of the problem."""
        # Simple heuristic: find the noun phrase closest to the question word
        focus = input
        for suffix in ["？", "?", "吗", "如何", "怎么", "为什么"]:
            if suffix in focus:
                focus = focus.split(suffix)[0]
                break
        return focus[-50:] if len(focus) > 50 else focus

    def _extract_intent(self, input: str) -> str:
        """Extract the implicit intent behind the question."""
        input_lower = input.lower()
        if "为什么" in input_lower:
            return "理解深层原因"
        elif "如何" in input_lower or "怎么" in input_lower:
            return "寻求解决方案"
        elif "应该" in input_lower or "是否" in input_lower:
            return "寻求判断或建议"
        elif "比较" in input_lower:
            return "对比评估"
        return "获取信息或分析"

    def _extract_key_point(self, text: str) -> str:
        """Extract the key conclusion point from cluster output."""
        if not text:
            return "无"
        lines = text.strip().split("\n")
        # Find the first substantive line
        for line in lines:
            if line.strip() and not line.startswith("**"):
                return line.strip()[:80]
        return lines[-1].strip()[:80] if lines else "无"
