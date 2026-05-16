"""Zhang Xuefeng Perspective - 蒸馏自 alchaincyf/zhangxuefeng-skill.

张雪峰的思维操作系统：社会筛子论、选择大于努力、就业倒推法、阶层现实主义、争议即传播。
注：张雪峰已于2026年3月24日去世，角色扮演基于其生前公开言论。
"""

from super_thinking.perspectives._interface import Perspective, PerspectiveOutput


class ZhangxuefengPerspective(Perspective):
    """张雪峰认知操作系统 - 用就业数据审视教育选择、用阶层现实主义评估机会、用社会筛子论分析路径。"""

    @property
    def id(self) -> str:
        return "zhangxuefeng_perspective"

    @property
    def name(self) -> str:
        return "张雪峰视角"

    @property
    def description(self) -> str:
        return "以张雪峰实用主义教育观为核心的思维框架：社会筛子论、选择大于努力、就业倒推法、阶层现实主义、争议即传播。适用于教育选择、职业规划、阶层流动分析。"

    @property
    def trigger_keywords(self) -> list[str]:
        return [
            "张雪峰", "雪峰", "高考", "考研", "志愿", "专业",
            "就业", "择业", "选专业", "考公", "体制内",
            "学历", "学校", "普通家庭", "寒门",
            "阶层", "翻身", "工资", "薪资",
        ]

    def think(self, input_str: str, context: dict) -> PerspectiveOutput:
        input_lower = input_str.lower()
        key_points = []
        warnings = []
        analysis_parts = []

        # === 心智模型1: 社会筛子论 ===
        # 社会用学历筛孩子、房子筛父母、工作筛家庭。普通家庭的可控变量只有学历。
        if any(k in input_lower for k in [
            "社会", "筛选", "学历", "名校", "普通家庭", "寒门",
            "穷", "翻身", "改变命运", "阶层", "出头",
        ]):
            key_points.append("【社会筛子论】中国几乎所有500强都说学历不重要，但他们会去齐齐哈尔大学招聘吗？")
            analysis_parts.append(
                "【社会筛子论】\n"
                "张雪峰核心隐喻：「社会就是一个大筛子，用学历筛孩子，用房子筛父母，用工作筛家庭。」\n"
                "「有钱人的孩子选错专业可以重来，穷人家的孩子错一步可能全盘皆输。」\n"
                "分析任何教育/就业问题时，先问：这个选择经不经得起社会筛子的筛？\n"
                "普通家庭的可控变量只有学历——其他变量（人脉、资本、背景）不在你手上。"
            )

        # === 心智模型2: 选择 > 努力 ===
        if any(k in input_lower for k in [
            "选择", "努力", "方向", "赛道", "转行", "转型",
            "该选哪个", "志愿", "专业", "考研", "考公",
        ]):
            key_points.append("【选择>努力】方向错误的努力是浪费，选对赛道比拼命奔跑重要")
            analysis_parts.append(
                "【选择 > 努力】\n"
                "张雪峰两本书直接命名：《方向比努力更重要》《选择比努力更重要》。\n"
                "「别用战术上的勤奋，掩盖战略上的懒惰。」\n"
                "适用：高考选专业、考研选院校、第一份工作选行业——这三个选择的权重远大于「你有多努力」。\n"
                "局限：可能导致选择焦虑，过度纠结选哪条路反而不行动。"
            )

        # === 心智模型3: 就业倒推法 ===
        # 从毕业后的就业数据倒推今天的专业选择，不看前3%天才，不看后5%极端，看中间20%-50%普通毕业生。
        if any(k in input_lower for k in [
            "专业", "就业", "薪资", "工资", "毕业", "找工作",
            "offer", "行业", "岗位", "职业发展", "中位数",
            "天坑", "生化环材", "计算机", "人工智能",
        ]):
            key_points.append("【就业倒推法】不看前3%天才，不看后5%极端，看中间50%普通毕业生的去向")
            analysis_parts.append(
                "【就业倒推法】\n"
                "「理工科选专业，文科选学校」——理工科的技术壁垒让专业决定就业。\n"
                "「生化环材四天王，没读博士别逞强」——从就业数据倒推出「天坑专业」概念。\n"
                "评估任何教育/职业选择时，不看宣传册上的光鲜案例，去看普通从业者5年后的中位数收入和发展路径。\n"
                "调研时搜索：中位数薪资、就业率、真实去向（不是学校宣传的）。"
            )

        # === 心智模型4: 阶层现实主义 ===
        # 家里没矿别谈理想，先谋生再谋爱，先站稳再登高。
        if any(k in input_lower for k in [
            "理想", "现实", "生存", "谋生", "家庭条件", "背景",
            "有钱", "没钱", "穷人", "富二代", "阶级",
        ]):
            key_points.append("【阶层现实主义】家里没矿别谈理想，先谋生再谋爱，先站稳再登高")
            analysis_parts.append(
                "【阶层现实主义】\n"
                "张雪峰：「先谋生，再谋爱；先站稳，再登高。」\n"
                "「你的工资，永远和你的不可替代性成正比。」\n"
                "给建议时，先问对方家庭背景和经济条件。同一问题，对不同阶层答案完全不同。\n"
                "有试错成本的家庭可以追求热爱，没有试错成本的家庭必须追求确定性。\n"
                "局限：容易滑向「穷人认命」的宿命论。"
            )

        # === 心智模型5: 争议即传播 ===
        # 温吞的建议没人记住，把观点推到极端才有传播力。
        if any(k in input_lower for k in [
            "传播", "流量", "ip", "个人品牌", "影响力", "营销",
            "争议", "话题", "热度", "媒体", "内容",
        ]):
            key_points.append("【争议即传播】核心观点绝不让步，只调整表达方式——道歉但不收回判断")
            analysis_parts.append(
                "【争议即传播】\n"
                "「打晕孩子别报新闻学」→ 2023年年度教育话题。\n"
                "张雪峰策略：核心观点绝不让步，只调整表达方式。涉及措辞不当可以道歉，涉及核心判断死不松口。\n"
                "局限：争议是双刃剑——2025年被网信办处罚封禁，嘴巴比脑子快是真实的代价。"
            )

        # === 默认分析 ===
        if not analysis_parts:
            analysis_parts.append(
                f"从张雪峰视角分析：{input_str}\n\n"
                "【张雪峰第一问】你孩子多少分？什么省的？家里做什么的？想去哪个城市？\n"
                "灵魂追问——通过连续追问快速建立决策框架，不上来就给答案。\n\n"
                "【核心问题】\n"
                "1. 这个选择的中位数毕业生去了哪？薪资多少？（就业倒推）\n"
                "2. 这个选择经不经得起社会筛子的筛？（社会筛子论）\n"
                "3. 你家孩子有没有试错成本？（阶层现实主义）\n"
                "4. 10年后会不会后悔选了这个方向？（选择>努力）"
            )
            key_points.append("【通用】不问前3%天才，问中间50%普通毕业生的情况")

        return PerspectiveOutput(
            perspective_id=self.id,
            perspective_name=self.name,
            analysis="\n\n".join(analysis_parts) if analysis_parts else f"从张雪峰视角分析：{input_str}",
            key_points=key_points,
            confidence=0.75,
            tags=[self.id, "教育选择", "阶层流动", "就业导向", "实用主义"],
            warnings=[
                "张雪峰已于2026年3月24日去世，其观点基于生前公开言论",
                "框架适用于普通家庭、就业导向的选择，对家境优越或追求学术的人可能反而是束缚",
                "就业数据有滞后性，今天的热门专业可能5年后饱和",
            ],
            metadata={
                "source": "https://github.com/alchaincyf/zhangxuefeng-skill",
                "mental_models_count": 5,
            },
        )

    def _matches(self, text: str, keywords: list[str]) -> bool:
        text_lower = text.lower()
        return any(kw.lower() in text_lower for kw in keywords)
