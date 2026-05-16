"""
NuwaMetaPerspective - 元视角生成器

女娲不是普通视角，而是视角生成器。她的职责是：
1. 分析用户问题，判断现有视角是否足够覆盖
2. 如果不够，动态生成新的 perspective 模块
3. 自动注册新生成的视角到 registry

女娲方法论（来自 huashu-nuwa skill）：
- Phase 0: 入口分流（直接路径 vs 模糊路径）
- Phase 1: 需求诊断（判断需要什么类型的视角）
- Phase 2: 视角推荐（现有视角组合 vs 生成新视角）
- Phase 3: 新视角生成（如需要）
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from super_thinking.perspectives._interface import Perspective, PerspectiveOutput


# ===== 视角类型元数据 =====

@dataclass
class PerspectiveType:
    """视角类型定义。"""
    id: str
    name: str
    description: str
    trigger_keywords: list[str]
    example_questions: list[str]
    compatible_with: list[str]  # 与哪些其他视角兼容


# 类型ID → 实际 perspective ID 的映射（处理命名不一致的情况）
TYPE_TO_PERSPECTIVE_ID = {
    "decision": "magi_debate",         # 决策类用 magi_debate
    "risk": "magi_debate",              # 风险分析用 magi_debate
    "emotion": "magi_debate",           # 情感类用 magi_debate
    "debate": "magi_debate",            # 辩论类用 magi_debate
    "meta": "meta_thinking",            # 元认知用 meta_thinking
    "verification": "verification",     # 证伪核查
    "tagmemo": "tagmemo_perspective",  # TagMemo浪潮检索
    "msa": "msa_perspective",          # MSA双重路由检索
    "vcp": "vcp_perspective",          # VCP系统集成
    # 已有实现的标准类型
    "mao": "mao_perspective",           # 毛泽东视角
    "business": "business_perspective",  # 商业视角（待实现）
    "creativity": "creativity_perspective",  # 创造力视角（待实现）
}


# 内置视角类型注册表
PERSPECTIVE_TYPES = [
    PerspectiveType(
        id="decision",
        name="决策分析视角",
        description="用于分析决策选项、风险收益比、权衡取舍",
        trigger_keywords=["决策", "选择", "应该", "要不要", "利弊", "风险", "回报", "决定", "option", "choice"],
        example_questions=["我应该接受这个offer吗", "要不要转行"],
        compatible_with=["risk", "emotion", "verification"],
    ),
    PerspectiveType(
        id="risk",
        name="风险分析视角",
        description="评估不确定性、尾部风险、黑天鹅事件",
        trigger_keywords=["风险", "不确定", "黑天鹅", "最坏情况", "保险", "风险管理", "尾部"],
        example_questions=["这个投资有哪些风险"],
        compatible_with=["decision", "verification"],
    ),
    PerspectiveType(
        id="emotion",
        name="情感心理视角",
        description="关注情绪、动机、心理偏差、认知陷阱",
        trigger_keywords=["情绪", "心理", "焦虑", "害怕", "动机", "偏见", "认知", "感受"],
        example_questions=["为什么我总是拖延", "怎么克服焦虑"],
        compatible_with=["decision", "mao"],
    ),
    PerspectiveType(
        id="mao",
        name="毛泽东视角",
        description="阶级分析、群众路线、矛盾论、实事求是",
        trigger_keywords=["革命", "斗争", "人民", "群众", "阶级", "矛盾", "实事求是", "独立自主", "持久战", "农村包围城市", "统一战线", "群众路线", "纸老虎", "毛选"],
        example_questions=["如何发动群众", "怎么处理人民内部矛盾", "面对强敌应该怎么办"],
        compatible_with=["emotion", "meta", "vcp"],
    ),
    PerspectiveType(
        id="debate",
        name="辩论视角",
        description="正反方论证、逻辑谬误、论证结构",
        trigger_keywords=["辩论", "论证", "支持", "反对", "正方", "反方", "逻辑", "谬误", "权衡", "利弊"],
        example_questions=["支持还是反对这个观点", "这个论证有什么问题", "如何权衡这个选择"],
        compatible_with=["meta", "decision"],
    ),
    PerspectiveType(
        id="meta",
        name="元认知视角",
        description="思考你的思考、分析框架本身、递归反思、逻辑结构",
        trigger_keywords=["分析", "思考", "逻辑", "框架", "方法", "认知", "元", "本质", "反思", "推理", "思维链"],
        example_questions=["这个分析方法有什么局限", "还有什么思考框架", "想想看为什么"],
        compatible_with=["debate", "vcp", "verification"],
    ),
    PerspectiveType(
        id="business",
        name="商业分析视角",
        description="商业模式、竞争格局、产品市场契合",
        trigger_keywords=["商业", "创业", "产品", "市场", "盈利", "竞争", "PMF", "增长"],
        example_questions=["这个商业模式可行吗", "如何找到PMF"],
        compatible_with=["decision", "risk", "vcp"],
    ),
    PerspectiveType(
        id="creativity",
        name="创造力视角",
        description="打破常规、类比思维、第一性原理",
        trigger_keywords=["创意", "创新", "突破", "第一性原理", "类比", "跨界", "灵感"],
        example_questions=["怎么想出创新的解决方案", "有什么突破性思路"],
        compatible_with=["meta", "business"],
    ),
    PerspectiveType(
        id="verification",
        name="证伪核查视角",
        description="证据优先原则，在声称完成/修复/通过之前，必须运行验证命令并确认输出",
        trigger_keywords=["验证", "确认", "证据", "完成", "测试", "通过", "修复", "bug", "核查", "检查", "质量门禁", "是否完成", "能否交付", "检验"],
        example_questions=["这个bug修好了吗", "测试通过了吗", "能交付了吗"],
        compatible_with=["meta", "decision"],
    ),
    PerspectiveType(
        id="tagmemo",
        name="TagMemo浪潮检索视角",
        description="四阶段RAG：感应（净化+EPA）、分段（语义断层）、扩张（标签+关联）、重塑（向量融合+霰弹枪检索）",
        trigger_keywords=["深度记忆", "关联", "检索", "浪潮", "语义引力", "记忆检索", "回忆", "相关内容", "知识检索", "关联记忆", "上下文"],
        example_questions=["搜索我之前的记忆", "查找相关内容", "我记得之前做过"],
        compatible_with=["msa", "vcp", "meta"],
    ),
    PerspectiveType(
        id="msa",
        name="MSA双重路由检索视角",
        description="主题级粗筛+词元级精筛，记忆交错最多3轮迭代，从L1-L4分层存储中检索",
        trigger_keywords=["记忆", "检索", "回忆", "msa", "双重路由", "迭代检索", "相关记忆", "上下文", "搜索记忆", "记得", "以前", "上次"],
        example_questions=["上次我们讨论了什么", "这个和我之前做过的项目有什么关系"],
        compatible_with=["tagmemo", "vcp"],
    ),
    PerspectiveType(
        id="vcp",
        name="VCP系统集成视角",
        description="整合TagMemo浪潮RAG、元思考系统、Magi三贤者辩论，输出VCP协议格式的综合分析",
        trigger_keywords=["vcp", "VCP", "系统集成", "综合分析", "整合", "协作", "分布式", "插件", "协议"],
        example_questions=["用VCP系统分析这个问题", "整合所有视角分析"],
        compatible_with=["meta", "debate", "mao", "tagmemo", "msa"],
    ),
]


# ===== 视角生成器 =====

@dataclass
class GeneratedPerspectiveSpec:
    """新视角生成规格。"""
    type_id: str
    name: str
    description: str
    trigger_keywords: list[str]
    core_questions: list[str]  # 这个视角最擅长回答的问题
    methodology: str  # 生成时的方法论描述


class PerspectiveGenerator:
    """根据需求动态生成新视角。"""

    def __init__(self):
        self._generated_classes: dict[str, type] = {}

    def generate(self, spec: GeneratedPerspectiveSpec) -> type:
        """
        根据规格生成新的 Perspective 类。

        Args:
            spec: 视角生成规格

        Returns:
            新生成的 Perspective 类（未实例化）
        """
        type_metadata = next((t for t in PERSPECTIVE_TYPES if t.id == spec.type_id), None)

        # 动态创建类
        class_name = f"Generated{spec.name.title().replace(' ', '')}Perspective"

        # 生成核心分析方法
        analysis_template = self._generate_analysis_template(spec, type_metadata)

        # 生成类定义
        GeneratedClass = type(
            class_name,
            (),
            {
                "id": f"generated_{spec.type_id}",
                "name": spec.name,
                "description": spec.description,
                "trigger_keywords": spec.trigger_keywords,
                "think": lambda self, input_str, context: self._think_impl(input_str, context, spec, analysis_template),
                "_spec": spec,
                "_analysis_template": analysis_template,
            },
        )

        # 添加实例方法
        def _think_impl(self, input_str: str, context: dict, spec: GeneratedPerspectiveSpec, template: str) -> PerspectiveOutput:
            """实际的 think 方法实现。"""
            input_lower = input_str.lower()

            # 分析输入
            key_points = []
            confidence = 0.6

            # 根据类型添加特定分析
            if spec.type_id == "decision":
                key_points = self._analyze_decision(input_str)
            elif spec.type_id == "risk":
                key_points = self._analyze_risk(input_str)
            elif spec.type_id == "emotion":
                key_points = self._analyze_emotion(input_str)
            elif spec.type_id == "business":
                key_points = self._analyze_business(input_str)
            elif spec.type_id == "creativity":
                key_points = self._analyze_creativity(input_str)
            else:
                key_points = [f"从【{spec.name}】视角分析：{input_str[:50]}..."]

            return PerspectiveOutput(
                perspective_id=self.id,
                perspective_name=self.name,
                analysis=template.format(question=input_str, perspective=spec.name),
                key_points=key_points,
                confidence=confidence,
                tags=[spec.type_id, "generated"],
                warnings=[f"自动生成的视角 [{spec.name}]，建议验证分析质量"],
                metadata={"generated": True, "spec_type": spec.type_id},
            )

        # Bind方法
        GeneratedClass._think_impl = _think_impl
        GeneratedClass.think = lambda self, input_str, context: self._think_impl(input_str, context, spec, analysis_template)

        self._generated_classes[spec.type_id] = GeneratedClass
        return GeneratedClass

    def _generate_analysis_template(self, spec: GeneratedPerspectiveSpec, type_metadata: Optional[PerspectiveType]) -> str:
        """生成分析模板。"""
        base = f"""【{spec.name}视角分析】

问题：{{question}}

分析框架：
- 核心问题识别
- 关键变量分析
- 权衡取舍评估

视角特色：
{spec.description}

方法论：{spec.methodology}

建议关注：
"""
        for q in spec.core_questions[:3]:
            base += f"- {q}\n"
        return base

    def _analyze_decision(self, input_str: str) -> list[str]:
        """决策分析视角的专用分析。"""
        return [
            "识别决策的核心变量",
            "列出所有可行选项",
            "评估每个选项的期望值",
            "考虑最坏情况的容错边界",
        ]

    def _analyze_risk(self, input_str: str) -> list[str]:
        """风险分析视角的专用分析。"""
        return [
            "识别潜在威胁来源",
            "评估每个威胁的概率和影响",
            "检查尾部风险（黑天鹅）",
            "建议风险缓解策略",
        ]

    def _analyze_emotion(self, input_str: str) -> list[str]:
        """情感心理视角的专用分析。"""
        return [
            "识别当前情绪状态",
            "检查可能的认知偏差",
            "追溯情绪背后的核心需求",
            "建议认知重构方向",
        ]

    def _analyze_business(self, input_str: str) -> list[str]:
        """商业分析视角的专用分析。"""
        return [
            "定义目标用户和需求",
            "分析竞争格局和壁垒",
            "验证商业模式可行性",
            "评估单位经济模型",
        ]

    def _analyze_creativity(self, input_str: str) -> list[str]:
        """创造力视角的专用分析。"""
        return [
            "打破现有假设和边界",
            "寻找跨领域的类比",
            "用第一性原理追问",
            "构建突破性假设",
        ]


# ===== Nuwa 元视角 =====

class NuwaMetaPerspective(Perspective):
    """
    女娲元视角 - 视角的视角生成器。

    女娲不直接分析问题，而是：
    1. 诊断用户需要什么类型的视角
    2. 检查现有视角的覆盖情况
    3. 推荐最优视角组合
    4. 如需要，动态生成新视角
    """

    @property
    def id(self) -> str:
        return "nuwa_meta"

    @property
    def name(self) -> str:
        return "女娲元视角"

    @property
    def description(self) -> str:
        return "视角生成器：诊断需求，评估现有视角，必要时动态生成新视角"

    @property
    def trigger_keywords(self) -> list[str]:
        return [
            "创造", "生成", "设计", "构思", "新视角", "新思维",
            "没有合适的", "没有能用的", "还有别的吗",
            "这个情况用什么视角", "从XX角度分析",
        ]

    def __init__(self):
        super().__init__()
        self.generator = PerspectiveGenerator()
        self.perspective_types = PERSPECTIVE_TYPES

    def think(self, input: str, context: dict) -> PerspectiveOutput:
        """
        分析用户需求，评估视角覆盖，推荐/生成解决方案。
        """
        input_lower = input.lower()

        # Phase 1: 需求诊断
        needed_types = self._diagnose_needs(input_lower)

        # Phase 2: 检查现有视角覆盖
        existing_coverage = self._check_existing_coverage(context)

        # Phase 3: 生成推荐
        recommendation = self._generate_recommendation(
            needed_types, existing_coverage, input
        )

        # 构建输出
        return self._build_output(input, needed_types, existing_coverage, recommendation)

    def _diagnose_needs(self, input_lower: str) -> list[PerspectiveType]:
        """
        Phase 1: 诊断用户需要什么类型的视角。

        遵循女娲的需求维度表。
        """
        matched_types: list[tuple[PerspectiveType, int]] = []

        for ptype in self.perspective_types:
            score = 0
            for kw in ptype.trigger_keywords:
                if kw.lower() in input_lower:
                    score += 1

            # 也检查示例问题
            for eq in ptype.example_questions:
                if any(w in input_lower for w in eq.lower().split()):
                    score += 0.5

            if score > 0:
                matched_types.append((ptype, score))

        # 排序并返回top匹配
        matched_types.sort(key=lambda x: x[1], reverse=True)

        if not matched_types:
            # 默认返回通用分析视角
            return [next(p for p in self.perspective_types if p.id == "meta")]

        return [pt for pt, _ in matched_types[:3]]

    def _check_existing_coverage(self, context: dict) -> dict[str, bool]:
        """
        Phase 2: 检查现有视角的覆盖情况。
        """
        coverage = {}

        # 从 context 获取已注册的视角
        registry = context.get("registry")
        if registry is None:
            try:
                from super_thinking.core.registry import get_registry
                registry = get_registry()
            except Exception:
                registry = None

        for ptype in self.perspective_types:
            # 使用映射表获取实际的 perspective ID（处理命名不一致）
            perspective_id = TYPE_TO_PERSPECTIVE_ID.get(ptype.id, f"{ptype.id}_perspective")
            has_perspective = False

            if registry:
                existing = registry.get(perspective_id)
                has_perspective = existing is not None

            coverage[ptype.id] = has_perspective

        return coverage

    def _generate_recommendation(
        self,
        needed_types: list[PerspectiveType],
        coverage: dict[str, bool],
        input_str: str,
    ) -> dict:
        """
        Phase 3: 生成推荐组合或新视角生成计划。
        """
        recommendation = {
            "existing_recommended": [],  # 现有可用的视角组合
            "new_perspectives_needed": [],  # 需要新生成的视角
            "confidence": 0.7,
            "reasoning": "",
        }

        # 找出已覆盖且被需要的
        for ntype in needed_types:
            if coverage.get(ntype.id, False):
                recommendation["existing_recommended"].append(ntype.name)

        # 找出未覆盖但被需要的
        for ntype in needed_types:
            if not coverage.get(ntype.id, False):
                recommendation["new_perspectives_needed"].append(ntype)

        # 生成新视角（如果需要）
        if recommendation["new_perspectives_needed"]:
            recommendation["confidence"] = 0.5  # 生成的有不确定性
            recommendation["reasoning"] = (
                f"现有视角未覆盖需求，建议生成: "
                f"{', '.join(t.name for t in recommendation['new_perspectives_needed'])}"
            )
        else:
            recommendation["reasoning"] = (
                f"现有视角已覆盖需求，推荐组合: "
                f"{', '.join(recommendation['existing_recommended'])}"
            )

        return recommendation

    def _build_output(
        self,
        input_str: str,
        needed_types: list[PerspectiveType],
        coverage: dict[str, bool],
        recommendation: dict,
    ) -> PerspectiveOutput:
        """构建女娲的分析输出。"""

        # 生成分析文本
        analysis_parts = [
            "## 🏺 女娲视角诊断报告",
            "",
            f"**问题**: {input_str}",
            "",
            "---",
            "",
            "### Phase 1: 需求诊断",
            "",
            f"根据问题分析，检测到以下需求类型：",
        ]

        for i, ntype in enumerate(needed_types, 1):
            analysis_parts.append(f"{i}. **[{ntype.name}]** - {ntype.description}")
            analysis_parts.append(f"   触发关键词匹配: {', '.join(ntype.trigger_keywords[:5])}")

        analysis_parts.extend([
            "",
            "---",
            "",
            "### Phase 2: 现有视角覆盖检查",
            "",
        ])

        # 覆盖情况
        covered = []
        uncovered = []
        for ntype in needed_types:
            if coverage.get(ntype.id, False):
                covered.append(ntype.name)
            else:
                uncovered.append(ntype.name)

        if covered:
            analysis_parts.append("✅ **已有视角可用**：")
            for name in covered:
                analysis_parts.append(f"   - {name}")
            analysis_parts.append("")

        if uncovered:
            analysis_parts.append("⚠️ **视角缺失（建议生成）**：")
            for name in uncovered:
                analysis_parts.append(f"   - {name}")
            analysis_parts.append("")

        analysis_parts.extend([
            "---",
            "",
            "### Phase 3: 视角推荐与生成",
            "",
            f"**女娲判断**: {recommendation['reasoning']}",
            "",
        ])

        # 推荐组合
        if recommendation["existing_recommended"]:
            analysis_parts.append("**推荐视角组合**：")
            for name in recommendation["existing_recommended"]:
                analysis_parts.append(f"  → **{name}**")
            analysis_parts.append("")

        # 新视角生成
        if recommendation["new_perspectives_needed"]:
            analysis_parts.append("**🔧 准备生成新视角**：")
            for ntype in recommendation["new_perspectives_needed"]:
                # 生成新视角
                spec = GeneratedPerspectiveSpec(
                    type_id=ntype.id,
                    name=ntype.name,
                    description=ntype.description,
                    trigger_keywords=ntype.trigger_keywords,
                    core_questions=ntype.example_questions,
                    methodology=f"基于女娲方法论自动生成，参考{ntype.name}类型视角标准模板",
                )

                generated_class = self.generator.generate(spec)
                instance = generated_class()
                analysis_parts.append(f"  → **{instance.name}** (ID: `{instance.id}`)")
                analysis_parts.append(f"     描述: {instance.description}")

                # 尝试注册到 registry
                try:
                    from super_thinking.core.registry import get_registry
                    reg = get_registry()
                    reg.register(instance)
                    analysis_parts.append(f"     ✅ 已注册到 Registry")
                except Exception as e:
                    analysis_parts.append(f"     ⚠️ 注册失败: {str(e)}")

                analysis_parts.append("")

        analysis_parts.extend([
            "---",
            "",
            "### 💡 女娲提示",
            "",
            "女娲的核心能力是**按需生成视角**。如果现有视角不够用，",
            "她会根据问题的本质特征，动态生成新的思维框架。",
            "",
            "生成的视角会自动注册，可立即在其他分析中调用。",
        ])

        # 构建 key_points
        key_points = [
            f"需求类型: {', '.join(t.name for t in needed_types)}",
            f"现有覆盖: {len(covered)}/{len(needed_types)}",
            f"推荐组合: {', '.join(recommendation['existing_recommended']) if recommendation['existing_recommended'] else '无'}",
        ]

        if recommendation["new_perspectives_needed"]:
            key_points.append(
                f"将生成: {', '.join(t.name for t in recommendation['new_perspectives_needed'])}"
            )

        warnings = []
        if recommendation["new_perspectives_needed"]:
            warnings.append("自动生成的视角未经人工验证，建议复核分析结果")

        return PerspectiveOutput(
            perspective_id=self.id,
            perspective_name=self.name,
            analysis="\n".join(analysis_parts),
            key_points=key_points,
            confidence=recommendation["confidence"],
            tags=["meta", "nuwa", "perspective-generator"],
            warnings=warnings,
            metadata={
                "needed_types": [t.id for t in needed_types],
                "coverage": coverage,
                "recommendation": {
                    "existing": recommendation["existing_recommended"],
                    "new": [t.id for t in recommendation["new_perspectives_needed"]],
                },
            },
        )


# 注册单例
nuwa_meta_instance = NuwaMetaPerspective()
