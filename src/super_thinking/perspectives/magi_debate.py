"""Magi Three Sages Debate Perspective - Rational, Emotional, and Balanced viewpoints.

Three archetypes: MELCHIOR (absolute reason), BALTHAZAR (emotional intuition),
CASPAR (balanced synthesis).
"""

import re
from super_thinking.perspectives._interface import Perspective, PerspectiveOutput


class MagiDebatePerspective(Perspective):
    """Magi三贤者辩论系统：理性、感性、平衡三方视角."""

    @property
    def id(self) -> str:
        return "magi_debate"

    @property
    def name(self) -> str:
        return "Magi三贤者辩论"

    @property
    def description(self) -> str:
        return "Magi三贤者辩论：MELCHIOR（绝对理性）、BALTHAZAR（感性直觉）、CASPAR（综合平衡）。用于重要决策的多角度分析。"

    @property
    def trigger_keywords(self) -> list[str]:
        return [
            "辩论", "权衡", "利弊", "理性", "感性", "决策",
            "多方分析", "三贤者", "应该吗", "如何选择",
            "纠结", "两难", "优缺点",
        ]

    def think(self, input: str, context: dict) -> PerspectiveOutput:
        """Execute the three-sage debate analysis."""
        melchiors_view = self._melchior_analysis(input)
        balthazars_view = self._balthazar_analysis(input)
        caspars_view = self._caspar_synthesis(input, melchiors_view, balthazars_view)

        analysis = (
            "## ⚖️ Magi三贤者辩论分析\n\n"
            f"**问题**：{input}\n\n"
            "---\n\n"
            "### 🔷 MELCHIOR（麦基西德）— 绝对理性\n\n"
            f"{melchiors_view}\n\n"
            "---\n\n"
            "### 🔶 BALTHAZAR（巴尔塔萨）— 感性直觉\n\n"
            f"{balthazars_view}\n\n"
            "---\n\n"
            "### 🏛️ CASPAR（卡斯帕）— 综合裁决\n\n"
            f"{caspars_view}\n\n"
            "---\n\n"
            "**三贤者立场总结**：理性提供逻辑框架，感性提供价值判断，平衡给出最终裁决。"
        )

        return PerspectiveOutput(
            perspective_id="magi_result",
            perspective_name="Magi三贤者辩论结果",
            analysis=analysis,
            confidence=0.75,
            warnings=[
                "辩论结果是分析性建议，不能替代实际决策。",
                "三贤者视角是结构化分析框架，实际判断需要结合具体情境。",
            ],
            metadata={
                "melchior": melchiors_view[:200],
                "balthazar": balthazars_view[:200],
                "caspar": caspars_view[:200],
            }
                )

    def _melchior_analysis(self, input: str) -> str:
        """MELCHIOR: Pure reason, data, logic, quantitative analysis."""
        input_lower = input.lower()

        # Extract key decision elements
        decision_elements = self._extract_decision_elements(input)

        analysis_parts = [
            "**逻辑分析**：",
            f"• 问题的核心变量是：{', '.join(decision_elements) if decision_elements else '尚未明确'}",
            "• 从数据角度，关键指标是：成功率、风险率、成本收益比",
            "• 量化评估建议：建立决策矩阵，列出各选项的期望值",
        ]

        # Specific reasoning for common decision types
        if any(k in input_lower for k in ["工作", "offer", "职业", "跳槽"]):
            analysis_parts.extend([
                "• 薪资与职业发展：计算5年累计收益对比",
                "• 机会成本：接受A意味着放弃B，量化B的价值",
                "• 风险：市场下行时，核心技能的价值稳定性",
            ])
        elif any(k in input_lower for k in ["创业", "项目", "产品"]):
            analysis_parts.extend([
                "• MVP验证：在投入全部资源前，用最小成本测试核心假设",
                "• 单元经济：客户获取成本 vs 客户终身价值",
                "• 现金流：生存周期内资金是否足够",
            ])
        elif any(k in input_lower for k in ["投资", "理财", "钱"]):
            analysis_parts.extend([
                "• 分散化：不要All-in单一标的",
                "• 风险调整后收益：夏普比率",
                "• 流动性：需要用钱时的变现能力",
            ])
        else:
            analysis_parts.extend([
                "• 列出所有可能选项",
                "• 评估每个选项的收益和损失",
                "• 计算期望值（概率×结果）",
                "• 选择期望值最高的选项",
            ])

        return "\n".join(analysis_parts)

    def _balthazar_analysis(self, input: str) -> str:
        """BALTHAZAR: Emotional intuition, human nature, ethics."""
        input_lower = input.lower()

        analysis_parts = [
            "**感性直觉分析**：",
            "• 这个决定反映了什么价值观？",
            "• 你的内心真实感受是什么？（不只是理性上的'应该'）",
            "• 如果5年后回头看，你会后悔这个决定吗？",
        ]

        if any(k in input_lower for k in ["工作", "offer", "职业", "跳槽"]):
            analysis_parts.extend([
                "• 这份工作让你兴奋还是消耗？",
                "• 团队氛围和文化是否让你感到归属？",
                "• 直属领导是否值得跟随？",
            ])
        elif any(k in input_lower for k in ["创业", "项目", "产品"]):
            analysis_parts.extend([
                "• 这个创业方向让你有热情持续投入吗？",
                "• 用户是否真的需要这个产品，还是你在强加需求？",
                "• 即使失败，这段经历是否有意义？",
            ])
        elif any(k in input_lower for k in ["投资", "理财"]):
            analysis_parts.extend([
                "• 你能承受多大的心理波动？",
                "• 这笔投资会不会影响你的睡眠？",
                "• 贪婪和恐惧各占多少比例？",
            ])
        else:
            analysis_parts.extend([
                "• 做这个决定时，你的情绪是平静还是焦虑？",
                "• 这个选择是否符合你的长期人生愿景？",
                "• 是否有人在情感上依赖你的决定？",
            ])

        return "\n".join(analysis_parts)

    def _caspar_synthesis(self, input: str, melchior: str, balthazar: str) -> str:
        """CASPAR: Balanced synthesis, weigh pros and cons, give final recommendation."""
        input_lower = input.lower()

        synthesis_parts = [
            "**综合裁决**：",
            "理性揭示了数据和逻辑框架，感性揭示了价值和情感维度。",
            "两者缺一不可，需要在它们之间找到平衡点。\n",
        ]

        # Decision type specific synthesis
        if any(k in input_lower for k in ["工作", "offer", "offer"]):
            synthesis_parts.extend([
                "**对职业选择的具体建议**：",
                "1. 理性指标（40%权重）：薪资成长曲线、行业发展空间、核心技能积累",
                "2. 感性指标（30%权重）：工作热情、团队氛围、领导品质",
                "3. 底线指标（30%权重）：是否能维持生活质量、是否有成长空间",
                "4. 如果两者冲突，问自己：5年后哪个选择让我更完整？",
            ])
        elif any(k in input_lower for k in ["创业", "项目"]):
            synthesis_parts.extend([
                "**对创业项目的综合建议**：",
                "1. 做一个月的用户访谈，验证真实需求（理性+感性）",
                "2. 用最小MVP验证商业模式，不要一开始就大规模投入",
                "3. 给自己设一个明确的'停止线'：如果X个月后没有Y进展，就调整方向",
                "4. 最坏的打算是什么？最坏的情况能承受吗？",
            ])
        else:
            synthesis_parts.extend([
                "**综合决策框架**：",
                "1. 理性分析给出了最优路径，但需要感性校验",
                "2. 感性强项指向的方向，往往有更持久的动力支撑",
                "3. 最终建议：在理性框架内，选择让你内心最平静的那个选项",
                "4. 如果理性选择和感性选择一致，这是最强信号",
            ])

        return "\n".join(synthesis_parts)

    def _extract_decision_elements(self, input: str) -> list[str]:
        """Extract key decision elements from the input."""
        # Simple heuristic extraction
        elements = []
        if any(k in input for k in ["工作", "offer", "职业"]):
            elements.append("职业发展")
        if any(k in input for k in ["薪资", "钱", "收入", "成本"]):
            elements.append("经济回报")
        if any(k in input for k in ["风险", "安全", "保障"]):
            elements.append("风险系数")
        if any(k in input for k in ["时间", "效率", "速度"]):
            elements.append("时间成本")
        if any(k in input for k in ["成长", "学习", "发展"]):
            elements.append("成长空间")
        if any(k in input for k in ["人", "关系", "团队", "文化"]):
            elements.append("人际环境")
        return elements if elements else []
