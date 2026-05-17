"""Elon Musk Perspective - 蒸馏自 alchaincyf/elon-musk-skill.

马斯克的思维操作系统：渐近极限法、五步算法、存在主义锚定、垂直整合、快速迭代。
"""

from super_thinking.perspectives._interface import Perspective, PerspectiveOutput


class ElonPerspective(Perspective):
    """马斯克认知操作系统 - 用物理极限审视成本、用五步算法审视流程、用激进迭代审视执行。"""

    @property
    def id(self) -> str:
        return "elon_perspective"

    @property
    def name(self) -> str:
        return "马斯克视角"

    @property
    def description(self) -> str:
        return "以马斯克第一性原理为核心的思维框架：拆解成本结构、质疑行业默认假设、评估垂直整合机会、设计激进可迭代的执行路径。"

    @property
    def trigger_keywords(self) -> list[str]:
        return [
            "马斯克", "elon", "musk", "第一性原理", "白痴指数",
            "渐近极限", "垂直整合", "五步算法", "成本拆解",
            "成本合理吗", "能不能垂直整合", "这个成本",
            "降本", "降成本", "供应链溢价",
        ]

    def think(self, input_str: str, context: dict) -> PerspectiveOutput:
        input_lower = input_str.lower()
        key_points = []
        warnings = []
        analysis_parts = []

        # === 心智模型1: 渐近极限法 ===
        # 先算物理定律允许的理论最优值，再分析现实为什么离这个值这么远。
        if any(k in input_lower for k in [
            "成本", "价格", "贵", "便宜", "贵了", "划算", "多少钱",
            "bom", "供应链", "原材料", "材料成本", "白痴指数",
        ]):
            key_points.append("【渐近极限法】先算理论最低成本：原材料值多少钱？当前价格是理论值的多少倍？")
            analysis_parts.append(
                "【渐近极限法】\n"
                "马斯克式的第一步：不算「合理价格」，算「物理极限价格」。\n"
                "问自己：这个东西的原材料在大宗商品市场值多少钱？\n"
                "如果成品价格是原材料成本的5倍以上——中间全是信息不透明税，有巨大的压缩空间。\n"
                "工具：白痴指数 = 成品价格 / 原材料成本。指数越高，改进空间越大。"
            )

        # === 心智模型2: 五步算法 ===
        # 先质疑需求是否存在，再删除，再简化，再加速，最后才自动化。
        if any(k in input_lower for k in [
            "流程", "优化", "自动化", "删", "砍", "简化",
            "效率", "多余", "功能", "需求", "为什么要做",
            "这个步骤", "能不能更快", "流程有必要吗",
        ]):
            key_points.append("【五步算法】先问：这个功能/步骤为什么存在？谁提出的需求？")
            analysis_parts.append(
                "【五步算法】\n"
                "马斯克的执行顺序：\n"
                "1. 质疑需求——每条需求必须附上提出者名字，聪明人提出的需求最危险\n"
                "2. 删除——删到删不动为止，删掉的东西至少有10%应该加回来\n"
                "3. 简化——只有删除完成后才允许优化\n"
                "4. 加速——缩短循环时间\n"
                "5. 自动化——最后才考虑\n"
                "警告：自动化一个不该存在的流程，是最大的浪费。"
            )

        # === 心智模型3: 存在主义锚定 ===
        # 一切决策锚定在「人类文明存续」或「多行星物种」尺度。
        if any(k in input_lower for k in [
            "使命", "长期", "人类", "文明", "战略", "方向",
            "愿景", "多行星", "可持续", "能源转型", "值得做吗",
        ]):
            key_points.append("【存在主义锚定】把决策锚定在「这在人类文明尺度上是否重要」")
            analysis_parts.append(
                "【存在主义锚定】\n"
                "马斯克把所有事业统一在两个文明级命题下：\n"
                "可持续能源（Tesla）和多行星物种（SpaceX）。\n"
                "任何决策用这个尺度过滤：这件事要么解决一个问题，要么其他都不重要。\n"
                "修辞工具：把重要议题框定为existential threat，让温和反驳显得不够认真。"
            )

        # === 心智模型4: 垂直整合即物理必然 ===
        # 白痴指数高的领域，供应链中间层是在收信息不透明税，垂直整合是降低成本的物理必然。
        if any(k in input_lower for k in [
            "整合", "外包", "供应商", "中间商", "自己做", "采购",
            "供应链", "自制", "外采", "合作", "合作方",
        ]):
            key_points.append("【垂直整合】白痴指数高 → 供应链中间层在收信息税 → 垂直整合是物理必然")
            analysis_parts.append(
                "【垂直整合即物理必然】\n"
                "如果白痴指数高（成品价格远超原材料成本），垂直整合不是偏好，是必然。\n"
                "SpaceX自制85%零部件，Tesla自建电池工厂和充电网络。\n"
                "问：供应链哪个环节溢价最高？我能不能绕过中间商直接获取原材料价值？\n"
                "如果差距大于5倍，垂直整合值得考虑。"
            )

        # === 心智模型5: 快速迭代 > 完美计划 ===
        # 把激进时间线当管理工具，接受大量失败作为加速学习的代价。
        if any(k in input_lower for k in [
            "迭代", "失败", "时间线", "计划", "测试", "原型",
            "快速", "激进", "交付", "mvp", "先做", "后验证",
            "实验", "试错",
        ]):
            key_points.append("【快速迭代】Failure is an option——不出错意味着不够创新")
            analysis_parts.append(
                "【快速迭代 > 完美计划】\n"
                "马斯克概率性自我认知：「我说的有些话是不对的，应该被纠正。」\n"
                "把自己当作会出错的信息系统，不维护正确性。\n"
                "激进时间线 = 管理工具，制造紧迫感。\n"
                "SpaceX前三次发射全炸，第四次成功——中间的失败是学习，不是浪费。"
            )

        # === 默认分析（没有触发特定模型） ===
        if not analysis_parts:
            analysis_parts.append(
                f"从马斯克视角分析：{input_str}\n\n"
                "【核心问题】\n"
                "1. 这个问题的理论最低成本/最快时间是多少？\n"
                "2. 哪个环节在加价？能不能垂直整合掉？\n"
                "3. 这个需求是谁提出的？能删掉吗？\n"
                "4. 物理定律允许的最优值和现实差距有多大？\n\n"
                "【马斯克第一问】原材料值多少钱？白痴指数是多少？"
            )
            key_points.append("【通用】先算渐近极限，再分析差距来源")

        return PerspectiveOutput(
            perspective_id=self.id,
            perspective_name=self.name,
            analysis="\n\n".join(analysis_parts) if analysis_parts else f"从马斯克视角分析：{input_str}",
            key_points=key_points,
            confidence=0.75,
            tags=[self.id, "第一性原理", "成本拆解", "垂直整合", "快速迭代"],
            warnings=[
                "马斯克框架在物理/工程领域极强，在政治/社会协调/公关领域系统性弱",
                "时间线预估至少乘以2-3倍才接近现实",
            ],
            metadata={
                "source": "https://github.com/alchaincyf/elon-musk-skill",
                "mental_models_count": 5,
            },
        )

    def _matches(self, text: str, keywords: list[str]) -> bool:
        text_lower = text.lower()
        return any(kw.lower() in text_lower for kw in keywords)
