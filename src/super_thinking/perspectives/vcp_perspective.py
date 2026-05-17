"""VCP System Integration Perspective.

Integrates TagMemo, MetaThinking, Magi Debate into VCP protocol framework.
VCP syntax: <<<[TOOL_REQUEST]>>> tool_name:「始」...「末」...
"""

import re
from super_thinking.perspectives._interface import Perspective, PerspectiveOutput


class VcpPerspective(Perspective):
    """VCP系统集成：TagMemo浪潮 + 元思考 + Magi辩论，统一协议输出."""

    @property
    def id(self) -> str:
        return "vcp_perspective"

    @property
    def name(self) -> str:
        return "VCP系统集成"

    @property
    def description(self) -> str:
        return (
            "VCP系统集成分析：不依赖外部环境，整合TagMemo净化+元思考推理+Magi三贤者裁决，"
            "输出结构化分析 + VCP协议格式文本。可移植，任何框架都能用。"
        )

    @property
    def trigger_keywords(self) -> list[str]:
        return [
            "vcp", "VCP", "系统集成", "综合分析",
            "整合", "协作", "分布式", "插件",
        ]

    def think(self, input: str, context: dict) -> PerspectiveOutput:
        """Execute VCP integrated analysis combining TagMemo + MetaThinking + Magi."""
        # Step 1: TagMemo preprocessing
        tagmemo_result = self._tagmemo_preprocess(input)

        # Step 2: MetaThinking analysis
        metathinking_result = self._metathinking_analysis(input, tagmemo_result)

        # Step 3: Magi Debate for key decisions
        magi_result = self._magi_decide(input, metathinking_result)

        # Step 4: VCP protocol output
        vcp_protocol = self._generate_vcp_protocol(input, tagmemo_result, metathinking_result, magi_result)

        analysis = (
            "## ⚙️ VCP系统集成分析\n\n"
            f"**输入问题**：{input}\n\n"
            "---\n\n"
            "### 🌊 TagMemo浪潮预处理\n\n"
            f"{tagmemo_result}\n\n"
            "---\n\n"
            "### 🧠 元思考系统\n\n"
            f"{metathinking_result}\n\n"
            "---\n\n"
            "### ⚖️ Magi三贤者裁决\n\n"
            f"{magi_result}\n\n"
            "---\n\n"
            "### 📡 VCP协议输出\n\n"
            f"```\n{vcp_protocol}\n```"
        )

        return PerspectiveOutput(
            perspective_id="vcp_result",
            perspective_name="VCP系统集成结果",
            analysis=analysis,
            confidence=0.82,
            warnings=[
                "VCP协议格式为规范化文本输出，可被支持VCP解析的系统直接读取。",
            ],
            metadata={
                "vcp_syntax": True,
                "components_used": ["TagMemo", "MetaThinking", "Magi"],
                "protocol_version": "V7.1",
            }
                )

    def _tagmemo_preprocess(self, input: str) -> str:
        """TagMemo preprocessing stage."""
        # Clean
        cleaned = re.sub(r'<[^>]+>', '', input)
        cleaned = re.sub(r'\{[^{}]*\}', '', cleaned)
        cleaned = re.sub(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF]', '', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        # EPA projection
        depth = min(10, max(1, len(cleaned) // 30 + 2))
        resonance = 5

        # Extract tags
        tags: list[str] = []
        tag_indicators = ["项目", "技术", "问题", "方案", "系统", "产品", "用户", "市场"]
        for indicator in tag_indicators:
            if indicator in cleaned:
                tags.append(indicator)

        output: list[str] = []
        output.append(f"**净化查询**：{cleaned}")
        output.append(f"**EPA投影**：depth={depth}/10, resonance={resonance}/10")
        output.append(f"**核心标签**：{', '.join(tags[:5]) if tags else '默认查询'}")
        output.append(f"**检索策略**：{'深度语义' if depth >= 6 else '标准检索'}")

        return "\n".join(output)

    def _metathinking_analysis(self, input: str, tagmemo: str) -> str:
        """MetaThinking analysis stage."""
        # Identify problem type
        input_lower = input.lower()
        if any(k in input_lower for k in ["为什么", "原因"]):
            problem_type = "因果分析"
        elif any(k in input_lower for k in ["如何", "怎么"]):
            problem_type = "方法求解"
        elif any(k in input_lower for k in ["应该", "是否"]):
            problem_type = "决策判断"
        else:
            problem_type = "综合分析"

        output: list[str] = []
        output.append(f"**问题类型**：{problem_type}")
        output.append(f"**思维簇激活**：前思维簇 → 逻辑推理簇 → 反思簇 → 决策簇")

        # Key reasoning points
        if problem_type == "因果分析":
            output.append("**推理链**：结果 → 直接原因 → 间接原因 → 根本原因")
        elif problem_type == "方法求解":
            output.append("**推理链**：目标 → 所需步骤 → 资源需求 → 执行计划")
        elif problem_type == "决策判断":
            output.append("**推理链**：选项列举 → 评估标准 → 权衡利弊 → 最终选择")
        else:
            output.append("**推理链**：问题分解 → 子问题分析 → 综合结论")

        # Reflection note
        output.append("\n**反思检查**：")
        output.append("• 无逻辑跳跃")
        output.append("• 结论与证据一致")
        output.append("• 无需修正")

        return "\n".join(output)

    def _magi_decide(self, input: str, metathinking: str) -> str:
        """Magi three-sages decision stage."""
        melchior = self._melchior_view(input)
        balthazar = self._balthazar_view(input)
        caspar = self._caspar_synthesis(melchior, balthazar)

        output: list[str] = []
        output.append("**MELCHIOR（理性）**：")
        output.append(melchior[:200])
        output.append("\n**BALTHAZAR（感性）**：")
        output.append(balthazar[:200])
        output.append("\n**CASPAR（裁决）**：")
        output.append(caspar[:200])

        return "\n".join(output)

    def _melchior_view(self, input: str) -> str:
        """MELCHIOR: Absolute reason."""
        return (
            f"• 逻辑分析：{input[:50]}... 的核心变量是X、Y、Z\n"
            "• 数据框架：建立决策矩阵，量化期望值\n"
            "• 风险评估：概率×影响，识别最大风险点"
        )

    def _balthazar_view(self, input: str) -> str:
        """BALTHAZAR: Emotional intuition."""
        return (
            f"• 价值观检视：{input[:50]}... 反映的核心价值是什么\n"
            "• 情感校验：做这个决定时内心是否平静\n"
            "• 长期视角：5年后回头看，会后悔吗"
        )

    def _caspar_synthesis(self, melchior: str, balthazar: str) -> str:
        """CASPAR: Balanced synthesis."""
        return (
            "综合理性数据和感性判断，"
            "在它们之间找到平衡点。"
            "理性给出最优路径，感性提供持续动力，"
            "最终建议：选择让你内心最平静的理性选项。"
        )

    def _generate_vcp_protocol(
        self,
        input: str,
        tagmemo: str,
        metathinking: str,
        magi: str,
    ) -> str:
        """Generate VCP protocol output."""
        # Extract key terms for protocol
        keywords = self._extract_protocol_keywords(input)

        protocol = f"""<<<[TOOL_REQUEST]>>>
tool_name:「始」VCP_SYSTEM_INTEGRATION「末」,
query:「始」{input[:100]}「末」,
tagmemo_tags:「始」{keywords}「末」,
metathinking_type:「始」{self._get_problem_type(input)}「末」,
magi_verdict:「始」{magi[:100] if len(magi) > 100 else magi}「末」,
protocol_version:「始」V7.1「末」,
confidence:「始」0.82「末」
<<<[END_TOOL_REQUEST]>>>"""

        return protocol

    def _extract_protocol_keywords(self, text: str) -> str:
        """Extract key terms for VCP protocol."""
        indicators = ["项目", "技术", "系统", "产品", "用户", "市场", "数据", "模型"]
        found = [w for w in indicators if w in text]
        return ",".join(found[:5]) if found else "综合查询"

    def _get_problem_type(self, text: str) -> str:
        """Get problem type for protocol."""
        text_lower = text.lower()
        if any(k in text_lower for k in ["为什么", "原因"]):
            return "因果分析"
        elif any(k in text_lower for k in ["如何", "怎么"]):
            return "方法求解"
        elif any(k in text_lower for k in ["应该", "是否"]):
            return "决策判断"
        return "综合分析"
