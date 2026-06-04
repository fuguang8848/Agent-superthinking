"""
Supervisor Adapter — 将 AgentTeam Supervisor 分解能力接入 SuperThinking.

将复杂问题分解为专家子任务 DAG，并行执行不同视角簇，最后综合。

核心思路：
- 复杂问题 → Supervisor 分解 → TaskPlan(DAG)
- DAG 每一层 = 一批可并行执行的专家视角
- 各层结果汇聚 → 综合报告
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class QuestionComplexity(str, Enum):
    """问题复杂度等级。"""

    SIMPLE = "simple"  # 单视角直接回答
    MODERATE = "moderate"  # 多视角并行分析
    COMPLEX = "complex"  # 需要分解 + 多轮深化
    CRITICAL = "critical"  # 高风险决策，需要三角验证


@dataclass
class ExpertSubTask:
    """专家子任务。"""

    id: str
    expert_id: str  # perspective ID
    expert_name: str
    question: str  # 针对该专家的提问
    focus: str  # 分析焦点
    depends_on: list[str] = field(default_factory=list)  # 依赖的子任务 ID
    priority: int = 0
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class DecomposedQuestion:
    """分解后的问题结构。"""

    original: str
    complexity: QuestionComplexity
    question_type: str  # 从 ProfileManager 分类
    subtasks: list[ExpertSubTask]
    execution_layers: list[list[str]]  # DAG 层级，每层内可并行
    synthesis_prompt: str  # 综合阶段的提示词
    key_angles: list[str]  # 核心分析角度
    warnings: list[str]  # 需要警惕的思维陷阱


class SupervisorAdapter:
    """
    将 AgentTeam Supervisor 的任务分解能力适配到 SuperThinking.

    使用方式：
        adapter = SupervisorAdapter(profile_manager)
        plan = adapter.decompose("创业还是打工？")
        for layer in plan.execution_layers:
            results = jury.execute_layer(layer)  # 并行
            jury.synthesize(results)
    """

    # 问题复杂度关键词
    COMPLEXITY_KEYWORDS = {
        QuestionComplexity.SIMPLE: [
            "是什么", "什么是", "介绍一下", "简单说说", "what is",
        ],
        QuestionComplexity.MODERATE: [
            "分析", "对比", "如何看待", "评价", "选择", "哪个好",
            "analyze", "compare", "evaluate", "choose",
        ],
        QuestionComplexity.COMPLEX: [
            "创业", "转型", "人生规划", "重大决策", "要不要", "是否应该",
            "长期", "未来", "规划",
        ],
        QuestionComplexity.CRITICAL: [
            "投资", "风险", "生死", "离婚", "犯罪", "大额", "高风险",
            "invest", "risk", "life-changing",
        ],
    }

    # 专家组合模板（按问题类型）
    EXPERT_TEMPLATES = {
        "职业发展": {
            "required": ["稻盛和夫", "德鲁克"],
            "optional": ["乔布斯", "查理芒格", "马斯克"],
            "synthesis": "综合职业发展专家建议，给出可执行的发展路径",
        },
        "人生规划": {
            "required": ["尼采", "加缪"],
            "optional": ["苏格拉底", "王阳明", "孔子"],
            "synthesis": "综合哲学视角，给出人生方向指引",
        },
        "情感关系": {
            "required": ["佛学视角", "心理学视角"],
            "optional": ["孔子", "亚里士多德"],
            "synthesis": "综合情感专家建议，给出关系改善方向",
        },
        "创业商业": {
            "required": ["巴菲特", "查理芒格"],
            "optional": ["孙正义", "马斯克", "马云"],
            "synthesis": "综合商业专家建议，给出商业决策支持",
        },
        "学术研究": {
            "required": ["费曼", "西蒙"],
            "optional": ["学科专家"],
            "synthesis": "综合学术专家建议，给出研究方法指导",
        },
        "通用问题": {
            "required": ["苏格拉底"],
            "optional": ["亚里士多德", "孔子", "尼采"],
            "synthesis": "综合多元视角，给出平衡的分析结论",
        },
    }

    def __init__(self, profile_manager: Optional[Any] = None):
        self._profile_manager = profile_manager

    def decompose(
        self,
        question: str,
        user_id: Optional[str] = None,
        force_complexity: Optional[QuestionComplexity] = None,
    ) -> DecomposedQuestion:
        """
        将问题分解为专家子任务 DAG。

        Args:
            question: 用户问题
            user_id: 可选，用于读取画像调整专家选择
            force_complexity: 可选，强制指定复杂度

        Returns:
            DecomposedQuestion：包含子任务列表和执行层级
        """
        # 1. 判断复杂度
        complexity = force_complexity or self._judge_complexity(question)

        # 2. 分类问题类型
        question_type = self._classify_question(question)

        # 3. 选择专家组合
        experts = self._select_experts(question_type, complexity, user_id)

        # 4. 生成子任务
        subtasks = self._generate_subtasks(question, question_type, experts)

        # 5. 构建 DAG 执行层级
        layers = self._build_execution_layers(subtasks)

        # 6. 生成分综合提示
        synthesis_prompt = self._generate_synthesis_prompt(
            question, question_type, experts
        )

        return DecomposedQuestion(
            original=question,
            complexity=complexity,
            question_type=question_type,
            subtasks=subtasks,
            execution_layers=layers,
            synthesis_prompt=synthesis_prompt,
            key_angles=self._extract_key_angles(question, question_type),
            warnings=self._extract_warnings(question_type),
        )

    def _judge_complexity(self, question: str) -> QuestionComplexity:
        """判断问题复杂度。"""
        q = question.lower()

        # 优先级：CRITICAL > COMPLEX > MODERATE > SIMPLE
        for kw in self.COMPLEXITY_KEYWORDS[QuestionComplexity.CRITICAL]:
            if kw in q:
                return QuestionComplexity.CRITICAL

        for kw in self.COMPLEXITY_KEYWORDS[QuestionComplexity.COMPLEX]:
            if kw in q:
                return QuestionComplexity.COMPLEX

        for kw in self.COMPLEXITY_KEYWORDS[QuestionComplexity.MODERATE]:
            if kw in q:
                return QuestionComplexity.MODERATE

        return QuestionComplexity.SIMPLE

    def _classify_question(self, question: str) -> str:
        """分类问题类型。"""
        if self._profile_manager is not None:
            try:
                return self._profile_manager.classify_question(question)
            except Exception:
                pass

        # 回退：关键词匹配
        keywords_map = {
            "职业发展": ["职业", "工作", "跳槽", "职场", "晋升", "career", "job"],
            "人生规划": ["人生", "意义", "目标", "规划", "未来", "迷茫"],
            "情感关系": ["情感", "恋爱", "分手", "婚姻", "家庭", "朋友"],
            "创业商业": ["创业", "商业", "融资", "市场", "产品", "startup"],
            "学术研究": ["研究", "论文", "学术", "research", "thesis"],
        }

        q_lower = question.lower()
        for qtype, kws in keywords_map.items():
            for kw in kws:
                if kw.lower() in q_lower:
                    return qtype

        return "通用问题"

    def _select_experts(
        self,
        question_type: str,
        complexity: QuestionComplexity,
        user_id: Optional[str] = None,
    ) -> list[str]:
        """根据问题类型和复杂度选择专家。"""
        template = self.EXPERT_TEMPLATES.get(
            question_type, self.EXPERT_TEMPLATES["通用问题"]
        )

        # 基础组合
        if complexity == QuestionComplexity.SIMPLE:
            selected = template["required"][:2]
        elif complexity == QuestionComplexity.MODERATE:
            selected = template["required"] + template["optional"][:2]
        elif complexity == QuestionComplexity.COMPLEX:
            selected = template["required"] + template["optional"]
        else:  # CRITICAL
            selected = template["required"] + template["optional"]

        # 画像调整
        if user_id and self._profile_manager is not None:
            try:
                profile = self._profile_manager.get_profile(user_id)
                adjusted = self._adjust_by_profile(selected, profile, question_type)
                selected = adjusted
            except Exception:
                pass

        return selected

    def _adjust_by_profile(
        self,
        experts: list[str],
        profile: dict,
        question_type: str,
    ) -> list[str]:
        """基于用户画像调整专家选择。"""
        expert_prefs = profile.get("expert_preferences", {})
        question_patterns = profile.get("question_patterns", {})
        personal_preferred = []

        # 从画像中提取该问题类型偏好专家
        if question_type in question_patterns:
            preferred = question_patterns[question_type].get("preferred_experts", [])
            personal_preferred = [e for e in preferred if e in experts]

        # 按偏好得分排序
        def pref_score(name: str) -> float:
            if name in expert_prefs:
                return expert_prefs[name].get("score", 0)
            return 0.0

        # 将画像偏好专家排在前面
        preferred_sorted = sorted(personal_preferred, key=pref_score, reverse=True)
        other = [e for e in experts if e not in personal_preferred]
        return preferred_sorted + other

    def _generate_subtasks(
        self,
        question: str,
        question_type: str,
        experts: list[str],
    ) -> list[ExpertSubTask]:
        """为每个专家生成子任务。"""
        subtasks = []
        task_id_prefix = f"task_{datetime.now().strftime('%H%M%S')}"

        # 焦点模板
        focus_templates = {
            "职业发展": [
                "职业选择的核心判断标准",
                "长期职业发展路径规划",
                "职场人际关系处理",
            ],
            "人生规划": [
                "人生意义与价值取向",
                "面对不确定性的态度",
                "行动与坚持的平衡",
            ],
            "情感关系": [
                "情感需求的深层分析",
                "关系中的边界与责任",
                "长期亲密关系经营",
            ],
            "创业商业": [
                "商业机会识别与评估",
                "风险与收益的权衡",
                "执行力与战略的配合",
            ],
            "学术研究": [
                "研究方法论反思",
                "知识体系的构建",
                "创新与传承的关系",
            ],
            "通用问题": [
                "问题的本质分析",
                "多元视角的整合",
                "行动建议",
            ],
        }

        focuses = focus_templates.get(question_type, focus_templates["通用问题"])

        for i, expert in enumerate(experts):
            focus = focuses[i % len(focuses)]
            subtask = ExpertSubTask(
                id=f"{task_id_prefix}_{i}",
                expert_id=self._expert_name_to_id(expert),
                expert_name=expert,
                question=question,
                focus=focus,
                priority=len(experts) - i,
            )
            subtasks.append(subtask)

        return subtasks

    def _expert_name_to_id(self, name: str) -> str:
        """将专家名称转换为 perspective ID。"""
        # 简单映射：中文名 → 拼音（部分已知 ID）
        name_map = {
            "尼采": "nietzsche_perspective",
            "加缪": "camus_perspective",
            "苏格拉底": "socrates_perspective",
            "孔子": "confucius_perspective",
            "王阳明": "wang_yangming_perspective",
            "巴菲特": "buffett_perspective",
            "查理芒格": "munger_perspective",
            "马斯克": "musk_perspective",
            "乔布斯": "jobs_perspective",
            "德鲁克": "drucker_perspective",
            "稻盛和夫": "inaochi_perspective",
            "费曼": "feynman_perspective",
            "西蒙": "simon_perspective",
            "佛学视角": "buddhism_perspective",
            "心理学视角": "psychology_perspective",
            "孙正义": "masayoshi_perspective",
        }
        return name_map.get(name, f"perspective_{name}")

    def _build_execution_layers(
        self,
        subtasks: list[ExpertSubTask],
    ) -> list[list[str]]:
        """
        构建 DAG 执行层级。

        返回：[[task_id, ...], [task_id, ...], ...]
        每层内任务可并行执行，层间需等待。
        目前所有子任务无依赖关系，全部在第一层。
        未来可扩展：根据专家之间的依赖关系构建 DAG。
        """
        if not subtasks:
            return []

        # 当前版本：所有子任务无依赖，单层并行
        # 未来可基于专家知识图谱建立依赖（如：先哲学分析，再商业落地）
        return [[t.id for t in subtasks]]

    def _generate_synthesis_prompt(
        self,
        question: str,
        question_type: str,
        experts: list[str],
    ) -> str:
        """生成分综合阶段的提示词。"""
        template = self.EXPERT_TEMPLATES.get(
            question_type, self.EXPERT_TEMPLATES["通用问题"]
        )
        return template["synthesis"]

    def _extract_key_angles(self, question: str, question_type: str) -> list[str]:
        """提取核心分析角度。"""
        base_angles = {
            "职业发展": ["个人优势", "行业趋势", "长期价值", "风险控制"],
            "人生规划": ["意义追寻", "行动实践", "内心平静", "社会价值"],
            "情感关系": ["需求匹配", "沟通质量", "共同成长", "边界清晰"],
            "创业商业": ["市场机会", "竞争壁垒", "团队能力", "资本效率"],
            "学术研究": ["方法论", "创新性", "可行性", "影响力"],
            "通用问题": ["事实层面", "价值层面", "行动层面", "风险层面"],
        }
        return base_angles.get(question_type, base_angles["通用问题"])

    def _extract_warnings(self, question_type: str) -> list[str]:
        """提取需要警惕的思维陷阱。"""
        warnings = {
            "职业发展": [
                "过度关注短期薪资，忽视长期成长",
                "把平台能力当成个人能力",
            ],
            "人生规划": [
                "用宏大叙事逃避具体行动",
                "过度规划未来而忽视当下",
            ],
            "情感关系": [
                "把期待寄托在对方改变上",
                "用理性分析替代情感体验",
            ],
            "创业商业": [
                "低估执行难度，高估市场规模",
                "忽视现金流，只看愿景",
            ],
            "学术研究": [
                "过度追求创新而忽视扎实性",
                "用文献堆砌替代独立思考",
            ],
            "通用问题": [
                "确认偏误：只看到支持自己观点的证据",
                "后见之明：把结果回溯为必然",
            ],
        }
        return warnings.get(question_type, warnings["通用问题"])
