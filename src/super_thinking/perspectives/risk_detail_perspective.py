"""Risk Detail Perspective - 蒸馏自 alchaincyf/taleb-skill (Nassim Nicholas Taleb)"""

from super_thinking.perspectives._interface import Perspective, PerspectiveOutput


class RiskDetailPerspective(Perspective):
    """
    塔勒布风险思维框架：非对称风险、反脆弱、黑天鹅识别。

    核心心智模型：
    1. 非对称风险思维 - 永远先看下行风险代价
    2. 反脆弱偏好 - 从混乱中获益
    3. Skin in the Game 检验 - 没下注的观点打五折
    4. 林迪效应 - 存在越久越可能继续存在
    5. Via Negativa - 减法优先
    6. 领域特异性 - 能力和理性都是领域特定的

    蒸馏来源：alchaincyf/taleb-skill (40+来源深度调研)
    触发词：黑天鹅、尾部风险、反脆弱、skin in the game、杠铃策略、不确定、风险评估
    """

    @property
    def id(self) -> str:
        return "risk_detail"

    @property
    def name(self) -> str:
        return "塔勒布风险视角"

    @property
    def description(self) -> str:
        return (
            "塔勒布风险思维：非对称风险优先（永远先看下行代价）、反脆弱设计（从混乱获益而非抵抗混乱）、"
            "Skin in the Game检验（没下注的观点可信度打五折）、林迪效应（久经时间筛选的才可信）、"
            "Via Negativa减法优先（去掉有害的>增加好的）。识别黑天鹅、评估尾部风险、设计反脆弱策略。"
        )

    @property
    def trigger_keywords(self) -> list[str]:
        return [
            "黑天鹅", "尾部风险", "反脆弱", "skin in the game", "杠铃策略",
            "林迪效应", "不确定", "风险评估", "最坏情况", "脆弱", "鲁棒",
            "不对称", "波动", "压力测试", "脆弱性", "barbell", "antifragile",
            "尾部", "via negativa", "skin_in_the_game",
        ]

    def think(self, input_str: str, context: dict) -> PerspectiveOutput:
        input_lower = input_str.lower()
        key_points = []
        warnings = []
        analysis_parts = []

        # ─── 模型1: 非对称风险思维 ───
        if any(kw in input_lower for kw in ["风险", "投资", "决策", "选择", "策略", "计划", "概率"]):
            key_points.append("【非对称风险】永远先问：最坏能坏到什么程度？我能承受吗？")
            analysis_parts.append(
                "非对称风险思维：不问「最可能发生什么」，问「下行风险多大、上行空间多大」。"
                "如果下行是毁灭性的（破产/死亡/不可逆损失），概率再小也不能忽视。"
                "期望值思维在极端斯坦（一个事件能主宰一切的地方）里是危险的。"
            )
            warnings.append("警惕期望值陷阱：平均斯坦里期望值有效，极端斯坦里必须先看不对称性")

        # ─── 模型2: 反脆弱偏好 ───
        if any(kw in input_lower for kw in ["系统", "组织", "策略", "适应", "压力", "混乱", "变化", "韧性"]):
            key_points.append("【反脆弱】压力/波动增加时，系统变好还是变差？")
            analysis_parts.append(
                "反脆弱三层级：脆弱（被波动伤害）→ 鲁棒（不受影响）→ 反脆弱（从波动中获益）。"
                "最优策略不是追求稳定，而是让自己处于反脆弱位置。"
                "杠铃策略：90%极度保守 + 10%极度冒险。中间地带最危险。"
            )

        # ─── 模型3: Skin in the Game 检验 ───
        if any(kw in input_lower for kw in ["专家", "建议", "观点", "政策", "计划", "分析", "顾问"]):
            key_points.append("【Skin in the Game】说这话的人是否为此下注？后果是什么？")
            analysis_parts.append(
                "观点可信度 = 该观点承担真实后果。没有skin in the game的人（顾问/学者/政策制定者）"
                "天然倾向于制造脆弱性，因为他们与反馈回路隔绝。"
                "听到任何建议立刻问：说这话的人是否下注？如果后果为零→观点打五折。"
            )
            warnings.append("记者、顾问、学者、政策制定者天然缺乏skin in the game，观点需打折")

        # ─── 模型4: 林迪效应 ───
        if any(kw in input_lower for kw in ["新", "创新", "技术", "方法", "现代", "古老", "传统"]):
            key_points.append("【林迪效应】这东西存在多久了？千年实践 vs 新兴方法")
            analysis_parts.append(
                "非易腐事物（书籍/技术/宗教/食物）预期寿命随已存在时间增长。"
                "存在千年的实践包含时间筛选过的智慧。新技术/新方法需证明自己比旧的好。"
                "「古老智慧」不是万能，但比「新奇特」有更长的压力测试历史。"
            )

        # ─── 模型5: Via Negativa 减法优先 ───
        if any(kw in input_lower for kw in ["改进", "优化", "提升", "治疗", "改变", "增加", "减少"]):
            key_points.append("【减法优先】改进往往来自去除有害的，而非增加更多的")
            analysis_parts.append(
                "Via Negativa核心：iatrogenics（干预本身造成的伤害）。"
                "在复杂系统中，添加新东西的风险通常大于移除有害东西的收益。"
                "健康：停止吃有害的 > 增加超级食物。投资：避免亏损 > 追求收益。"
            )

        # ─── 模型6: 领域特异性 ───
        if any(kw in input_lower for kw in ["理性", "智慧", "判断", "决策者", "专家", "成功"]):
            key_points.append("【领域特异性】能力和理性都是领域特定的，不能跨域迁移")
            analysis_parts.append(
                "同一个人在一个领域极其理性，在另一个领域可以极其愚蠢。"
                "不要因为一个人在A领域成功就信任他在B领域的判断。"
                "政治立场可以在不同尺度上完全不同——「国家层面自由主义者，家庭层面社会主义者」。"
            )

        # ─── 黑天鹅专项 ───
        if any(kw in input_lower for kw in ["黑天鹅", "极端", "罕见", "不可能发生", "从来没发生过"]):
            key_points.append("【黑天鹅警告】从未发生≠不会发生。极端事件在极端斯坦里是常态。")
            analysis_parts.append(
                "黑天鹅三个特征：稀有性、极端影响、事后可解释（事前不可预测）。"
                "在金融/社会/政治领域，极端斯坦主宰一切——一个事件可以改变历史分布。"
                "不要基于「过去从未发生」来判断未来可能性。COVID就是典型的黑天鹅。"
            )
            warnings.append("黑天鹅无法预测，只能识别脆弱性并设计反脆弱结构")

        # ─── 通用风险评估 ───
        if any(kw in input_lower for kw in ["风险", "最坏", "万一", "失败", "不确定"]):
            if not any(kw in input_lower for kw in ["黑天鹅", "极端", "尾部"]):
                key_points.append("【通用风险】列出3个最大威胁 + 1个极端尾部风险")

        if not key_points:
            key_points.append("【风险扫描】此议题暂未触发塔勒布核心模型，尝试提及：风险/黑天鹅/反脆弱/专家建议")

        return PerspectiveOutput(
            perspective_id=self.id,
            perspective_name=self.name,
            analysis="\n\n".join(analysis_parts) if analysis_parts else "从塔勒布风险视角分析...",
            key_points=key_points,
            confidence=0.8,
            tags=["风险", "塔勒布", "反脆弱", "黑天鹅", "不对称风险"],
            warnings=warnings,
            metadata={
                "source": "https://github.com/alchaincyf/taleb-skill",
                "mental_models": [
                    "非对称风险思维",
                    "反脆弱偏好",
                    "Skin in the Game检验",
                    "林迪效应",
                    "Via Negativa",
                    "领域特异性"
                ],
                "perspective_type": "risk_analysis"
            },
        )
