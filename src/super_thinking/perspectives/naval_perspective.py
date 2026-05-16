"""Naval Ravikant Perspective - 蒸馏自 alchaincyf/naval-skill.

Naval的思维操作系统：杠杆思维、特定知识、欲望即合同、重新定义、痛苦系统化重构。
"""

from super_thinking.perspectives._interface import Perspective, PerspectiveOutput


class NavalPerspective(Perspective):
    """Naval认知操作系统 - 用杠杆思维评估机会、用特定知识定位自己、用欲望管理追求内在平和。"""

    @property
    def id(self) -> str:
        return "naval_perspective"

    @property
    def name(self) -> str:
        return "Naval视角"

    @property
    def description(self) -> str:
        return "以Naval Ravikant财富与幸福观为核心的思维框架：杠杆思维（4种）、特定知识、欲望即合同、重新定义术、痛苦系统化重构。"

    @property
    def trigger_keywords(self) -> list[str]:
        return [
            "naval", "纳瓦尔", "财富", "杠杆", "特定知识",
            "specific knowledge", "欲望", "幸福", "自由",
            "创业", "职业", "选择", "赚钱", "不需要许可",
            "财务自由", "被动收入", "复利", "不快乐", "焦虑",
        ]

    def think(self, input_str: str, context: dict) -> PerspectiveOutput:
        input_lower = input_str.lower()
        key_points = []
        warnings = []
        analysis_parts = []

        # === 心智模型1: 杠杆思维 ===
        # 不要用时间换钱，要用可复制的系统换钱。代码和媒体是新时代的无许可杠杆。
        if any(k in input_lower for k in [
            "杠杆", "创业", "职业", "工作", "赚钱", "财富",
            "收入", "商业模式", "规模化", "复制", "被动",
            "时间换钱", "财富创造", "财务",
        ]):
            key_points.append("【杠杆思维】代码和媒体是无许可杠杆——不需要任何人批准，边际成本为零")
            analysis_parts.append(
                "【杠杆思维（Leverage）】\n"
                "Naval把杠杆分为四种：\n"
                "1. 劳动力（他人为你工作）— 最古老，需要管理\n"
                "2. 资本（钱为你工作）— 需要许可（别人给你钱）\n"
                "3. 代码（软件为你工作）— 无需许可，边际成本为零\n"
                "4. 媒体（内容为你工作）— 无需许可，边际成本为零\n\n"
                "核心：一个人+代码+媒体，可以产生过去需要千人公司才能产生的影响力。\n"
                "面对任何机会问：「这有杠杆吗？我的投入能被多少倍放大？需要谁的许可？」"
            )

        # === 心智模型2: 特定知识 ===
        # 你最大的竞争力是那些像玩一样的工作——别人觉得苦，你觉得有趣的事。
        if any(k in input_lower for k in [
            "擅长", "优势", "能力", "竞争力", "知识", "专业",
            "技能", "经验", "独特", "差异化", "热爱",
            "好奇心", "判断力", "直觉",
        ]):
            key_points.append("【特定知识】如果有人能写书教别人做你做的事，那不是特定知识——做起来像在玩才是")
            analysis_parts.append(
                "【特定知识（Specific Knowledge）】\n"
                "特定知识不是「技能」。技能可以被培训、教材化、批量生产。\n"
                "特定知识是你独特的组合——你的好奇心、经历、判断力的交叉点。\n\n"
                "识别方法：\n"
                "- 如果有人能写一本书教别人做你做的事 → 那不是特定知识\n"
                "- 如果你做这件事时觉得像在玩 → 接近了\n"
                "- 如果你在这个领域的判断比大多数人好，但你说不清为什么 → 这就是\n\n"
                "Naval自己的特定知识：快速吸收跨领域信息→看到模式→用极简语言重新表达→说服他人。"
            )

        # === 心智模型3: 欲望即合同 ===
        # 每一个欲望都是你跟不快乐签的合同。焦虑来自欲望的并发冲突。
        if any(k in input_lower for k in [
            "欲望", "焦虑", "不快乐", "幸福", "快乐", "追求",
            "选择", "纠结", "贪心", "太多事", "精力不够",
            "欲望管理", "减少欲望", "断舍离",
        ]):
            key_points.append("【欲望即合同】一次只保留一个欲望——焦虑来自欲望的并发冲突")
            analysis_parts.append(
                "【欲望即合同（Desire as Contract）】\n"
                "Naval：「每一个欲望都是你跟不快乐签的合同——只要我没得到X，我就不快乐。」\n\n"
                "解法不是消灭欲望，而是「一次只保留一个」。\n"
                "「I try to keep my desires as few as possible. At any given time, I try to have only one desire.」\n\n"
                "应用：焦虑时列出所有当前欲望——你会发现焦虑来自欲望的并发冲突，不是精力不够。"
            )

        # === 心智模型4: 重新定义术 ===
        # Naval最核心的思维+修辞策略是重新定义关键词，一旦接受新定义，结论自动成立。
        if any(k in input_lower for k in [
            "定义", "什么是", "财富", "幸福", "退休", "成功",
            "自由", "富有", "赚钱", "竞争", "运气",
        ]):
            key_points.append("【重新定义术】先重新定义关键词——一旦接受新定义，结论自然成立")
            analysis_parts.append(
                "【重新定义术（Redefine the Word, the Conclusion Follows）】\n"
                "Naval最核心的思维+修辞策略：\n\n"
                "经典重定义案例：\n"
                "｜常规定义 ｜ Naval的定义 ｜ 结论 ｜\n"
                "｜财富=很多钱 ｜ 财富=睡觉时也在赚的资产 ｜ 工资不是财富，资产才是 ｜\n"
                "｜退休=不工作 ｜ 退休=只做想做的事 ｜ 他「已经退休了」即使还在创业 ｜\n"
                "｜幸福=得到想要的 ｜ 幸福=没有欲望的状态 ｜ 减少欲望比实现欲望更有效 ｜\n\n"
                "面对任何困难问题，先问：「我们在用什么定义？如果重新定义，问题本身是否会消失？」"
            )

        # === 心智模型5: 痛苦→系统化重构 ===
        # 不修复个案，重构产生问题的系统。
        if any(k in input_lower for k in [
            "挫折", "痛苦", "不公平", "系统", "问题", "创业失败",
            "教训", "经验", "结构性", "制度", "改变",
        ]):
            key_points.append("【痛苦系统化重构】不妥协不沉沦——把个人创伤转化为帮助所有人的系统性解决方案")
            analysis_parts.append(
                "【痛苦→系统化重构（Pain to Systemic Solution）】\n"
                "Naval的行动记录：\n"
                "Epinions被VC欺骗 → 创建Venture Hacks教所有创始人防骗\n"
                "融资市场信息不对称 → 创建AngelList让融资透明化\n"
                "法律限制民主化投资 → 游说推动JOBS Act\n"
                "自己不开心 → 系统性研究幸福并公开分享\n\n"
                "关键：跳到更高一层重构产生问题的结构，不在同一个层面上修复。"
            )

        # === 默认分析 ===
        if not analysis_parts:
            analysis_parts.append(
                f"从Naval视角分析：{input_str}\n\n"
                "【Naval第一问】这有杠杆吗？你的产出和投入时间是线性关系还是指数关系？\n\n"
                "【核心问题】\n"
                "1. 这需要谁的许可？有没有无需许可的路径？（杠杆）\n"
                "2. 这是特定知识吗？做起来像在玩吗？（特定知识）\n"
                "3. 这个欲望有几个？并发冲突吗？（欲望）\n"
                "4. 我们在用什么定义？（重新定义）"
            )
            key_points.append("【通用】先问杠杆类型，再判断是不是特定知识")

        return PerspectiveOutput(
            perspective_id=self.id,
            perspective_name=self.name,
            analysis="\n\n".join(analysis_parts) if analysis_parts else f"从Naval视角分析：{input_str}",
            key_points=key_points,
            confidence=0.75,
            tags=[self.id, "杠杆", "特定知识", "财富", "幸福", "欲望管理"],
            warnings=[
                "Naval框架对起点较高的人最有效，对完全从零开始的人可能缺少「如何先活下来」的部分",
                "Epinions创伤对他的世界观影响很大（反建制姿态），不完全是纯理论推导",
                "有推广自己有财务利益项目的记录（Zcash案例），相关观点需额外审视",
            ],
            metadata={
                "source": "https://github.com/alchaincyf/naval-skill",
                "mental_models_count": 5,
            },
        )

    def _matches(self, text: str, keywords: list[str]) -> bool:
        text_lower = text.lower()
        return any(kw.lower() in text_lower for kw in keywords)
