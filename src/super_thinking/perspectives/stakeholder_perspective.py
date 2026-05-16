"""Stakeholder Perspective - 蒸馏自 alchaincyf/munger-skill (Charlie Munger)"""

from super_thinking.perspectives._interface import Perspective, PerspectiveOutput


class StakeholderPerspective(Perspective):
    """
    芒格利益相关者视角：多元思维、激励结构、Lollapalooza效应。

    核心心智模型：
    1. 多元思维模型 - 从多个学科视角审视，单一视角=锤子找钉子
    2. 逆向思考 - 正面解决不了就反过来想
    3. Lollapalooza效应 - 多种偏误同时发力产生极端非线性结果
    4. 激励机制决定一切 - 理解任何人的行为，先看激励结构
    5. 能力圈+意见资格制 - 知道自己不知道什么更重要
    6. 葡萄干与粪便法则 - 一个致命缺陷污染整体

    蒸馏来源：alchaincyf/munger-skill
    触发词：各方、利益、激励、立场、冲突、博弈、权力、关系、诉求
    """

    @property
    def id(self) -> str:
        return "stakeholder"

    @property
    def name(self) -> str:
        return "芒格利益相关者视角"

    @property
    def description(self) -> str:
        return (
            "芒格利益相关者分析：激励诊断（理解任何人的行为先看激励结构）、多元视角（至少3个学科视角审视）、"
            "逆向排除（不问怎么赢而问怎么输）、Lollapalooza效应（多种因素同时强化时的极端结果）、"
            "葡萄干法则（一个致命缺陷污染整体）。识别各方立场、隐性冲突、潜在联盟机会。"
        )

    @property
    def trigger_keywords(self) -> list[str]:
        return [
            "各方", "利益", "激励", "立场", "冲突", "博弈", "权力", "关系",
            "诉求", "矛盾", "联盟", "Stakeholder", "incentive", "芒格", "munger",
            "受益", "受损", "谁想要", "谁损失", "谁获益", "博弈论",
        ]

    def think(self, input_str: str, context: dict) -> PerspectiveOutput:
        input_lower = input_str.lower()
        key_points = []
        warnings = []
        analysis_parts = []

        # ─── 模型: 激励诊断（核心） ───
        if any(kw in input_lower for kw in ["利益", "激励", "动机", "立场", "诉求", "受益", "受损", "获益", "损失"]):
            key_points.append("【激励诊断】谁在赚钱？谁在承担风险？两者对齐吗？")
            analysis_parts.append(
                "激励机制决定一切：理解任何人的行为，先看激励结构。\n"
                "激励诊断步骤：\n"
                "1. 谁在这个局面里赚钱？方式是什么？\n"
                "2. 谁在承担风险？风险和收益是否匹配？\n"
                "3. 激励是否对齐？不对齐 = 危险信号\n\n"
                "「告诉我他的激励，我就能预测他的行为。」——芒格"
            )

        # ─── 模型: 多元视角 ───
        if any(kw in input_lower for kw in ["决策", "选择", "方案", "计划", "策略", "分析", "判断"]):
            key_points.append("【多元视角】至少3个学科视角审视——心理学/经济学/博弈论")
            analysis_parts.append(
                "多元思维模型：单一学科必然导致系统性盲区。遇到任何决策，至少从3个学科视角审视：\n"
                "• 心理学（人的行为动机）\n"
                "• 经济学（激励结构、机会成本）\n"
                "• 博弈论（多方互动、零和vs正和）\n"
                "• 物理学（系统动力学、平衡）\n"
                "• 生物学（进化、适应）\n\n"
                "如果只从一个角度看，你在「拿锤子找钉子」。"
            )
            warnings.append("单一视角分析往往是偏见——先强制自己列出至少3个不同视角")

        # ─── 模型: 逆向思考 ───
        if any(kw in input_lower for kw in ["冲突", "矛盾", "问题", "失败", "障碍", "困难"]):
            key_points.append("【逆向排除】先问怎么必定失败→然后避开。不问怎么赢，问怎么不输。")
            analysis_parts.append(
                "逆向思考（Inversion）：正面解决不了的问题，反过来想。\n"
                "操作步骤：\n"
                "1. 列出所有「一定会导致失败的路径」\n"
                "2. 避开这些路径\n"
                "3. 剩下的选择自然不会太差\n\n"
                "芒格：「我只想知道我会死在哪里，这样我就永远不会去那里。」"
            )

        # ─── 模型: Lollapalooza效应 ───
        if any(kw in input_lower for kw in ["加剧", "强化", "极端", "狂热", "泡沫", "群体", "一边倒", "情绪"]):
            key_points.append("【Lollapalooza检测】多种偏误同时作用？社会认同+过度乐观+被剥夺超级反应=危险")
            analysis_parts.append(
                "Lollapalooza效应：多种心理偏误同时发力、相互强化，产生极端非线性结果。\n"
                "当看到一件事迅速升温时（市场狂热/舆论一边倒/团队集体乐观），问：\n"
                "这里有几种偏误在同时作用？\n"
                "常见组合：社会认同（别人都这样）+ 过度乐观（只涨不跌）+ 被剥夺超级反应（错过就亏了）\n"
                "= Lollapalooza = 危险。"
            )

        # ─── 模型: 葡萄干与粪便法则 ───
        if any(kw in input_lower for kw in ["组合", "整体", "混合", "搭配", "合作", "联盟", "打包"]):
            key_points.append("【葡萄干法则】有一个致命缺陷，整体就是有毒的——好元素无法中和坏的")
            analysis_parts.append(
                "葡萄干与粪便法则：如果混合一个组合里有一个致命缺陷，整体就是有毒的。\n"
                "评估多方合作/产品组合/投资组合时：\n"
                "• 找到最弱的环节——这就是整体的真实水平\n"
                "• 好的元素无法中和坏的元素\n"
                "• 「和坏人做了一笔好交易，你通常是输家。」——芒格"
            )

        # ─── 博弈结构分析 ───
        if any(kw in input_lower for kw in ["博弈", "竞争", "对抗", "合作", "谈判", "交易"]):
            key_points.append("【博弈结构】零和还是正和？先分清楚再进场")
            analysis_parts.append(
                "博弈结构诊断：\n"
                "• 零和博弈（我的所得=你的所失）→ 谈判极其重要\n"
                "• 正和博弈（可以共同受益）→ 合作是优选\n"
                "• 负和博弈（双方都受损）→ 避免或止损\n\n"
                "同时问：这是重复博弈还是一次性博弈？重复博弈中诚信有长期价值。"
            )

        if not key_points:
            key_points.append("【芒格扫描】尝试提及：激励/利益/冲突/博弈/逆向/多视角等触发词")

        return PerspectiveOutput(
            perspective_id=self.id,
            perspective_name=self.name,
            analysis="\n\n".join(analysis_parts) if analysis_parts else "从芒格利益相关者视角分析...",
            key_points=key_points,
            confidence=0.8,
            tags=["利益相关者", "芒格", "激励", "博弈", "多元思维", "逆向思考"],
            warnings=warnings,
            metadata={
                "source": "https://github.com/alchaincyf/munger-skill",
                "mental_models": [
                    "多元思维模型",
                    "逆向思考",
                    "Lollapalooza效应",
                    "激励机制决定一切",
                    "能力圈+意见资格制",
                    "葡萄干与粪便法则"
                ],
                "perspective_type": "stakeholder_analysis"
            },
        )
