"""Steve Jobs Perspective - 蒸馏自 alchaincyf/steve-jobs-skill.

乔布斯的思维操作系统：聚焦即说不、端到端控制、连点成线、死亡过滤器、现实扭曲力场、技术人文交汇。
"""

from super_thinking.perspectives._interface import Perspective, PerspectiveOutput


class JobsPerspective(Perspective):
    """乔布斯认知操作系统 - 用减法思维审视产品、用端到端控制评估整合、用死亡过滤器做人生决策。"""

    @property
    def id(self) -> str:
        return "jobs_perspective"

    @property
    def name(self) -> str:
        return "乔布斯视角"

    @property
    def description(self) -> str:
        return "以乔布斯产品哲学为核心的思维框架：聚焦即说不、端到端控制、连点成线、死亡过滤器、现实扭曲力场、技术与人文交汇。"

    @property
    def trigger_keywords(self) -> list[str]:
        return [
            "乔布斯", "jobs", "steve", "产品", "设计", "体验",
            "简洁", "聚焦", "减法", "删除", "砍掉",
            "端到端", "一体化", "乔布斯会怎么看", "乔布斯视角",
            "这个产品", "产品设计", "功能", "创新",
        ]

    def think(self, input_str: str, context: dict) -> PerspectiveOutput:
        input_lower = input_str.lower()
        key_points = []
        warnings = []
        analysis_parts = []

        # === 心智模型1: 聚焦即说不 ===
        # 聚焦不是对要专注的事说Yes，而是对其他一百个好主意说No。
        if any(k in input_lower for k in [
            "聚焦", "专注", "优先级", "功能", "产品线", "做什么",
            "选择", "删", "砍", "简化", "减法", "要不要加",
        ]):
            key_points.append("【聚焦即说不】先问：该砍掉什么？350个产品减到10个才是正确的减法")
            analysis_parts.append(
                "【聚焦即说不】\n"
                "乔布斯：「人们以为聚焦意味着对要专注的事说Yes。但根本不是这样。\n"
                "聚焦意味着对其他一百个好主意说No。」\n"
                "1997年回归Apple后，从350个产品减到10个——2×2矩阵（消费者/专业 × 台式/笔记本）。\n"
                "面对任何产品或战略决策，先问：「能砍掉什么？」"
            )

        # === 心智模型2: 端到端控制 ===
        # 真正认真对待软件的人，应该自己做硬件。
        if any(k in input_lower for k in [
            "端到端", "一体化", "整合", "控制", "生态", "闭环",
            "外包", "合作", "平台", "控制体验", "软硬件",
        ]):
            key_points.append("【端到端控制】控制整个体验链条的能力，决定了你能做出多好的产品")
            analysis_parts.append(
                "【端到端控制（The Whole Widget）】\n"
                "引用Alan Kay：「真正认真对待软件的人，应该自己做硬件。」\n"
                "乔布斯：「我们是唯一控制整个产品的公司——硬件、软件、操作系统。\n"
                "我们能对用户体验负全责。」\n"
                "评估产品策略时：关键环节在谁手上？如果交给别人，你能保证最终体验吗？"
            )

        # === 心智模型3: 连点成线 ===
        # 人生无法前瞻规划，只能回溯理解。信任直觉。
        if any(k in input_lower for k in [
            "人生", "选择", "规划", "职业", "方向", "热爱",
            "转型", "转行", "当初", "后悔", "弯路", "意义",
        ]):
            key_points.append("【连点成线】人生无法前瞻规划，只能回溯理解。信任直觉，跟随好奇心")
            analysis_parts.append(
                "【连点成线】\n"
                "乔布斯斯坦福演讲：「你无法向前看连接这些点；你只能回头看把它们连起来。\n"
                "所以你必须信任这些点会在你的未来以某种方式连接。」\n"
                "书法课→Mac字体；被Apple开除→NeXT→Mac OS X。\n"
                "当你被要求证明「这有什么用」「ROI是什么」时：有些最重要的投资，在当下看起来毫无关联。"
            )

        # === 心智模型4: 死亡过滤器 ===
        # 如果今天是你生命最后一天，你还会做今天要做的事吗？
        if any(k in input_lower for k in [
            "生死", "最后一天", "死亡", "要不要做", "该不该",
            "犹豫", "纠结", "重大决策", "人生选择", "辞职",
            "妥协", "要不要坚持",
        ]):
            key_points.append("【死亡过滤器】如果今天是最后一天，还做这件事吗？连续No说明需要改变")
            analysis_parts.append(
                "【死亡过滤器】\n"
                "乔布斯17岁起每天早上对镜子问自己这个问题。\n"
                "「如果你是为了别人而活，那就跟死了没什么区别。」\n"
                "用死亡做过滤：你害怕的东西、别人的期望、尴尬、失败——在「你会死」面前，全都不重要。\n"
                "注意：这个工具对大决策有用，对日常小决策容易过度戏剧化。"
            )

        # === 心智模型5: 现实扭曲力场 ===
        # 通过让人相信不可能的目标，让它变成可能。
        if any(k in input_lower for k in [
            "不可能", "做不到", "团队", "管理", "激励", "push",
            "deadline", "期限", "目标", "鼓舞", "激励团队",
        ]):
            key_points.append("【现实扭曲力场】推团队突破自我认知限制，但也注意代价")
            analysis_parts.append(
                "【现实扭曲力场】\n"
                "Bud Tribble引用Star Trek描述乔布斯：「在他面前，现实是可以重塑的。」\n"
                "Andy Hertzfeld：「他能够用魅力、魄力、夸张和执着的混合体，说服自己和周围的人相信几乎任何事情。」\n"
                "Mac团队在「不可能的」期限内交付了产品。\n"
                "代价：我用它push团队做出了不可思议的产品，但也让一些人崩溃了。这是张力，不是Bug。"
            )

        # === 心智模型6: 技术与人文的交汇 ===
        if any(k in input_lower for k in [
            "技术", "人文", "美", "体验", "用户", "产品", "设计",
            "创新", "革命", "创意",
        ]):
            key_points.append("【技术×人文】仅有技术不够，技术必须与自由艺术结合才能让人心灵歌唱")
            analysis_parts.append(
                "【技术与人文的交汇】\n"
                "乔布斯iPad 2发布会：「技术本身是不够的。\n"
                "技术必须与自由艺术、人文科学结合，才能产生让人心灵歌唱的结果。」\n"
                "受Edwin Land（Polaroid创始人）启发。\n"
                "评估产品/团队/创业方向时问：这里面有人文关怀吗？这个东西除了功能正确，还能让人感受到美吗？"
            )

        # === 默认分析 ===
        if not analysis_parts:
            analysis_parts.append(
                f"从乔布斯视角分析：{input_str}\n\n"
                "【乔布斯第一问】这东西是amazing还是shit？\n"
                "乔布斯不用「还行」「不错」「有待改进」——只有两档判断。\n\n"
                "【核心问题】\n"
                "1. 该砍掉什么？（聚焦即说不）\n"
                "2. 关键体验在谁的控制之下？（端到端）\n"
                "3. 这是一件追随好奇心的「书法课」吗？（连点成线）\n"
                "4. 如果今天是最后一天，还做这件事吗？（死亡过滤器）"
            )
            key_points.append("【通用】先给amazing/shit二元判断，再问该砍什么")

        return PerspectiveOutput(
            perspective_id=self.id,
            perspective_name=self.name,
            analysis="\n\n".join(analysis_parts) if analysis_parts else f"从乔布斯视角分析：{input_str}",
            key_points=key_points,
            confidence=0.75,
            tags=[self.id, "产品哲学", "聚焦", "减法", "用户体验", "端到端控制"],
            warnings=[
                "乔布斯框架最适合产品设计和战略聚焦，对需要制度性协调的社会问题效果弱",
                "Jobs已于2011年去世，对2011年后技术发展无公开表态，任何推断都是推测",
            ],
            metadata={
                "source": "https://github.com/alchaincyf/steve-jobs-skill",
                "mental_models_count": 6,
            },
        )

    def _matches(self, text: str, keywords: list[str]) -> bool:
        text_lower = text.lower()
        return any(kw.lower() in text_lower for kw in keywords)
