"""Verification Perspective - Evidence-based completion checking.

The iron law: NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE.
Evidence before claims, always.
"""

import re
from super_thinking.perspectives._interface import Perspective, PerspectiveOutput


class VerificationPerspective(Perspective):
    """证伪核查：证据优先原则，完成前必须验证."""

    @property
    def id(self) -> str:
        return "verification"

    @property
    def name(self) -> str:
        return "证伪核查"

    @property
    def description(self) -> str:
        return "证伪核查系统：证据优先原则，在声称完成/修复/通过之前，必须运行验证命令并确认输出。"

    @property
    def trigger_keywords(self) -> list[str]:
        return [
            "验证", "确认", "证据", "完成", "测试", "通过",
            "修复", "bug", "验证", "核查", "检查", "通过了吗",
            "是否完成", "能否交付", "检验",
        ]

    def think(self, input: str, context: dict) -> PerspectiveOutput:
        """Execute verification-oriented analysis."""
        input_lower = input.lower()

        # Classify what needs verification
        verification_type = self._classify_verification(input_lower)

        analysis_parts = [f"**证伪核查分析（{verification_type['type']}）**\n"]

        # Step 1: Identify the claim
        analysis_parts.append(f"**待验证主张**：{self._extract_claim(input)}")

        # Step 2: What evidence is required
        analysis_parts.append(f"\n**所需证据**：")
        required_evidence = self._get_required_evidence(verification_type)
        for item in required_evidence:
            analysis_parts.append(f"• {item}")

        # Step 3: What NOT sufficient
        analysis_parts.append(f"\n**⚠️ 证据不足的标志（不可接受）**：")
        insufficient = self._get_insufficient_signs(verification_type)
        for item in insufficient:
            analysis_parts.append(f"❌ {item}")

        # Step 4: Gate function checklist
        analysis_parts.append(f"\n**🔲 质量门禁检查表**：")
        gate_steps = self._get_gate_steps(verification_type)
        for i, step in enumerate(gate_steps, 1):
            analysis_parts.append(f"☐ [{i}] {step}")

        # Step 5: Red flags
        analysis_parts.append(f"\n**🚨 红牌警告**：")
        red_flags = self._get_red_flags()
        for flag in red_flags:
            analysis_parts.append(f"⚠️ {flag}")

        # Step 6: Action recommendations
        analysis_parts.append(f"\n**✅ 下一步行动**：")
        actions = self._get_actions(verification_type)
        for action in actions:
            analysis_parts.append(f"→ {action}")

        analysis = "\n".join(analysis_parts)

        return PerspectiveOutput(
            perspective_id="verification_result",
            perspective_name="证伪核查结果",
            analysis=analysis,
            confidence=0.9,
            warnings=[
                "证伪核查不是否定，而是确保有充分的证据支撑结论。",
                "跳过任何验证步骤都可能导致错误结论。",
                "本框架不能替代实际的测试和验证执行。",
            ],
            metadata={
                "verification_type": verification_type["type"],
                "required_evidence": required_evidence,
                "gate_steps_count": len(gate_steps),
            },
        )

    def _classify_verification(self, input_lower: str) -> dict:
        """Classify the type of verification needed."""
        if any(k in input_lower for k in ["测试", "测试通过", "test pass", "单元测试"]):
            return {"type": "测试验证", "claim": "Tests pass"}
        elif any(k in input_lower for k in ["bug", "修复", "fix", "错误", "缺陷"]):
            return {"type": "Bug修复验证", "claim": "Bug fixed"}
        elif any(k in input_lower for k in ["构建", "编译", "build", "编译成功"]):
            return {"type": "构建验证", "claim": "Build succeeds"}
        elif any(k in input_lower for k in ["完成", "交付", "完成了吗"]):
            return {"type": "完成度验证", "claim": "Task complete"}
        elif any(k in input_lower for k in ["代码", "代码质量", "lint", "代码检查"]):
            return {"type": "代码质量验证", "claim": "Code quality"}
        elif any(k in input_lower for k in ["功能", "feature", "需求"]):
            return {"type": "功能验证", "claim": "Feature works"}
        else:
            return {"type": "通用验证", "claim": "Claim to verify"}

    def _extract_claim(self, input: str) -> str:
        """Extract what is being claimed."""
        # Remove question words and clean up
        claim = input
        for suffix in ["？", "?", "吗", "吗？"]:
            if suffix in claim:
                claim = claim.split(suffix)[0]
                break
        return claim.strip()

    def _get_required_evidence(self, vtype: dict) -> list[str]:
        """Get required evidence list for verification type."""
        if vtype["type"] == "测试验证":
            return [
                "运行测试命令的实际输出",
                "失败数为0",
                "所有测试用例通过",
                "测试覆盖率报告（如有）",
            ]
        elif vtype["type"] == "Bug修复验证":
            return [
                "重现Bug的原始失败",
                "修复后同一测试通过",
                "相关回归测试全部通过",
                "无新引入的错误",
            ]
        elif vtype["type"] == "构建验证":
            return [
                "构建命令返回exit code 0",
                "构建产物存在且完整",
                "启动命令无报错",
            ]
        elif vtype["type"] == "完成度验证":
            return [
                "逐条对照需求清单",
                "每条需求有对应的实现证据",
                "边界情况已测试",
            ]
        elif vtype["type"] == "代码质量验证":
            return [
                "Linter输出无错误",
                "类型检查通过（如使用TypeScript等）",
                "无明显代码异味",
            ]
        elif vtype["type"] == "功能验证":
            return [
                "功能正常工作的实际输出",
                "边界条件测试结果",
                "错误处理验证",
            ]
        return ["能证明主张成立的直接证据"]

    def _get_insufficient_signs(self, vtype: dict) -> list[str]:
        """Get signs that are NOT sufficient evidence."""
        return [
            "之前的运行结果",
            "代码改了，应该可以",
            "看起来没问题",
            "日志看起来正常",
            "理论上应该能过",
            "之前有过一次通过",
            "测试是同事跑的，我没看结果",
        ]

    def _get_gate_steps(self, vtype: dict) -> list[str]:
        """Get the gate function checklist."""
        if vtype["type"] == "测试验证":
            return [
                "运行完整测试命令（不要只运行失败的测试）",
                "读取完整输出",
                "确认失败数=0",
                "确认测试覆盖率符合要求",
                "只有以上全部通过才能说'测试通过'",
            ]
        elif vtype["type"] == "Bug修复验证":
            return [
                "重新运行导致Bug的原始输入",
                "确认输出符合预期",
                "运行相关回归测试",
                "检查是否引入新问题",
                "只有以上全部通过才能说'Bug已修复'",
            ]
        elif vtype["type"] == "构建验证":
            return [
                "运行完整构建命令",
                "检查exit code是否为0",
                "确认构建产物存在",
                "尝试运行构建产物（如可执行文件能启动）",
                "只有以上全部通过才能说'构建成功'",
            ]
        elif vtype["type"] == "完成度验证":
            return [
                "重读原始需求/计划",
                "创建逐条检查清单",
                "为每条需求找到对应实现证据",
                "明确标注未完成项",
                "只有100%完成才能说'完成'，否则说明差距",
            ]
        return [
            "明确要验证的具体主张",
            "找到能证明该主张的命令/操作",
            "执行并获取实际输出",
            "核对输出是否支撑主张",
            "如实报告结果",
        ]

    def _get_red_flags(self) -> list[str]:
        """Get red flag warnings."""
        return [
            "使用了'应该'、'可能'、'也许'等模糊词汇",
            "在运行验证之前表达满意",
            "说'Great!'、'Perfect!'、'Done!'等完成语",
            "信任其他Agent的报告而不独立验证",
            "只做部分检查就下结论",
            "因为累了想早点结束而跳过验证",
            "认为'这次例外没关系'",
        ]

    def _get_actions(self, vtype: dict) -> list[str]:
        """Get recommended next actions."""
        if vtype["type"] == "测试验证":
            return [
                "运行测试：pytest / npm test / go test（视项目而定）",
                "检查测试输出中的失败数",
                "如有任何失败，不要声称'测试通过'",
            ]
        elif vtype["type"] == "Bug修复验证":
            return [
                "重现原始Bug场景",
                "运行修复后的代码",
                "对比结果是否符合预期",
            ]
        elif vtype["type"] == "构建验证":
            return [
                "运行构建命令（如：npm run build / cargo build / mvn package）",
                "检查exit code",
                "验证构建产物",
            ]
        elif vtype["type"] == "完成度验证":
            return [
                "列出所有需求项",
                "逐项打勾确认",
                "明确未完成项",
            ]
        return [
            "明确需要验证的具体命令或操作",
            "执行并记录实际输出",
            "基于实际输出做出判断",
        ]
