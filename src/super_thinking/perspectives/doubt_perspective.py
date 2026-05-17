"""Doubt Perspective - 蒸馏自 alchaincyf/feynman-skill (Richard Feynman)"""

from super_thinking.perspectives._interface import Perspective, PerspectiveOutput


class DoubtPerspective(Perspective):
    """
    费曼怀疑质疑视角：知识边界、证伪精神、具象化思考。

    核心心智模型：
    1. 命名 ≠ 理解 - 知道叫什么和理解它是什么是两回事
    2. 反自欺原则 - 你最容易被自己骗
    3. 不确定性是力量 - 承认不知道比假装确定更有力量
    4. 具象化思考 - 用具体、可感知的类比替代抽象概念
    5. 深度游戏 - 跟着好奇心走，不预设「有用」或「没用」

    蒸馏来源：alchaincyf/feynman-skill
    触发词：怀疑、质疑、真的假的、怎么证明、什么意思、懂了吗、简化
    """

    @property
    def id(self) -> str:
        return "doubt"

    @property
    def name(self) -> str:
        return "费曼怀疑视角"

    @property
    def description(self) -> str:
        return (
            "费曼怀疑思维：命名≠理解（能说名字≠真懂）、反自欺（自己最容易被骗）、"
            "不确定性是力量（承认不知道比假装确定更有力量）、货物崇拜检测（空有形式缺内核）、"
            "具象化检验（能不用术语解释吗？）。专挑假设漏洞、证据不足、伪深度。"
        )

    @property
    def trigger_keywords(self) -> list[str]:
        return [
            "怀疑", "质疑", "真的吗", "怎么证明", "什么意思", "懂了吗",
            "简化", "本质", "真正的原因", "证据", "自欺", "术语",
            "命名", "理解", "抽象", "具象", "类比", "确定性",
            "feynman", "费曼",
        ]

    def think(self, input_str: str, context: dict) -> PerspectiveOutput:
        input_lower = input_str.lower()
        key_points = []
        warnings = []
        analysis_parts = []

        # ─── 模型1: 命名 ≠ 理解 ───
        if any(kw in input_lower for kw in ["理解", "懂", "知道", "概念", "理论", "原理", "本质"]):
            key_points.append("【命名≠理解】能说名字≠真懂。能用六年级水平解释吗？")
            analysis_parts.append(
                "知道一个东西叫什么，和理解它是什么、怎么运作，是完全不同的两件事。\n"
                "检测问题：\n"
                "• 我能不用任何术语解释这个吗？\n"
                "• 换一种问法我还能回答吗？\n"
                "• 能举一个具体的、可感知的例子吗？\n"
                "如果回答不了，你只是记住了名字。"
            )

        # ─── 模型2: 反自欺原则 ───
        if any(kw in input_lower for kw in ["相我相信", "认为", "判断", "结论", "观点", "以为", "确定"]):
            key_points.append("【反自欺】你最容易骗自己。有没有在选择性看证据？")
            analysis_parts.append(
                "人类最危险的认知陷阱不是被别人骗，而是被自己骗。\n"
                "做任何判断前问自己：\n"
                "• 我有没有在选择性地看证据？\n"
                "• 我是因为证据才相信，还是因为我想相信？\n"
                "• 我有没有把希望当成了事实？\n"
                "• 如果有人要反驳我，他会用什么证据？"
            )
            warnings.append("自欺是最难察觉的偏误——你不会意识到自己在骗自己")

        # ─── 模型3: 不确定性是力量 ───
        if any(kw in input_lower for kw in ["不确定", "不知道", "模糊", "复杂", "焦虑", "必须确定"]):
            key_points.append("【不确定性】「不知道」不是终点，是探索的起点")
            analysis_parts.append(
                "费曼：「能在不确定中照样前进，比追求正确答案更有力量。」\n"
                "两种态度的区分：\n"
                "❌ 「需要确定答案才能行动」→ 导致自欺或决策瘫痪\n"
                "✅ 「在不确定中照样前进」→ 保持探索和学习的开放性\n"
                "对无法证明的事情保持开放，比假装确定更有智慧。"
            )

        # ─── 模型4: 货物崇拜检测 ───
        if any(kw in input_lower for kw in ["方法", "流程", "体系", "框架", "系统", "专业", "标准"]):
            key_points.append("【货物崇拜检测】空有形式缺内核——飞机不会降落")
            analysis_parts.append(
                "货物崇拜：有科学/专业的所有外在形式，但缺少核心精神。\n"
                "检测场景：\n"
                "• 团队做了所有敏捷流程但产品没变好 → 货物崇拜敏捷\n"
                "• 写了完美报告但没验证假设 → 货物崇拜研究\n"
                "• 用了所有最新工具但效率没提升 → 货物崇拜技术\n"
                "问：这里有真正的核心精神，还是只有外表形式？"
            )

        # ─── 模型5: 具象化思考 ───
        if any(kw in input_lower for kw in ["抽象", "复杂", "理论", "解释", "概念"]):
            key_points.append("【具象化】这个东西在物理世界里长什么样？能画出来吗？")
            analysis_parts.append(
                "费曼的具象化策略：\n"
                "1. 找到一个日常生活每个人都经历过的场景\n"
                "2. 把抽象概念映射到这个场景上\n"
                "3. 检验映射是否保留了关键特征\n"
                "注意：不是所有概念都适合具象化。知道什么时候不该类比，和知道什么时候该类比一样重要。"
            )

        # ─── 证伪检验 ───
        if any(kw in input_lower for kw in ["证明", "证实", "证据", "真的", "假的", "事实"]):
            key_points.append("【证伪检验】什么证据能推翻这个结论？找不到=没验证")
            analysis_parts.append(
                "卡尔·萨根：「非凡结论需要非凡证据。」\n"
                "分析任何声称时，主动问：\n"
                "• 什么条件下这个结论会是错的？\n"
                "• 有人做过可证伪的检验吗？\n"
                "• 证据是相关还是因果？"
            )

        if not key_points:
            key_points.append("【费曼检验】尝试提及：理解/证据/怀疑/证明/抽象/货物崇拜等触发词")

        return PerspectiveOutput(
            perspective_id=self.id,
            perspective_name=self.name,
            analysis="\n\n".join(analysis_parts) if analysis_parts else "从费曼怀疑视角分析...",
            key_points=key_points,
            confidence=0.8,
            tags=["怀疑", "费曼", "证伪", "具象化", "反自欺", "货物崇拜"],
            warnings=warnings,
            metadata={
                "source": "https://github.com/alchaincyf/feynman-skill",
                "mental_models": [
                    "命名≠理解",
                    "反自欺原则",
                    "不确定性是力量",
                    "货物崇拜检测",
                    "具象化思考",
                    "证伪精神"
                ],
                "perspective_type": "skepticism"
            },
        )
