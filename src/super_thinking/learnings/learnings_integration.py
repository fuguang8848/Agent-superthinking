"""
Learnings Integration — 将 AgentTeam .learnings 经验闭环接入 SuperThinking.

核心能力：
1. 每次分析完成后捕获经验（专家组合效果、问题类型反应）
2. 基于历史经验优化下次专家选择
3. 经验自动晋升到文档（AGENTS.md / SOUL.md）
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class LearningsIntegration:
    """
    经验闭环集成器。

    将 AgentTeam .learnings 系统适配到 SuperThinking：
    - 记录专家组合使用效果
    - 追踪问题类型与分析质量的映射
    - 经验自动晋升到文档

    使用方式：
        lm = LearningsIntegration()
        # 分析完成后记录
        lm.capture_analysis_result(question_type, experts_used, rating)
        # 下次分析前查询经验
        tips = lm.get_tips_for_question_type("创业商业")
        # 检查晋升
        promoted = lm.check_promotions()
    """

    def __init__(
        self,
        learnings_dir: Optional[str] = None,
    ):
        """
        初始化经验集成器。

        Args:
            learnings_dir: .learnings 文件存储目录
                          默认 ~/.hermes/superthinking_learnings
        """
        self._learnings_dir = Path(
            learnings_dir or "~/.hermes/superthinking_learnings"
        ).expanduser()
        self._learnings_dir.mkdir(parents=True, exist_ok=True)

        # 经验存储（简化版，不依赖 AgentTeam 的完整 Pydantic 模型）
        self._entries_file = self._learnings_dir / "analysis_experiences.json"
        self._experiences: list[dict] = []
        self._load()

        # 领域关键词映射
        self._area_keywords = {
            "职业发展": ["职业", "工作", "跳槽", "晋升", "职场", "career", "job"],
            "人生规划": ["人生", "意义", "目标", "规划", "迷茫", "life", "purpose"],
            "情感关系": ["情感", "恋爱", "婚姻", "家庭", "朋友", "relationship"],
            "创业商业": ["创业", "商业", "融资", "市场", "startup", "business"],
            "学术研究": ["研究", "论文", "学术", "research", "thesis"],
            "通用问题": [],
        }

    def _load(self) -> None:
        """从磁盘加载经验数据。"""
        if self._entries_file.exists():
            try:
                import json
                data = json.loads(self._entries_file.read_text(encoding="utf-8"))
                self._experiences = data if isinstance(data, list) else []
            except Exception:
                self._experiences = []

    def _save(self) -> None:
        """保存经验数据到磁盘。"""
        try:
            import json
            self._entries_file.write_text(
                json.dumps(self._experiences, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as e:
            logger.warning(f"Failed to save experiences: {e}")

    def _detect_area(self, question_type: str) -> str:
        """将问题类型映射到领域。"""
        return question_type

    def _now_iso(self) -> str:
        return datetime.now().isoformat()

    def capture_analysis_result(
        self,
        question_type: str,
        experts_used: list[str],
        rating: int,
        user_feedback: str = "",
        useful_experts: Optional[list[str]] = None,
        missing_experts: Optional[list[str]] = None,
        context: str = "",
    ) -> str:
        """
        捕获分析结果，记录为经验。

        Args:
            question_type: 问题类型
            experts_used: 使用的专家列表
            rating: 用户评分 (1-5)
            user_feedback: 用户反馈文本
            useful_experts: 认为有帮助的专家
            missing_experts: 认为缺失的专家

        Returns:
            经验条目 ID
        """
        import uuid

        entry_id = f"exp_{uuid.uuid4().hex[:8]}"
        combo_key = "+".join(sorted(experts_used)) if experts_used else "unknown"

        entry = {
            "entry_id": entry_id,
            "entry_type": "analysis_experience",
            "summary": f"[{question_type}] 使用专家组合 {combo_key}，评分 {rating}/5",
            "details": {
                "question_type": question_type,
                "experts_used": experts_used,
                "combo_key": combo_key,
                "rating": rating,
                "useful_experts": useful_experts or [],
                "missing_experts": missing_experts or [],
                "user_feedback": user_feedback,
                "context": context,
            },
            "area": self._detect_area(question_type),
            "priority": "high" if rating >= 4 else "medium",
            "count": 1,
            "first_seen": self._now_iso(),
            "last_seen": self._now_iso(),
            "resolved": False,
        }

        # 检查是否有相似的经验（相同专家组合 + 相同问题类型）
        similar = self._find_similar(combo_key, question_type)
        if similar:
            similar["count"] += 1
            similar["last_seen"] = self._now_iso()
            if rating >= 4:
                similar["details"]["success_count"] = similar["details"].get("success_count", 0) + 1
            entry_id = similar["entry_id"]
            logger.info(f"Merged into existing experience {entry_id} (count: {similar['count']})")
        else:
            entry["details"]["success_count"] = 1 if rating >= 4 else 0
            self._experiences.append(entry)
            logger.info(f"New experience: {entry_id} for {combo_key}")

        self._save()
        return entry_id

    def _find_similar(
        self, combo_key: str, question_type: str
    ) -> Optional[dict]:
        """查找相似的经验条目。"""
        for exp in self._experiences:
            details = exp.get("details", {})
            if (
                details.get("combo_key") == combo_key
                and details.get("question_type") == question_type
            ):
                return exp
        return None

    def get_tips_for_question_type(
        self,
        question_type: str,
        min_rating: float = 3.5,
        limit: int = 5,
    ) -> list[str]:
        """
        获取特定问题类型的经验建议。

        Args:
            question_type: 问题类型
            min_rating: 最低平均评分
            limit: 返回数量限制

        Returns:
            经验提示列表
        """
        tips = []
        seen_combos = set()

        # 按最近时间排序
        sorted_exps = sorted(
            self._experiences,
            key=lambda x: x.get("last_seen", ""),
            reverse=True,
        )

        for exp in sorted_exps:
            if len(tips) >= limit:
                break

            details = exp.get("details", {})
            if details.get("question_type") != question_type:
                continue

            combo_key = details.get("combo_key", "")
            if combo_key in seen_combos:
                continue

            rating = details.get("rating", 0)
            success_count = details.get("success_count", 0)
            count = exp.get("count", 1)

            # 计算成功率
            if count >= 1:
                success_rate = success_count / count
                avg_rating = rating  # 简化版只取最后一次评分
                if avg_rating >= min_rating:
                    seen_combos.add(combo_key)
                    tips.append(
                        f"专家组合「{combo_key}」历史评分 {avg_rating}/5，"
                        f"成功率 {success_rate:.0%}（{count}次使用）"
                    )

        return tips

    def get_best_expert_combinations(
        self,
        question_type: str,
        top_n: int = 3,
    ) -> list[dict[str, Any]]:
        """
        获取特定问题类型的最佳专家组合。

        Args:
            question_type: 问题类型
            top_n: 返回数量

        Returns:
            最佳组合列表，每项包含 combo_key、avg_rating、count
        """
        combos: dict[str, dict] = {}

        for exp in self._experiences:
            details = exp.get("details", {})
            if details.get("question_type") != question_type:
                continue

            combo_key = details.get("combo_key", "unknown")
            if combo_key not in combos:
                combos[combo_key] = {
                    "combo_key": combo_key,
                    "total_rating": 0,
                    "count": 0,
                    "experts": details.get("experts_used", []),
                    "useful_experts_all": [],
                    "missing_experts_all": [],
                }

            c = combos[combo_key]
            c["total_rating"] += details.get("rating", 0)
            c["count"] += 1
            c["useful_experts_all"].extend(details.get("useful_experts", []))
            c["missing_experts_all"].extend(details.get("missing_experts", []))

        # 计算平均评分并排序
        results = []
        for combo_key, data in combos.items():
            if data["count"] >= 1:
                avg = data["total_rating"] / data["count"]
                results.append({
                    "combo_key": combo_key,
                    "experts": data["experts"],
                    "avg_rating": round(avg, 2),
                    "count": data["count"],
                    "common_useful": list(set(data["useful_experts_all"])),
                    "common_missing": list(set(data["missing_experts_all"])),
                })

        results.sort(key=lambda x: (x["avg_rating"], x["count"]), reverse=True)
        return results[:top_n]

    def get_learning_summary(self, days: int = 7) -> str:
        """
        生成学习摘要报告。

        Args:
            days: 统计最近多少天的数据

        Returns:
            Markdown 格式的摘要报告
        """
        if not self._experiences:
            return "暂无经验数据。"

        # 统计各问题类型
        type_stats: dict[str, dict] = {}
        for exp in self._experiences:
            details = exp.get("details", {})
            qt = details.get("question_type", "未知")
            if qt not in type_stats:
                type_stats[qt] = {"count": 0, "total_rating": 0, "combos": set()}
            type_stats[qt]["count"] += 1
            type_stats[qt]["total_rating"] += details.get("rating", 0)
            type_stats[qt]["combos"].add(details.get("combo_key", ""))

        lines = [
            f"## SuperThinking 经验摘要（最近 {days} 天）\n",
            f"总经验条目：{len(self._experiences)}\n",
            f"覆盖问题类型：{len(type_stats)}\n\n",
        ]

        lines.append("### 按问题类型统计\n\n")
        lines.append("| 类型 | 分析次数 | 平均评分 | 组合数 |\n")
        lines.append("|------|----------|----------|--------|\n")

        for qt, stats in sorted(type_stats.items(), key=lambda x: x[1]["count"], reverse=True):
            avg = stats["total_rating"] / stats["count"] if stats["count"] > 0 else 0
            lines.append(
                f"| {qt} | {stats['count']} | {avg:.1f} | {len(stats['combos'])} |\n"
            )

        lines.append("\n### 最佳专家组合\n\n")
        for qt in type_stats:
            best = self.get_best_expert_combinations(qt, top_n=1)
            if best:
                b = best[0]
                lines.append(
                    f"- **{qt}**：「{b['combo_key']}」（评分 {b['avg_rating']}/5，"
                    f"{b['count']}次使用）\n"
                )

        return "".join(lines)

    def check_promotions(self) -> list[str]:
        """
        检查需要晋升的经验条目。

        当某专家组合使用次数 >= 5 且平均评分 >= 4 时，
        晋升到 SOUL.md 或相关文档。

        Returns:
            已晋升的经验条目 ID 列表
        """
        promoted = []
        for exp in self._experiences:
            if exp.get("resolved", False):
                continue

            details = exp.get("details", {})
            count = exp.get("count", 0)
            rating = details.get("rating", 0)

            if count >= 5 and rating >= 4:
                # 晋升到文档
                target = self._learnings_dir.parent / "SOUL.md"
                try:
                    existing = ""
                    if target.exists():
                        existing = target.read_text(encoding="utf-8")

                    combo_key = details.get("combo_key", "")
                    experts = details.get("experts_used", [])

                    promo_text = f"""
## 经验组合：{combo_key}

**问题类型**: {details.get('question_type', '通用')}
**使用次数**: {count}
**平均评分**: {rating}/5

**涉及专家**: {', '.join(experts)}
**有帮助的专家**: {', '.join(details.get('useful_experts', []))}
**缺失的专家**: {', '.join(details.get('missing_experts', []))}

**用户反馈摘要**: {details.get('user_feedback', '无')[:200]}

---
"""
                    target.write_text(existing + promo_text, encoding="utf-8")
                    exp["resolved"] = True
                    exp["promoted_to"] = str(target)
                    promoted.append(exp["entry_id"])
                    logger.info(f"Promoted {exp['entry_id']} to SOUL.md")
                except Exception as e:
                    logger.warning(f"Failed to promote: {e}")

        if promoted:
            self._save()
        return promoted

    def search(self, query: str, area: Optional[str] = None) -> list[dict]:
        """
        搜索经验条目。

        Args:
            query: 搜索关键词
            area: 可选，限定问题类型

        Returns:
            匹配的经验条目列表
        """
        results = []
        query_lower = query.lower()

        for exp in self._experiences:
            details = exp.get("details", {})
            if area and details.get("question_type") != area:
                continue

            # 匹配专家名称或问题类型
            combo_key = details.get("combo_key", "").lower()
            qt = details.get("question_type", "").lower()
            experts_str = " ".join(details.get("experts_used", [])).lower()

            if (
                query_lower in combo_key
                or query_lower in qt
                or query_lower in experts_str
            ):
                results.append(exp)

        return results
