"""Doubt Perspective - 怀疑质疑视角

专门挑逻辑漏洞、假设漏洞、证据不足。
触发关键词: 怀疑、质疑、真的吗、万一、不一定、可能错、漏洞、假设
"""

from super_thinking.perspectives._interface import Perspective, PerspectiveOutput


class DoubtPerspective(Perspective):
    """怀疑质疑视角：专门挑逻辑漏洞、假设漏洞、证据不足."""

    @property
    def id(self) -> str:
        return "doubt_perspective"

    @property
    def name(self) -> str:
        return "怀疑质疑视角"

    @property
    def description(self) -> str:
        return "专门挑逻辑漏洞、假设漏洞、证据不足的分析视角。列出3-5个可能的疑点，质疑论证的薄弱环节。"

    @property
    def trigger_keywords(self) -> list[str]:
        return [
            "怀疑", "质疑", "真的吗", "万一", "不一定", "可能错",
            "漏洞", "假设", "有问题", "靠得住吗", "成立吗",
            "凭什么", "证据呢", "论证", "前提", "逻辑",
        ]

    def think(self, input: str, context: dict) -> PerspectiveOutput:
        """Execute doubt-based critical analysis."""
        input_lower = input.lower()

        doubts = self._generate_doubts(input, input_lower)
        logical_gaps = self._find_logical_gaps(input, input_lower)
        evidence_issues = self._check_evidence_issues(input, input_lower)
        alternative_explanations = self._find_alternatives(input, input_lower)

        analysis_parts = [
            "## 🤔 怀疑质疑分析\n",
            f"**被质疑的问题**: {input}\n",
            "---\n",
            "### 🔍 核心疑点（3-5个）\n",
        ]

        for i, doubt in enumerate(doubts, 1):
            analysis_parts.append(f"{i}. **{doubt['point']}**")
            analysis_parts.append(f"   疑点依据: {doubt['reason']}")
            analysis_parts.append(f"   严重程度: {doubt['severity']}/5")
            analysis_parts.append("")

        analysis_parts.extend([
            "### 🕳️ 逻辑漏洞\n",
        ])
        for gap in logical_gaps:
            analysis_parts.append(f"- **{gap['type']}**: {gap['description']}")
            analysis_parts.append(f"  反驳: {gap['counter']}\n")

        analysis_parts.extend([
            "### ⚠️ 证据问题\n",
        ])
        for issue in evidence_issues:
            analysis_parts.append(f"- {issue}\n")

        analysis_parts.extend([
            "### 💡 替代解释\n",
        ])
        for alt in alternative_explanations:
            analysis_parts.append(f"- {alt}\n")

        analysis_parts.extend([
            "---\n",
            "### 🎯 质疑总结\n",
            f"**最需关注的疑点**: {doubts[0]['point'] if doubts else '无'}\n",
            "**建议**: 在接受结论之前，必须先解决最严重的疑点。",
        ])

        analysis = "\n".join(analysis_parts)

        return PerspectiveOutput(
            perspective_id="doubt_result",
            perspective_name="怀疑质疑结果",
            analysis=analysis,
            confidence=0.75,
            key_points=[d["point"] for d in doubts],
            warnings=[
                "怀疑视角不是为了否定而否定，而是指出需要更多证据支撑的地方。",
                "列出的疑点不代表结论是错的，只是需要更严格的验证。",
            ],
            metadata={
                "doubt_count": len(doubts),
                "gap_count": len(logical_gaps),
                "most_severe": doubts[0]["point"] if doubts else None,
            },
        )

    def _generate_doubts(self, input: str, input_lower: str) -> list[dict]:
        """Generate 3-5 doubt points based on input analysis."""
        doubts = []

        # Check for absolute language
        if any(k in input for k in ["一定", "必然", "肯定", "绝对", "必须", "必然"]):
            doubts.append({
                "point": "使用了绝对化表述",
                "reason": "绝对化语言（'一定'、'必然'、'肯定'）通常暗示论证过于自信，忽略了概率性和例外情况。",
                "severity": 4,
            })

        # Check for correlation vs causation
        if any(k in input_lower for k in ["因为", "导致", "引起", "造成", "因此"]):
            doubts.append({
                "point": "因果关系未经验证",
                "reason": "相关性不等于因果性。A和B同时出现，不代表A导致B。可能存在共同原因或反向因果。",
                "severity": 5,
            })

        # Check for missing alternatives
        if any(k in input_lower for k in ["只能", "只有", "必须", "最好的", "最优"]):
            doubts.append({
                "point": "可能存在被忽略的替代方案",
                "reason": "在声称某方案是'唯一'或'最好'之前，应该系统性地列举和评估所有替代选项。",
                "severity": 3,
            })

        # Check for appeal to authority
        if any(k in input_lower for k in ["专家说", "研究表明", "数据显示", "证明", "权威"]):
            doubts.append({
                "point": "权威引用需核实来源和语境",
                "reason": "'专家说'或'研究表明'可能断章取义，需要核实原始来源、样本量、研究条件等。",
                "severity": 3,
            })

        # Check for future predictions
        if any(k in input_lower for k in ["将会", "会", "未来", "以后", "预期", "估计"]):
            doubts.append({
                "point": "未来预测存在高度不确定性",
                "reason": "任何涉及未来事件的预测都有不确定性区间，'将会'这种确定性表述需要警惕。",
                "severity": 4,
            })

        # Check for missing base rate
        if any(k in input_lower for k in ["很多", "大多数", "少数", "部分", "一些"]):
            doubts.append({
                "point": "模糊的比例表述缺乏精确性",
                "reason": "'很多'、'少数'等表述没有给出具体数字，需要核实实际比例和基数。",
                "severity": 2,
            })

        # Default doubts if none triggered
        if not doubts:
            doubts = [
                {
                    "point": "这个结论依赖的前提是否成立？",
                    "reason": "大多数论证都建立在某些前提之上，这些前提本身是否可靠需要审查。",
                    "severity": 3,
                },
                {
                    "point": "论证过程中是否有跳跃的逻辑环节？",
                    "reason": "有时论证会跳过某些步骤，直接从前提跳到结论，这些跳过的步骤可能就是漏洞。",
                    "severity": 3,
                },
                {
                    "point": "是否有被刻意忽略的反面证据？",
                    "reason": "确认偏误会让人倾向于忽略不支持自己观点的证据，这也是一个常见的论证漏洞。",
                    "severity": 4,
                },
            ]

        return doubts[:5]

    def _find_logical_gaps(self, input: str, input_lower: str) -> list[dict]:
        """Identify logical gaps in the argument."""
        gaps = []

        if any(k in input_lower for k in ["因为", "所以", "因此", "导致"]):
            gaps.append({
                "type": "因果跳跃",
                "description": "从'因为A'到'所以B'之间可能存在逻辑跳跃",
                "counter": "需要补充因果链条：A是如何具体导致B的？是否有中介变量？",
            })

        if any(k in input_lower for k in ["所有", "一切", "每个", "全部"]):
            gaps.append({
                "type": "过度泛化",
                "description": "使用全称量词（所有、每个）但证据可能只来自部分样本",
                "counter": "是否存在反例？样本量和代表性是否足够？",
            })

        if any(k in input_lower for k in ["以前", "过去", "历史"]):
            gaps.append({
                "type": "历史类比谬误",
                "description": "用过去的情况类比现在，但条件可能已发生变化",
                "counter": "过去和现在的关键条件有哪些不同？类比是否恰当？",
            })

        if any(k in input_lower for k in ["直觉", "感觉", "认为", "觉得"]):
            gaps.append({
                "type": "直觉谬误",
                "description": "依赖直觉而非系统分析，可能受到可得性启发等认知偏差影响",
                "counter": "直觉背后是否有数据和逻辑支撑？是否做了系统性分析？",
            })

        if not gaps:
            gaps.append({
                "type": "潜在假设未声明",
                "description": "论证过程中可能隐含了某些未明确声明的假设",
                "counter": "列出论证成立所依赖的所有假设，并逐一检验它们是否成立。",
            })

        return gaps[:4]

    def _check_evidence_issues(self, input: str, input_lower: str) -> list[str]:
        """Check for evidence-related problems."""
        issues = []

        if any(k in input_lower for k in ["据说", "听说", "有人说", "传言"]):
            issues.append("⚠️ 消息来源不明或未经核实（据说/听说）")

        if any(k in input_lower for k in ["可能", "也许", "大概", "或许"]):
            issues.append("⚠️ 使用了模糊的概率表述，结论的确定性被高估")

        if not any(k in input_lower for k in ["数据", "研究", "证据", "统计", "实验", "调查"]):
            issues.append("⚠️ 缺乏具体数据或研究支撑，多为主观论述")

        if len(input) < 30:
            issues.append("⚠️ 输入信息量过少，难以进行充分的证据核查")

        if not issues:
            issues.append("✓ 初步检查未发现明显的证据缺失问题（但仍需深入核查）")

        return issues

    def _find_alternatives(self, input: str, input_lower: str) -> list[str]:
        """Find alternative explanations or perspectives."""
        alternatives = [
            "另一种可能是[某个被忽略的因素]在起作用，而不是你主要考虑的原因。",
            "这个现象可能有多重解释，需要更细粒度的分析才能区分。",
            "将问题框架从'如何做到'改为'为什么要做'，可能揭示不同视角。",
        ]
        return alternatives
