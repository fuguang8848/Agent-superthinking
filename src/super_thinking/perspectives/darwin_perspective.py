"""Darwin Perspective - 蒸馏自 alchaincyf/darwin-skill.

Darwin Skill：autonomous skill optimizer inspired by Karpathy's autoresearch.
评估→改进→实测验证→人类确认→保留或回滚→生成成果卡片。
"""

from super_thinking.perspectives._interface import Perspective, PerspectiveOutput


class DarwinPerspective(Perspective):
    """Darwin Skill认知操作系统 - 用8维rubric评估SKILL质量、用自主优化循环改进、用棘轮机制保留改进。"""

    @property
    def id(self) -> str:
        return "darwin_perspective"

    @property
    def name(self) -> str:
        return "Darwin优化视角"

    @property
    def description(self) -> str:
        return "以Darwin Skill为核心的SKILL优化框架：8维rubric评估（结构60分+效果40分）、自主优化循环、棘轮机制（只保留改进）、双重评估（结构+实测）、人在回路。适用于skill质量评估与优化。"

    @property
    def trigger_keywords(self) -> list[str]:
        return [
            "优化skill", "skill评分", "自动优化", "auto optimize",
            "skill质量", "达尔文", "darwin", "skill review",
            "skill打分", "提升skill", "评估skill", "skill评估",
            "帮我改skill", "skill怎么样", "skill优化",
        ]

    def think(self, input_str: str, context: dict) -> PerspectiveOutput:
        input_lower = input_str.lower()
        key_points = []
        warnings = []
        analysis_parts = []

        # === 心智模型1: 8维Rubric评估 ===
        # 结构维度（60分）+ 效果维度（40分），总分100
        if any(k in input_lower for k in [
            "评估", "评分", "打分", "质量", "结构", "效果",
            "rubric", "维度", "怎么样", "好不好",
        ]):
            key_points.append("【8维Rubric】结构维度60分（前置matter/工作流/边界/检查点/具体性/资源）+ 效果维度40分（整体架构/实测表现）")
            analysis_parts.append(
                "【8维Rubric评估（总分100）】\n\n"
                "结构维度（60分）：\n"
                "1. Frontmatter质量（8分）：name规范、description包含做什么+何时用+触发词、≤1024字符\n"
                "2. 工作流清晰度（15分）：步骤明确可执行、有序号、每步有明确输入/输出\n"
                "3. 边界条件覆盖（10分）：处理异常情况、有fallback路径、错误恢复\n"
                "4. 检查点设计（7分）：关键决策前有用户确认、防止自主失控\n"
                "5. 指令具体性（15分）：不模糊、有具体参数/格式/示例、可直接执行\n"
                "6. 资源整合度（5分）：references/scripts/assets引用正确、路径可达\n\n"
                "效果维度（40分）：\n"
                "7. 整体架构（15分）：结构层次清晰、不冗余不遗漏\n"
                "8. 实测表现（25分）：用测试prompt跑一遍，输出质量是否符合skill宣称的能力"
            )

        # === 心智模型2: 自主优化循环 ===
        # 评估→改进→实测验证→人类确认→保留或回滚→下一轮
        if any(k in input_lower for k in [
            "优化", "改进", "改进方案", "改什么", "如何优化",
            "round", "迭代", "循环",
        ]):
            key_points.append("【自主优化循环】诊断最低分维度→提出改进方案→执行→重新评估→决策保留/回滚→进入下一轮")
            analysis_parts.append(
                "【自主优化循环】\n\n"
                "Phase 1 基线评估：\n"
                "对每个skill先做结构评分（主agent）+ 效果评分（子agent独立跑测试prompt）\n\n"
                "Phase 2 优化循环（默认最多3轮）：\n"
                "Step 1 诊断：找出得分最低的维度\n"
                "Step 2 提出改进方案：改什么+为什么改+预期提升多少分\n"
                "Step 3 执行改进：编辑SKILL.md，git add+commit\n"
                "Step 4 重新评估：结构维度主agent重打分，效果维度子agent重跑\n"
                "Step 5 决策：新总分>旧总分→keep；否则→git revert回滚\n"
                "Step 6 日志：results.tsv追加记录\n\n"
                "【检查点】每个skill优化完后展示改动摘要，等用户确认OK再继续。"
            )

        # === 心智模型3: 棘轮机制 ===
        # 只保留有改进的commit，自动回滚退步
        if any(k in input_lower for k in [
            "回滚", "revert", "保留", "棘轮", "git",
            "commit", "版本", "退步",
        ]):
            key_points.append("【棘轮机制】只保留有改进的commit，自动回滚退步——分数必须严格高于改进前才保留")
            analysis_parts.append(
                "【棘轮机制（Ratchet）】\n"
                "借鉴Karpathy autoresearch的核心设计：\n"
                "- 只保留有改进的commit，自动回滚退步\n"
                "- 改进后总分必须严格高于改进前才保留（不靠四舍五入）\n"
                "- 用git revert而非git reset --hard保留历史\n\n"
                "异常处理：\n"
                "- 不在git仓库 → 用文件备份代替revert\n"
                "- results.tsv损坏 → 备份后重建\n"
                "- 分支已存在 → 末尾加 -2/-3"
            )

        # === 心智模型4: 双重评估（结构+实测） ===
        # 结构评分主agent做，效果评分必须用子agent独立跑——不能自己改自己评
        if any(k in input_lower for k in [
            "测试", "prompt", "效果", "实测", "验证",
            "子agent", "对比", "baseline",
        ]):
            key_points.append("【双重评估】效果维度必须用子agent独立跑——不能自己改自己评，避免评分偏差")
            analysis_parts.append(
                "【双重评估】\n"
                "结构评分（主agent）：按维度1-7逐项打分\n"
                "效果评分（子agent）：\n"
                "1. 为每个skill设计2-3个典型用户prompt\n"
                "2. spawn子agent：with_skill执行 vs baseline不带skill执行\n"
                "3. 对比两组输出，从三维度打分：是否完成用户意图？比baseline质量提升明显吗？有skill引入的负面影响吗？\n\n"
                "如果子agent不可用：退化到干跑验证（模拟执行思路判断），但要在results.tsv标注dry_run。"
            )

        # === 心智模型5: 人在回路 ===
        # 每个skill优化完后暂停，用户确认再继续
        if any(k in input_lower for k in [
            "确认", "暂停", "用户", "human", "人工", "检查",
            "决策", "判断",
        ]):
            key_points.append("【人在回路】每个skill优化完后展示改动摘要（git diff+分数变化），等用户确认OK再继续")
            analysis_parts.append(
                "【人在回路（Human in the Loop）】\n"
                "与纯autoresearch的区别：\n"
                "- 不全自主：每个skill优化完后暂停\n"
                "- 展示：git diff（改前vs改后）+ 分数变化 + 测试prompt输出对比\n"
                "- 等用户确认OK才继续下一个skill\n"
                "- 用户说「不好」→ 回滚到该skill优化前版本\n\n"
                "Phase 2.5探索性重写（可选）：当连续2个skill在round 1就break（涨不动）时，提议从头重写——但必须征得用户同意。"
            )

        # === 默认分析 ===
        if not analysis_parts:
            analysis_parts.append(
                f"从Darwin视角分析：{input_str}\n\n"
                "【Darwin第一问】是要评估一个skill的质量，还是要优化它？\n\n"
                "【执行路径】\n"
                "评估 → Phase 1（结构评分+效果评分）→ 展示评分卡 → 用户确认\n"
                "优化 → Phase 1 基线评估 → Phase 2 优化循环（最多3轮/每个skill）→ Phase 3 汇总报告\n\n"
                "【输出格式（汇总报告）】\n"
                "优化skills数、总实验次数、保留改进数、分数变化表、主要改进摘要。"
            )
            key_points.append("【通用】先基线评估（Phase 1），再优化（Phase 2），最后汇总（Phase 3）")

        return PerspectiveOutput(
            perspective_id=self.id,
            perspective_name=self.name,
            analysis="\n\n".join(analysis_parts) if analysis_parts else f"从Darwin视角分析：{input_str}",
            key_points=key_points,
            confidence=0.75,
            tags=[self.id, "skill优化", "评估", "rubric", "autoresearch", "自主实验"],
            warnings=[
                "效果维度必须用子agent独立评分，主agent不能自己改自己评",
                "MAX_ROUNDS默认3轮，达到后需用户决定继续/探索性重写/收工",
                "优化后SKILL.md不应超过原始大小的150%",
            ],
            metadata={
                "source": "https://github.com/alchaincyf/darwin-skill",
                "mental_models_count": 5,
            },
        )

    def _matches(self, text: str, keywords: list[str]) -> bool:
        text_lower = text.lower()
        return any(kw.lower() in text_lower for kw in keywords)
