"""Past Experience Perspective - 基于达尔文进化论 + 认知心理学"""

from super_thinking.perspectives._interface import Perspective, PerspectiveOutput


class PastExperiencePerspective(Perspective):
    """
    过往经历视角：从历史经验中提取模式、类比推理、教训学习。

    核心心智模型：
    1. 达尔文进化机制 - 变异+选择+遗传，环境压力是主驱动力
    2. 自然选择类比 - 好策略像好基因一样被保留，坏策略被淘汰
    3. 认知锚定 - 过去的成功经验会成为未来的判断锚点（好/坏两方面）
    4. 确认偏误回溯 - 人倾向于选择性地记住所验证自己观点的经历
    5. 模式识别 - 从历史数据中提取可复用的教训，而非记住所有细节

    适用场景：从历史案例提取模式、评估「以前这样做是否有效」、类比推理
    触发词：以前、之前、过去、曾经、历史经验、教训、成功案例、失败案例、类比
    """

    @property
    def id(self) -> str:
        return "past_experience"

    @property
    def name(self) -> str:
        return "达尔文经验视角"

    @property
    def description(self) -> str:
        return (
            "达尔文经验学习框架：进化机制应用于经验分析（变异+选择+遗传）、自然选择类比（好策略像好基因被保留）、"
            "认知锚定（过去经验成为判断锚点）、确认偏误回溯警惕（选择性记忆）、模式识别（提取可复用教训而非记住所有细节）。"
            "从历史案例提取模式，评估以前类似情况的做法，判断经验是否仍适用。"
        )

    @property
    def trigger_keywords(self) -> list[str]:
        return [
            "以前", "之前", "过去", "曾经", "历史经验", "教训", "成功案例",
            "失败案例", "类比", "类似情况", "重复", "模式", "历史", "达尔文",
            "进化", "经验", "经历", "借鉴", "参照",
        ]

    def think(self, input_str: str, context: dict) -> PerspectiveOutput:
        input_lower = input_str.lower()
        key_points = []
        warnings = []
        analysis_parts = []

        # ─── 模型1: 达尔文进化机制 ───
        if any(kw in input_lower for kw in ["进化", "变异", "选择", "遗传", "适应", "演化", "压力"]):
            key_points.append("【进化机制】变异+选择+遗传：好策略像好基因一样被保留")
            analysis_parts.append(
                "达尔文进化框架应用于经验分析：\n"
                "• 变异：新策略不断产生（试错）\n"
                "• 选择：环境压力筛选（市场竞争/用户选择/结果验证）\n"
                "• 遗传：好策略被复制传承\n\n"
                "评估经验时问：这个策略是经过选择压力验证的，还是只在稳定环境中有效？\n"
                "环境变了=选择压力变了=过去的好策略可能变成坏策略。"
            )

        # ─── 模型2: 自然选择类比 ───
        if any(kw in input_lower for kw in ["策略", "方法", "方案", "选择", "竞争", "市场", "生存"]):
            key_points.append("【自然选择类比】这个策略在什么环境下被选择？环境变了吗？")
            analysis_parts.append(
                "类比自然选择评估策略：\n"
                "1. 这个策略在什么「环境」中被验证？（技术环境/市场竞争/组织文化）\n"
                "2. 环境变了吗？（技术更新/市场成熟/团队扩张）\n"
                "3. 如果环境变了，这个策略还有效吗？\n\n"
                "成功案例需要问：成功是因为策略好，还是因为环境恰好配合？"
            )

        # ─── 模型3: 认知锚定 ───
        if any(kw in input_lower for kw in ["经验", "成功", "失败", "判断", "决策", "以前", "过去"]):
            key_points.append("【认知锚定警惕】过去经验会成为未来判断的锚点——可能是资产也可能是负债")
            analysis_parts.append(
                "认知锚定效应：\n"
                "• 过去的成功经验 → 可能导致过度自信（这次也会成功）\n"
                "• 过去的失败教训 → 可能导致过度规避（这次也会失败）\n"
                "两者都可能是偏误，关键是识别当前情境与过去情境的差异。\n\n"
                "检验问题：\n"
                "• 当时成功的关键因素现在还存在吗？\n"
                "• 这个判断是真正基于分析，还是只是「上次这样做成功了」？"
            )
            warnings.append("锚定效应：过去的成功/失败经验会不成比例地影响当前判断——需要主动检验情境是否真正相似")

        # ─── 模型4: 确认偏误回溯 ───
        if any(kw in input_lower for kw in ["相信", "认为", "结论", "观点", "案例", "证据"]):
            key_points.append("【确认偏误回溯】你是在分析历史，还是在选择性记忆来验证已有观点？")
            analysis_parts.append(
                "确认偏误回溯：人倾向于选择性地记住所验证自己观点的经历，忽略相反案例。\n"
                "检验方法：\n"
                "1. 主动问：「有没有反例？有没有失败案例？」\n"
                "2. 列出这个经验的反例（如果找不到，可能是偏误）\n"
                "3. 芒格的「达尔文协议」：等量时间寻找反面证据\n\n"
                "真正从历史学习的标志是：你能同时说清楚支持的案例和反对的案例。"
            )

        # ─── 模型5: 模式识别 vs 记住细节 ───
        if any(kw in input_lower for kw in ["模式", "规律", "本质", "关键", "核心", "结构"]):
            key_points.append("【模式识别】记住可复用的教训，不是记住所有细节")
            analysis_parts.append(
                "有效经验学习的标志是模式识别，不是记住所有细节。\n"
                "应该提取：\n"
                "• 这个情况下，什么原则/规律在起作用？\n"
                "• 这个原则在什么条件下适用？什么条件下失效？\n"
                "• 能用一句话总结这个教训吗？\n\n"
                "记住细节但提取不了模式=无效学习。记住模式+知道适用条件=有效学习。"
            )

        # ─── 历史案例调用 ───
        memory_data = context.get("memory", [])
        if memory_data and len(memory_data) > 0:
            key_points.append(f"【记忆调用】发现 {len(memory_data)} 条相关历史记忆可参考")
            analysis_parts.append(
                "从记忆检索到的相关经历：\n"
                + "\n".join([f"• {m.get('text', m)[:100]}" for m in memory_data[:3]])
            )

        if not key_points:
            key_points.append("【达尔文扫描】尝试提及：经验/模式/成功案例/失败案例/进化/锚定等触发词")

        return PerspectiveOutput(
            perspective_id=self.id,
            perspective_name=self.name,
            analysis="\n\n".join(analysis_parts) if analysis_parts else "从达尔文经验视角分析...",
            key_points=key_points,
            confidence=0.75,
            tags=["经验学习", "达尔文", "认知偏误", "模式识别", "锚定效应", "历史类比"],
            warnings=warnings,
            metadata={
                "source": "达尔文进化论 + 认知心理学",
                "mental_models": [
                    "达尔文进化机制",
                    "自然选择类比",
                    "认知锚定警惕",
                    "确认偏误回溯",
                    "模式识别学习"
                ],
                "perspective_type": "experience_based"
            },
        )
