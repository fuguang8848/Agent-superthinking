"""X-Mentor Perspective - 蒸馏自 alchaincyf/x-mentor-skill.

X/Twitter运营导师的思维操作系统：Hook公式、1/3/1节奏、四段Thread结构、4A选题矩阵、算法利用。
"""

from super_thinking.perspectives._interface import Perspective, PerspectiveOutput


class XmentorPerspective(Perspective):
    """X/Twitter运营导师认知操作系统 - 选题策略、Hook写作、Thread结构、增长引擎、算法利用。"""

    @property
    def id(self) -> str:
        return "xmentor_perspective"

    @property
    def name(self) -> str:
        return "X运营导师视角"

    @property
    def description(self) -> str:
        return "以X/Twitter顶级创作者方法论为核心的运营框架：Hook公式、1/3/1节奏、四段Thread结构、4A选题矩阵、增长阶段策略。适用于内容创作、社交媒体运营、个人IP打造。"

    @property
    def trigger_keywords(self) -> list[str]:
        return [
            "推文", "tweet", "thread", "x运营", "twitter",
            "涨粉", "粉丝", "内容", "选题", "hook",
            "写推文", "发推", "x算法", "thread结构",
            "内容创作", "社交媒体", "个人ip", "内容运营",
        ]

    def think(self, input_str: str, context: dict) -> PerspectiveOutput:
        input_lower = input_str.lower()
        key_points = []
        warnings = []
        analysis_parts = []

        # === 心智模型1: Hook公式 ===
        # 3种核心Hook公式：好奇缺口、可信度锚点、Value Equation
        if any(k in input_lower for k in [
            "hook", "标题", "开头", "吸引", "点击", "第一句",
            "开头怎么写", "推文开头", "thread开头",
        ]):
            key_points.append("【Hook公式】3种核心Hook：好奇缺口 / 可信度锚点 / Value Equation，生成3个版本让用户选")
            analysis_parts.append(
                "【Hook公式】\n"
                "3种核心Hook类型：\n"
                "1. 好奇缺口：提出一个反直觉的事实或问题，让读者产生「为什么」的冲动\n"
                "2. 可信度锚点：用数字、权威背书、具体经历建立信任\n"
                "3. Value Equation：直接告诉读者能获得什么价值\n\n"
                "执行：针对用户需求生成3个不同Hook版本，每个标注用了哪个公式和发帖时间建议，【检查点】让用户选择或修改。"
            )

        # === 心智模型2: 1/3/1节奏 + Thread四段结构 ===
        # Hook→Main→TL;DR→CTA，Thread的标准结构
        if any(k in input_lower for k in [
            "thread", "推文", "正文", "结构", "写作", "怎么写推文",
            "内容", "段落", "结尾", "cta", "call to action",
        ]):
            key_points.append("【1/3/1节奏】短推文控制120-130字符；Thread用四段结构：Hook→Main→TL;DR→CTA")
            analysis_parts.append(
                "【1/3/1节奏 + Thread四段结构】\n"
                "短推文（推文本身，非Thread）：\n"
                "- 控制120-130字符\n"
                "- 1个Hook + 1个核心信息 + 1个行动（视情况）\n\n"
                "Thread四段结构：\n"
                "1. Hook（钩子）：第一句话决定读者是否继续\n"
                "2. Main（主体）：每条推文推进一个子观点，Rate of Revelation要快\n"
                "3. TL;DR（摘要）：用一句话总结核心信息\n"
                "4. CTA（行动召唤）：引导互动或关注\n\n"
                "每条Thread内部遵循1/3/1节奏：开头引发好奇 → 中间给出1-3个核心信息 → 结尾总结或引导。"
            )

        # === 心智模型3: 4A选题矩阵 ===
        # Awareness→Analytical→Argumentative→Action，4个维度生成选题
        if any(k in input_lower for k in [
            "选题", "灵感", "没灵感", "写什么", "主题", "角度",
            "话题", "方向", "内容规划", "素材",
        ]):
            key_points.append("【4A选题矩阵】Awareness→Analytical→Argumentative→Action，每个角度出1-2个选题")
            analysis_parts.append(
                "【4A选题矩阵】\n"
                "4A：\n"
                "1. Awareness（认知型）：让读者意识到一个他们不知道的问题\n"
                "2. Analytical（分析型）：拆解一个现象或趋势背后的原因\n"
                "3. Argumentative（论证型）：提出一个反共识观点并论证\n"
                "4. Action（行动型）：给出具体可操作的建议或步骤\n\n"
                "执行：基于用户的主题桶，每个角度出1-2个选题，标注每个选题的预期效果（拉新/留人/引发讨论），【检查点】用户选择方向后再展开为写作brief。"
            )

        # === 心智模型4: 增长阶段策略 ===
        # 0-1K/1K-10K/10K-100K三个阶段的瓶颈和策略不同
        if any(k in input_lower for k in [
            "涨粉", "增长", "粉丝", "阶段", "瓶颈", "策略",
            "账号", "运营", "推广", "koc", "kol",
            "互动", "er", "engagement",
        ]):
            key_points.append("【增长阶段策略】先确认粉丝量阶段：0-1K/1K-10K/10K-100K，瓶颈和策略不同")
            analysis_parts.append(
                "【增长阶段策略】\n"
                "三阶段诊断：\n"
                "0-1K（冷启动）：内容即产品，聚焦单一主题桶，建立标签认知\n"
                "1K-10K（建立势能）：找到高互动内容类型，测试不同Hook，优化发布频率\n"
                "10K-100K（规模化）：内容多元化，建立内容系列，增加评论区互动\n\n"
                "执行：先确认用户当前粉丝量和是否有Premium，再诊断瓶颈。\n"
                "如果用户说「涨粉变慢」→ 先用诊断框架排查：算法层→内容层→受众层。"
            )

        # === 心智模型5: 算法利用 ===
        # X算法权重：互动率>粉丝数，内容类型权重因阶段而异
        if any(k in input_lower for k in [
            "算法", "推荐", "流量", "曝光", "x算法", "算法规则",
            "热门", "trending", "virality", "传播",
        ]):
            key_points.append("【算法利用】X算法核心权重：互动率>粉丝数，外链降低分发，外链建议放第一条回复")
            analysis_parts.append(
                "【算法利用】\n"
                "X算法核心原则：\n"
                "- 互动率（点赞/回复/转推/收藏）比粉丝数更重要\n"
                "- 外链会降低初始分发——如果需要链接，建议放在第一条推文的回复中\n"
                "- 发布后的前30-60分钟互动决定是否进入更大流量池\n"
                "- hashtag控制在1-2个，多了降低权重\n"
                "- Media（图片/视频）能显著提高互动率\n\n"
                "AI/科技赛道特殊性：响应热点（超级碗等活动）可获得算法额外加权。"
            )

        # === 默认分析 ===
        if not analysis_parts:
            analysis_parts.append(
                f"从X运营导师视角分析：{input_str}\n\n"
                "【X导师第一问】短推文还是Thread？目标受众是谁？英文还是中文？\n"
                "（默认值：短推文、中文、AI/tech从业者）\n\n"
                "【核心问题】\n"
                "1. 写什么？（选题问题→4A矩阵）\n"
                "2. 怎么开头？（Hook问题→3种Hook公式）\n"
                "3. 结构怎么安排？（Thread结构→1/3/1节奏+四段式）\n"
                "4. 怎么涨粉？（增长问题→阶段诊断）"
            )
            key_points.append("【通用】先确认内容类型和受众，再进入对应场景")

        return PerspectiveOutput(
            perspective_id=self.id,
            perspective_name=self.name,
            analysis="\n\n".join(analysis_parts) if analysis_parts else f"从X运营导师视角分析：{input_str}",
            key_points=key_points,
            confidence=0.75,
            tags=[self.id, "X运营", "内容创作", "选题", "Hook", "增长"],
            warnings=[
                "算法数据基于2026年4月前，X平台算法可能已有变化",
                "方法论来自英文市场创作者，中文在X上的传播规律可能不同",
                "幸存者偏差：方法论来自已成功者，看不到失败案例",
            ],
            metadata={
                "source": "https://github.com/alchaincyf/x-mentor-skill",
                "mental_models_count": 5,
            },
        )

    def _matches(self, text: str, keywords: list[str]) -> bool:
        text_lower = text.lower()
        return any(kw.lower() in text_lower for kw in keywords)
