"""Mao Zedong Perspective - Dialectical analysis based on Mao Zedong Thought.

7 core mental models from Mao Zedong's philosophical works.
"""

import re
from super_thinking.perspectives._interface import Perspective, PerspectiveOutput


class MaoPerspective(Perspective):
    """毛泽东思维框架：矛盾分析法、实践论、持久战、农村包围城市、统一战线、群众路线、纸老虎论."""

    @property
    def id(self) -> str:
        return "mao_perspective"

    @property
    def name(self) -> str:
        return "毛选视角"

    @property
    def description(self) -> str:
        return "以《毛泽东选集》为核心的辩证分析框架：矛盾分析法、实践论、持久战、农村包围城市、统一战线、群众路线、纸老虎论。"

    @property
    def trigger_keywords(self) -> list[str]:
        return [
            "矛盾", "主要矛盾", "次要矛盾", "战略", "竞争",
            "持久战", "农村包围城市", "统一战线", "群众路线",
            "纸老虎", "实践", "实事求是", "分清敌友", "教员",
            "毛泽东", "毛选", "星火燎原", "一分为二",
        ]

    def think(self, input: str, context: dict) -> PerspectiveOutput:
        """Apply Mao Zedong's dialectical thinking to analyze the problem."""
        input_lower = input.lower()
        findings: list[str] = []
        warnings: list[str] = []
        models_applied: list[str] = []

        # --- Contradiction Analysis ---
        if any(k in input_lower for k in ["矛盾", "主要矛盾", "问题", "困境"]):
            models_applied.append("矛盾分析法")
            contradiction_analysis = self._contradiction_analysis(input)
            findings.append(contradiction_analysis)

        # --- Practice-Knowledge Cycle ---
        if any(k in input_lower for k in ["实践", "调查", "验证", "试"]):
            models_applied.append("实践论")
            practice_analysis = self._practice_analysis(input)
            findings.append(practice_analysis)

        # --- Protracted Strategy ---
        if any(k in input_lower for k in ["持久战", "长期", "短期", "劣势", "强敌"]):
            models_applied.append("持久战")
            protracted_analysis = self._protracted_analysis(input)
            findings.append(stratified_analysis)

        # --- Periphery-to-Center ---
        if any(k in input_lower for k in ["农村包围城市", "边缘", "切入", "小切口", "垂直"]):
            models_applied.append("农村包围城市")
            periphery_analysis = self._periphery_analysis(input)
            findings.append(periphery_analysis)

        # --- United Front ---
        if any(k in input_lower for k in ["统一战线", "团结", "盟友", "分清敌友", "敌人", "朋友"]):
            models_applied.append("统一战线")
            front_analysis = self._united_front_analysis(input)
            findings.append(front_analysis)

        # --- Mass Line ---
        if any(k in input_lower for k in ["群众", "用户", "一线", "调研", "需求"]):
            models_applied.append("群众路线")
            mass_analysis = self._mass_line_analysis(input)
            findings.append(mass_analysis)

        # --- Paper Tiger ---
        if any(k in input_lower for k in ["纸老虎", "强敌", "巨头", "竞争", "对手"]):
            models_applied.append("纸老虎论")
            tiger_analysis = self._paper_tiger_analysis(input)
            findings.append(tiger_analysis)

        # Default: general dialectical analysis
        if not findings:
            findings.append(self._default_analysis(input))

        # Build final analysis
        model_summary = "、".join(models_applied) if models_applied else "基本辩证分析"
        analysis = f"**毛泽东思维框架分析（{model_summary}）**\n\n"
        analysis += "\n\n".join(findings)
        analysis += f"\n\n**总结**：同志，前途是光明的，道路是曲折的。抓住主要矛盾，实事求是，从实际出发。"

        warnings.append("本框架基于《毛选》公开著作，适用于战略分析和问题诊断，不涉及政治立场评判。")
        warnings.append("矛盾分析需要充分信息支撑，信息不足时容易误判。")

        confidence = min(0.9, 0.5 + 0.15 * len(models_applied))

        return PerspectiveOutput(
            perspective_id="mao_result",
            perspective_name="毛选视角分析结果",
            analysis=analysis,
            confidence=confidence,
            warnings=warnings,
            metadata={"models_applied": models_applied},
        )

    def _contradiction_analysis(self, input: str) -> str:
        """矛盾分析法：找主要矛盾."""
        return (
            "**矛盾分析法**\n\n"
            "一切事物的发展都是由内部矛盾推动的。\n"
            "当前问题中存在多个矛盾，其中必有一个**主要矛盾**，它的存在和发展规定或影响着其他矛盾。\n\n"
            "**分析建议**：\n"
            "1. 列出当前面临的所有问题\n"
            "2. 找出那个牵一发动全身的主要矛盾\n"
            "3. 解决主要矛盾，其他矛盾往往连带解决或自然消解\n"
            "4. 注意矛盾的主要方面和次要方面的转化"
        )

    def _practice_analysis(self, input: str) -> str:
        """实践论：认识从实践中来."""
        return (
            "**实践认识循环**\n\n"
            "认识从实践中来，在实践中检验，再回到实践中去。\n"
            "没有调查就没有发言权。\n\n"
            "**分析建议**：\n"
            "1. 你对这个问题做过多少实际调查？\n"
            "2. 理论推导和实际经验是否一致？\n"
            "3. 先做一个小规模的实践验证，再全面推广\n"
            "4. '你要知道梨子的滋味，就得变革梨子，亲口吃一吃'"
        )

    def _protracted_analysis(self, input: str) -> str:
        """持久战：战略防御→相持→反攻."""
        return (
            "**持久战略**\n\n"
            "在力量对比不利时，不求速胜，以时间换空间，在持久中逐步改变力量对比。\n\n"
            "**三阶段判断**：\n"
            "• 战略防御期：保存实力，不在对方强项上硬拼\n"
            "• 战略相持期：最关键、最困难、最容易出错的阶段\n"
            "• 战略反攻期：力量对比改变后，抓住时机\n\n"
            "**分析建议**：不要因为起步小而气馁，也不要在条件不成熟时冒险。"
        )

    def _periphery_analysis(self, input: str) -> str:
        """农村包围城市：边缘切入."""
        return (
            "**农村包围城市战略**\n\n"
            "不在敌人力量最强的地方争夺，先在边缘建立根据地，再逐步包围中心。\n\n"
            "**分析建议**：\n"
            "1. 当前的核心竞争点（城市）是否是必争之地？\n"
            "2. 有没有被忽视的边缘市场或垂直场景可以先扎根？\n"
            "3. 先在一个小范围做到极致，证明模式可复制\n"
            "4. '星星之火，可以燎原'——一个小根据地就够了"
        )

    def _united_front_analysis(self, input: str) -> str:
        """统一战线：团结朋友."""
        return (
            "**统一战线分析**\n\n"
            "谁是我们的敌人？谁是我们的朋友？这个问题是革命的首要问题。\n"
            "把朋友搞得多多的，把敌人搞得少少的。\n\n"
            "**分析建议**：\n"
            "1. 列出所有利益相关方，分清敌我友\n"
            "2. 在主要矛盾上一致即可结盟，不要求所有问题一致\n"
            "3. '又团结又斗争，以斗争求团结'\n"
            "4. 根据矛盾变化动态调整联盟"
        )

    def _mass_line_analysis(self, input: str) -> str:
        """群众路线：从群众中来，到群众中去."""
        return (
            "**群众路线**\n\n"
            "从群众中来，到群众中去。领导者不是高高在上的指挥官，是群众智慧的集中者和执行者。\n\n"
            "**分析建议**：\n"
            "1. 做决策之前，先到一线去了解真实情况\n"
            "2. 把群众分散的、不系统的意见集中起来\n"
            "3. 做完决策之后，拿回一线去检验\n"
            "4. '群众是真正的英雄'"
        )

    def _paper_tiger_analysis(self, input: str) -> str:
        """纸老虎论：战略藐视，战术重视."""
        return (
            "**纸老虎论**\n\n"
            "一切貌似强大的对手，从长远看、从本质看，都是纸老虎。\n"
            "战略上藐视它，战术上重视它。\n\n"
            "**分析建议**：\n"
            "1. 战略层面：看本质、看趋势——貌似强大的对手往往有致命弱点\n"
            "2. 战术层面：每一个具体的仗都要认真打\n"
            "3. 误判真老虎为纸老虎后果严重，需要准确把握本质\n"
            "4. 既不要轻敌冒进，也不要畏敌怯战"
        )

    def _default_analysis(self, input: str) -> str:
        """Default dialectical analysis."""
        return (
            "**一分为二的辩证分析**\n\n"
            "任何事物都有两面：好事里面有危机，坏事里面有转机。\n\n"
            f"**对当前问题的基本判断**：\n{input}\n\n"
            "**建议**：运用矛盾分析法，找出主要矛盾；运用实践论，从实际出发；战略上藐视，战术上重视。"
        )
