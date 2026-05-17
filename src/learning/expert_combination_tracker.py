"""
ExpertCombinationTracker - 专家组合追踪器

专门负责追踪和推荐专家组合的效果。
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from collections import defaultdict
import json


class ExpertCombinationTracker:
    """
    专家组合效果追踪器。
    
    追踪：
    - 哪些专家组合效果好
    - 在什么上下文中有效
    - 组合的历史表现
    
    推荐：
    - 基于历史推荐最佳组合
    - 基于上下文推荐相似组合
    """
    
    # 组合效果评级
    EFFECTIVENESS_RATING = {
        "excellent": 0.85,  # 极好
        "good": 0.70,       # 良好
        "average": 0.50,    # 一般
        "poor": 0.30        # 较差
    }
    
    def __init__(self, combinations: Optional[Dict] = None):
        """
        初始化追踪器。
        
        Args:
            combinations: 初始组合数据字典
        """
        self.combinations = combinations or {}
        self._index_cache = self._build_index()
    
    def _build_index(self) -> Dict[str, List[str]]:
        """构建组合索引，加速查询。"""
        index = defaultdict(list)
        
        for combo_key in self.combinations.keys():
            # 提取每个专家作为索引
            experts = combo_key.split("+")
            for expert in experts:
                index[expert].append(combo_key)
        
        return dict(index)
    
    def _make_key(self, experts: List[str]) -> str:
        """生成组合键（排序后用+连接）。"""
        return "+".join(sorted(experts))
    
    def record(self, experts: List[str], rating: int, context: str = "", 
               response_time_ms: int = 0, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        记录一次专家组合的使用。
        
        Args:
            experts: 专家列表
            rating: 评分 (1-5)
            context: 上下文信息
            response_time_ms: 响应时间（毫秒）
            metadata: 额外元数据
            
        Returns:
            记录结果
        """
        if len(experts) < 2:
            return {"recorded": False, "reason": "需要至少2位专家"}
        
        combo_key = self._make_key(experts)
        
        # 获取或创建组合记录
        if combo_key not in self.combinations:
            self.combinations[combo_key] = {
                "success_count": 0,
                "total_count": 0,
                "success_rate": 0.0,
                "avg_rating": 0.0,
                "avg_response_time": 0.0,
                "last_success": None,
                "last_used": None,
                "contexts": [],
                "examples": [],
                "question_types": defaultdict(int),
                "created_at": datetime.now().isoformat()
            }
        
        combo = self.combinations[combo_key]
        
        # 更新统计
        combo["total_count"] += 1
        combo["last_used"] = datetime.now().isoformat()
        
        if rating >= 4:
            combo["success_count"] += 1
            combo["last_success"] = datetime.now().isoformat()
        
        # 更新平均评分
        total = combo["total_count"]
        old_total = total - 1
        combo["avg_rating"] = (combo["avg_rating"] * old_total + rating) / total
        
        # 更新平均响应时间
        if response_time_ms > 0:
            combo["avg_response_time"] = (
                (combo["avg_response_time"] * old_total + response_time_ms) / total
            )
        
        # 记录上下文
        if context and context not in combo["contexts"]:
            combo["contexts"].append(context)
        
        # 记录示例（最多保留10个）
        if rating >= 4 and len(combo["examples"]) < 10:
            combo["examples"].append({
                "rating": rating,
                "context": context,
                "timestamp": datetime.now().isoformat()
            })
        
        # 更新问题类型统计
        if metadata and "question_type" in metadata:
            combo["question_types"][metadata["question_type"]] += 1
        
        # 重新计算成功率
        combo["success_rate"] = combo["success_count"] / combo["total_count"]
        
        # 更新索引缓存
        self._index_cache = self._build_index()
        
        return {
            "recorded": True,
            "combination": combo_key,
            "experts": experts,
            "total_count": combo["total_count"],
            "success_count": combo["success_count"],
            "success_rate": combo["success_rate"],
            "avg_rating": combo["avg_rating"]
        }
    
    def get(self, experts: List[str]) -> Optional[Dict[str, Any]]:
        """
        获取组合数据。
        
        Args:
            experts: 专家列表
            
        Returns:
            组合数据或None
        """
        combo_key = self._make_key(experts)
        return self.combinations.get(combo_key)
    
    def get_success_rate(self, experts: List[str]) -> float:
        """
        获取组合成功率。
        
        Args:
            experts: 专家列表
            
        Returns:
            成功率 (0.0 - 1.0)
        """
        combo = self.get(experts)
        if not combo:
            return 0.0
        return combo.get("success_rate", 0.0)
    
    def find_best_for_context(self, context: str, min_count: int = 2) -> List[Dict[str, Any]]:
        """
        根据上下文查找最佳组合。
        
        Args:
            context: 上下文字符串
            min_count: 最小使用次数
            
        Returns:
            最佳组合列表
        """
        candidates = []
        
        for combo_key, data in self.combinations.items():
            if data["total_count"] < min_count:
                continue
            
            # 检查上下文匹配
            context_match = False
            for stored_context in data.get("contexts", []):
                if stored_context and context:
                    # 简单匹配：包含关系
                    if stored_context in context or context in stored_context:
                        context_match = True
                        break
            
            if context_match:
                candidates.append({
                    "combination": combo_key,
                    "experts": combo_key.split("+"),
                    "success_rate": data["success_rate"],
                    "avg_rating": data["avg_rating"],
                    "total_count": data["total_count"],
                    "context_match": True
                })
        
        # 按成功率排序
        candidates.sort(key=lambda x: (x["success_rate"], x["avg_rating"]), reverse=True)
        
        return candidates[:5]
    
    def find_best_overall(self, min_count: int = 2, limit: int = 10) -> List[Dict[str, Any]]:
        """
        查找整体最佳组合。
        
        Args:
            min_count: 最小使用次数
            limit: 返回数量限制
            
        Returns:
            最佳组合列表
        """
        candidates = []
        
        for combo_key, data in self.combinations.items():
            if data["total_count"] < min_count:
                continue
            
            candidates.append({
                "combination": combo_key,
                "experts": combo_key.split("+"),
                "success_rate": data["success_rate"],
                "avg_rating": data["avg_rating"],
                "total_count": data["total_count"],
                "last_used": data.get("last_used"),
                "effectiveness": self._rate_effectiveness(data["success_rate"])
            })
        
        # 按成功率+评分综合排序
        candidates.sort(
            key=lambda x: (x["success_rate"] * 100 + x["avg_rating"], x["total_count"]),
            reverse=True
        )
        
        return candidates[:limit]
    
    def find_by_expert(self, expert: str, min_count: int = 2) -> List[Dict[str, Any]]:
        """
        查找包含特定专家的所有组合。
        
        Args:
            expert: 专家名称
            min_count: 最小使用次数
            
        Returns:
            组合列表
        """
        combo_keys = self._index_cache.get(expert, [])
        results = []
        
        for combo_key in combo_keys:
            data = self.combinations[combo_key]
            if data["total_count"] >= min_count:
                results.append({
                    "combination": combo_key,
                    "experts": combo_key.split("+"),
                    "success_rate": data["success_rate"],
                    "avg_rating": data["avg_rating"],
                    "total_count": data["total_count"]
                })
        
        results.sort(key=lambda x: x["success_rate"], reverse=True)
        return results
    
    def suggest_new_combinations(self, used_experts: List[str], count: int = 3) -> List[Dict[str, Any]]:
        """
        推荐新的专家组合（基于现有数据）。
        
        策略：
        1. 找出与已用专家频繁搭配且效果好的专家
        2. 找出与已用专家形成互补的专家
        
        Args:
            used_experts: 已使用的专家列表
            count: 推荐数量
            
        Returns:
            推荐组合列表
        """
        suggestions = []
        
        # 统计与已用专家搭配的专家
        partner_stats = defaultdict(lambda: {"count": 0, "success_sum": 0})
        
        for used in used_experts:
            combos_with_used = self.find_by_expert(used, min_count=1)
            for combo in combos_with_used:
                partners = [e for e in combo["experts"] if e != used]
                for partner in partners:
                    partner_stats[partner]["count"] += combo["total_count"]
                    partner_stats[partner]["success_sum"] += combo["success_rate"] * combo["total_count"]
        
        # 计算每个潜在伙伴的得分
        partner_scores = []
        for partner, stats in partner_stats.items():
            if stats["count"] > 0:
                avg_success = stats["success_sum"] / stats["count"]
                partner_scores.append({
                    "expert": partner,
                    "times_together": stats["count"],
                    "avg_success_when_together": avg_success
                })
        
        partner_scores.sort(key=lambda x: (x["avg_success_when_together"], x["times_together"]), reverse=True)
        
        # 生成推荐组合
        top_partners = [p["expert"] for p in partner_scores[:3]]
        
        # 组合1：最常搭配且效果好的
        for partner in top_partners:
            if partner not in used_experts:
                new_combo = sorted(used_experts + [partner])
                combo_key = self._make_key(new_combo)
                
                # 检查是否已存在
                if combo_key not in self.combinations:
                    suggestions.append({
                        "type": "frequently_together",
                        "experts": new_combo,
                        "reason": f"与{'、'.join(used_experts)}经常搭配使用"
                    })
        
        # 组合2：互补型（添加不同领域的专家）
        all_experts = set()
        for combos in self.combinations.values():
            for exp in combos.get("examples", []):
                if exp.get("context"):
                    all_experts.add(exp["context"].split("：")[0] if "：" in exp["context"] else "")
        
        # 去重已用的
        for expert in used_experts:
            all_experts.discard(expert)
        
        return suggestions[:count]
    
    def _rate_effectiveness(self, success_rate: float) -> str:
        """根据成功率评级。"""
        for rating, threshold in self.EFFECTIVENESS_RATING.items():
            if success_rate >= threshold:
                return rating
        return "poor"
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取组合追踪统计。
        
        Returns:
            统计字典
        """
        if not self.combinations:
            return {
                "total_combinations": 0,
                "total_usages": 0,
                "avg_success_rate": 0.0,
                "excellent_combinations": 0,
                "most_used": []
            }
        
        total_usages = sum(c["total_count"] for c in self.combinations.values())
        total_success = sum(c["success_count"] for c in self.combinations.values())
        
        # 找出最常用的组合
        sorted_by_usage = sorted(
            self.combinations.items(),
            key=lambda x: x[1]["total_count"],
            reverse=True
        )
        
        return {
            "total_combinations": len(self.combinations),
            "total_usages": total_usages,
            "total_successes": total_success,
            "avg_success_rate": total_success / total_usages if total_usages > 0 else 0.0,
            "excellent_combinations": sum(
                1 for c in self.combinations.values()
                if self._rate_effectiveness(c["success_rate"]) == "excellent"
            ),
            "most_used": [
                {
                    "combination": key,
                    "experts": key.split("+"),
                    "total_count": data["total_count"]
                }
                for key, data in sorted_by_usage[:5]
            ]
        }
    
    def export_data(self) -> str:
        """导出数据为JSON字符串。"""
        return json.dumps(self.combinations, ensure_ascii=False, indent=2)
    
    def import_data(self, data: str) -> bool:
        """
        从JSON字符串导入数据。
        
        Args:
            data: JSON字符串
            
        Returns:
            是否成功
        """
        try:
            self.combinations = json.loads(data)
            self._index_cache = self._build_index()
            return True
        except json.JSONDecodeError:
            return False
    
    def merge(self, other: "ExpertCombinationTracker") -> None:
        """
        合并另一个追踪器的数据。
        
        Args:
            other: 另一个追踪器实例
        """
        for combo_key, other_data in other.combinations.items():
            if combo_key in self.combinations:
                # 合并统计
                self.combinations[combo_key]["total_count"] += other_data["total_count"]
                self.combinations[combo_key]["success_count"] += other_data["success_count"]
                self.combinations[combo_key]["success_rate"] = (
                    self.combinations[combo_key]["success_count"] / 
                    self.combinations[combo_key]["total_count"]
                )
                
                # 合并上下文（去重）
                for ctx in other_data.get("contexts", []):
                    if ctx not in self.combinations[combo_key]["contexts"]:
                        self.combinations[combo_key]["contexts"].append(ctx)
            else:
                self.combinations[combo_key] = other_data.copy()
        
        self._index_cache = self._build_index()
