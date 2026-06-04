"""
V-SuperBrain — 元认知层（系统自审）

在 Jury 之上添加自反思能力：
- 分析前：系统预判"这类问题我通常处理得怎样"
- 分析后：系统自审"刚才的分析质量如何，还有哪些遗漏"
- 自动记录到 V-Journal（经验沉淀）

灵感：V（浮光的 AI 助理）在"我在做什么"上清楚，
"我为什么这么做"模糊，"我做得怎么样"完全没 metric。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class SelfAuditResult:
    """自审结果。"""

    question: str
    question_type: str
    experts_used: list[str]
    confidence: float
    self_rating: float  # 系统自评 1-5
    strengths: list[str]
    weaknesses: list[str]
    improvements: list[str]
    missed_perspectives: list[str]
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class VBrainProfile:
    """V-SuperBrain 的自我认知画像（系统级，不混于用户画像）。"""

    session_id: str
    total_analyses: int = 0
    self_ratings: list[float] = field(default_factory=list)
    avg_self_rating: float = 0.0
    question_types_handled: dict[str, int] = field(default_factory=dict)
    strengths_by_type: dict[str, list[str]] = field(default_factory=dict)
    weaknesses_by_type: dict[str, list[str]] = field(default_factory=dict)
    missed_patterns: list[str] = field(default_factory=list)
    improvement_log: list[dict] = field(default_factory=list)

    def record_analysis(
        self,
        question_type: str,
        self_rating: float,
        strengths: list[str],
        weaknesses: list[str],
        improvements: list[str],
    ) -> None:
        """记录一次分析的自审结果。"""
        self.total_analyses += 1
        self.self_ratings.append(self_rating)
        self.avg_self_rating = sum(self.self_ratings) / len(self.self_ratings)

        # 记录问题类型分布
        self.question_types_handled[question_type] = (
            self.question_types_handled.get(question_type, 0) + 1
        )

        # 记录该类型的优劣势
        if question_type not in self.strengths_by_type:
            self.strengths_by_type[question_type] = []
            self.weaknesses_by_type[question_type] = []
        self.strengths_by_type[question_type].extend(strengths[:3])
        self.weaknesses_by_type[question_type].extend(weaknesses[:3])

        # 记录改进日志
        if improvements:
            self.improvement_log.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "question_type": question_type,
                "improvements": improvements,
            })

    def get_self_awareness(self, question_type: str) -> dict[str, Any]:
        """获取对特定问题类型的自我认知。"""
        return {
            "avg_rating": self.avg_self_rating,
            "total_analyses": self.total_analyses,
            "handled_types": self.question_types_handled,
            "strengths": self.strengths_by_type.get(question_type, [])[:5],
            "weaknesses": self.weaknesses_by_type.get(question_type, [])[:5],
            "recent_improvements": self.improvement_log[-3:] if self.improvement_log else [],
        }


class VSuperBrain:
    """
    V-SuperBrain：系统自审的超级大脑层。

    在 Jury 分析之上添加元认知：
    1. pre_think：分析前自审 — "这类问题我通常处理得怎样？"
    2. post_think：分析后自审 — "刚才的分析质量如何？哪些遗漏？"
    3. self_improve：记录改进点到 V-Journal

    使用方式：
        brain = VSuperBrain(jury)
        result = brain.think("30岁要不要跳槽？", user_id="default")
        audit = result.self_audit  # 自审结果
        print(audit.self_rating, audit.improvements)
    """

    def __init__(
        self,
        jury: Any,
        v_brain_profile: Optional[VBrainProfile] = None,
    ):
        self._jury = jury
        self._profile = v_brain_profile or VBrainProfile(
            session_id=datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        )

    @property
    def jury(self) -> Any:
        return self._jury

    @property
    def profile(self) -> VBrainProfile:
        return self._profile

    def pre_think(self, input: str, question_type: str) -> dict[str, Any]:
        """
        分析前的自我预判。

        Returns:
            包含预判和提醒的字典
        """
        awareness = self._profile.get_self_awareness(question_type)

        pre_warnings = []
        if awareness["total_analyses"] > 0:
            if awareness["avg_rating"] < 3.0:
                pre_warnings.append(
                    f"⚠️ 这类问题（{question_type}）历史平均分偏低({awareness['avg_rating']:.1f})，"
                    "建议多角度分析"
                )
            if awareness["weaknesses"]:
                pre_warnings.append(
                    f"💡 历史弱点：{'、'.join(awareness['weaknesses'][:2])}"
                )

        return {
            "pre_awareness": awareness,
            "pre_warnings": pre_warnings,
            "suggested_questions": self._generate_clarifying_questions(input, question_type),
        }

    def post_think(
        self,
        input: str,
        question_type: str,
        jury_result: Any,
    ) -> SelfAuditResult:
        """
        分析后的自我审查。

        评估维度：
        1. 覆盖率 — 是否涵盖了关键视角？
        2. 深度 — 分析是否有洞见还是流于表面？
        3. 实用性 — 建议是否可操作？
        4. 一致性 — 各专家视角是否有逻辑冲突？
        """
        experts_used = jury_result.analysis_metadata.get("experts_used", []) if jury_result.analysis_metadata else []
        outputs = jury_result.outputs

        strengths: list[str] = []
        weaknesses: list[str] = []
        improvements: list[str] = []
        missed: list[str] = []

        # 1. 覆盖率评估
        if len(experts_used) >= 3:
            strengths.append("多视角覆盖充分")
        else:
            weaknesses.append(f"视角数量偏少（{len(experts_used)}个）")
            improvements.append("考虑增加相关领域的专家视角")

        # 2. 分析深度评估
        has_long_analysis = any(
            len(getattr(o, "analysis", "")) > 500 for o in outputs.values()
        )
        if has_long_analysis:
            strengths.append("分析有一定深度")
        else:
            weaknesses.append("分析偏简略，缺乏深入展开")
            improvements.append("各视角建议展开到 300+ 字")

        # 3. 一致性检查（各视角结论是否矛盾）
        conclusions = []
        for output in outputs.values():
            if hasattr(output, "analysis") and output.analysis:
                lines = [l.strip() for l in output.analysis.split("\n") if l.strip()]
                conclusions.extend([l for l in lines if l.startswith("**") or l.startswith("##")])
        if len(set(conclusions)) < len(conclusions) * 0.3:
            weaknesses.append("各视角结论可能存在重复或矛盾")
            improvements.append("建议在综合阶段显式处理视角冲突")

        # 4. 置信度评估
        avg_confidence = sum(
            getattr(o, "confidence", 0.5) for o in outputs.values()
        ) / max(len(outputs), 1)

        # 5. 问题类型特定检查
        if question_type == "职业发展":
            if not any("商业" in e or "管理" in e for e in experts_used):
                missed.append("职业发展问题通常需要商业/管理视角（如巴菲特、芒格）")
        elif question_type == "人生规划":
            if not any("哲学" in e or "尼采" in e or "加缪" in e for e in experts_used):
                missed.append("人生规划问题通常需要哲学视角（如尼采、加缪）")
        elif question_type == "创业商业":
            if not any("投资" in e or "商业" in e for e in experts_used):
                missed.append("创业问题通常需要投资视角（如巴菲特、芒格）")

        if missed:
            improvements.append(f"遗漏视角：{'；'.join(missed)}")

        # 计算自我评分
        self_rating = 3.0  # 基础分
        self_rating += 0.2 * len(strengths)
        self_rating -= 0.3 * len(weaknesses)
        self_rating = max(1.0, min(5.0, self_rating))

        audit = SelfAuditResult(
            question=input,
            question_type=question_type,
            experts_used=experts_used,
            confidence=avg_confidence,
            self_rating=round(self_rating, 2),
            strengths=strengths,
            weaknesses=weaknesses,
            improvements=improvements,
            missed_perspectives=missed,
        )

        # 记录到画像
        self._profile.record_analysis(
            question_type,
            self_rating,
            strengths,
            weaknesses,
            improvements,
        )

        return audit

    def _generate_clarifying_questions(self, input: str, question_type: str) -> list[str]:
        """生成澄清性问题（分析前追问）。"""
        base = ["这个问题对你来说，核心困惑是什么？"]
        if question_type == "职业发展":
            base.append("你考虑跳槽的原因是薪资、成长、还是环境？")
        elif question_type == "人生规划":
            base.append("你目前处于什么人生阶段？")
        elif question_type == "情感关系":
            base.append("这个问题是关于亲密关系、亲情、还是社交？")
        elif question_type == "创业商业":
            base.append("你的项目目前处于什么阶段？MVP、增长、还是盈利？")
        return base

    def think(
        self,
        input: str,
        context: Optional[dict[str, Any]] = None,
        mode: str = "auto",
        user_id: Optional[str] = None,
    ) -> Any:
        """
        完整的超级大脑思考（含前后自审）。

        返回 JuryResult 增强版，含 self_audit 字段。
        """
        # Step 1: 预判
        question_type = "通用问题"
        if self._jury._profile_manager and user_id:
            try:
                question_type = self._jury._profile_manager.classify_question(input)
            except Exception:
                pass

        pre = self.pre_think(input, question_type)

        # Step 2: Jury 分析
        jury_result = self._jury.think(
            input=input,
            context=context,
            mode=mode,
            user_id=user_id,
        )

        # Step 3: 自审
        audit = self.post_think(input, question_type, jury_result)

        # 将自审结果附加到 jury_result（不修改原 dataclass）
        # 通过动态属性注入
        jury_result.self_audit = audit
        jury_result.pre_analysis = pre

        # 如果有 V-Journal 路径，记录改进
        self._log_to_v_journal(audit)

        return jury_result

    def _log_to_v_journal(self, audit: SelfAuditResult) -> None:
        """将自审结果追加到 V-Journal（如果可写）。"""
        try:
            import os
            vj_path = os.path.join(
                os.path.dirname(__file__),
                "..", "..", "..",
                "docs", "v-journal", "super_brain_log.md"
            )
            vj_path = os.path.normpath(vj_path)

            if os.path.exists(os.path.dirname(vj_path)):
                timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
                entry = f"\n## [{timestamp}] {audit.question[:40]}...\n"
                entry += f"- 自我评分: {audit.self_rating}/5\n"
                entry += f"- 问题类型: {audit.question_type}\n"
                entry += f"- 使用视角: {', '.join(audit.experts_used)}\n"
                if audit.improvements:
                    entry += f"- 改进建议: {'；'.join(audit.improvements)}\n"

                with open(vj_path, "a", encoding="utf-8") as f:
                    f.write(entry)
                logger.debug(f"V-SuperBrain: 记录到 {vj_path}")
        except Exception as e:
            logger.debug(f"V-SuperBrain: 无法写入 V-Journal: {e}")


# 便捷函数
def create_super_brain(
    jury: Any,
    session_id: Optional[str] = None,
) -> VSuperBrain:
    """创建 V-SuperBrain 实例。"""
    profile = VBrainProfile(
        session_id=session_id or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    )
    return VSuperBrain(jury=jury, v_brain_profile=profile)
