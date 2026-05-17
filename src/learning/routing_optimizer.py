"""
RoutingOptimizer - 路由优化器

基于用户反馈和画像数据，优化专家路由权重。
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict


class RoutingOptimizer:
    """
    路由优化器。
    
    提供：
    - 基于画像动态调整专家权重
    - 专家组合效果追踪
    - 最佳组合推荐
    """
    
    # 问题类型与专家映射
    DEFAULT_EXPERT_POOL = {
        "职业发展": {
            "people": ["稻盛和夫", "德鲁克", "乔布斯", "杰克韦尔奇"],
            "methods": ["目标管理", "时间管理", "战略规划"],
            "fields": ["管理学", "组织行为学"]
        },
        "人生规划": {
            "people": ["尼采", "加缪", "苏格拉底", "王阳明", "老子", "孔子"],
            "methods": ["反思方法", "存在主义分析"],
            "fields": ["哲学", "伦理学"]
        },
        "情感关系": {
            "people": ["佛学视角", "心理学视角", "孔子"],
            "methods": ["依恋理论", "沟通技巧"],
            "fields": ["心理学", "社会学"]
        },
        "创业商业": {
            "people": ["巴菲特", "查理芒格", "孙正义", "马斯克", "马云"],
            "methods": ["价值投资", "精益创业", "战略分析"],
            "fields": ["金融学", "经济学", "市场营销"]
        },
        "学术研究": {
            "people": ["费曼", "西蒙"],
            "methods": ["科学方法", "批判性思维"],
            "fields": ["学科专家"]
        },
        "通用问题": {
            "people": ["苏格拉底", "亚里士多德", "孔子", "佛学视角"],
            "methods": ["批判性思维", "逻辑分析"],
            "fields": ["哲学", "心理学"]
        }
    }
    
    # 动态加成配置
    BOOST_CONFIG = {
        "recent_success_days": 7,      # 最近成功的时间窗口
        "recent_success_boost": 0.1,   # 最近成功加成
        "context_match_boost": 0.2,    # 上下文匹配加成
        "streak_bonus_per": 0.05,      # 连续使用加成（每次）
        "max_streak_boost": 0.2,       # 连续使用最大加成
        "high_success_rate_threshold": 0.8  # 高成功率阈值
    }
    
    def __init__(self, profile: Optional[Dict] = None):
        """
        初始化 RoutingOptimizer。
        
        Args:
            profile: 用户画像字典
        """
        self.profile = profile or {}
        self._weights_cache = {}
    
    def set_profile(self, profile: Dict) -> None:
        """设置用户画像。"""
        self.profile = profile
        self._weights_cache = {}
    
    def adjust_weights(self, question_type: str, base_weights: Optional[Dict] = None) -> Dict[str, float]:
        """
        基于用户画像调整专家权重。
        
        Args:
            question_type: 问题类型
            base_weights: 基础权重字典
            
        Returns:
            调整后的专家权重字典
        """
        # 获取基础权重
        if base_weights is None:
            base_weights = self._get_default_weights(question_type)
        
        # 获取画像中的调整
        personal_adj = self.profile.get("routing_weights", {}).get("personal_adjustments", {})
        expert_prefs = self.profile.get("expert_preferences", {})
        stats = self.profile.get("statistics", {})
        
        # 计算动态加成
        dynamic_boosts = self._calculate_dynamic_boosts(expert_prefs)
        
        # 计算最终权重
        final_weights = {}
        for expert, base_weight in base_weights.items():
            weight = base_weight
            
            # 加上个人调整
            if expert in personal_adj:
                weight += personal_adj[expert]
            
            # 加上动态加成
            if expert in dynamic_boosts:
                weight += dynamic_boosts[expert]
            
            # 确保权重在有效范围内
            final_weights[expert] = max(0.0, min(1.0, weight))
        
        # 对权重进行归一化
        total = sum(final_weights.values())
        if total > 0:
            final_weights = {k: v / total for k, v in final_weights.items()}
        
        return final_weights
    
    def _get_default_weights(self, question_type: str) -> Dict[str, float]:
        """获取默认专家权重。"""
        default_weights = self.profile.get("routing_weights", {}).get("default_weights", {})
        
        if question_type in default_weights:
            return default_weights[question_type].copy()
        
        # 返回通用默认权重
        return {
            "苏格拉底": 0.7,
            "亚里士多德": 0.6,
            "孔子": 0.6,
            "尼采": 0.5,
            "加缪": 0.5,
            "心理学视角": 0.5
        }
    
    def _calculate_dynamic_boosts(self, expert_prefs: Dict) -> Dict[str, float]:
        """计算动态加成。"""
        boosts = {}
        config = self.BOOST_CONFIG
        
        for expert, pref in expert_prefs.items():
            boost = 0.0
            
            # 最近成功加成
            if pref.get("last_used"):
                try:
                    last_used = datetime.fromisoformat(pref["last_used"])
                    days_since = (datetime.now() - last_used).days
                    if days_since <= config["recent_success_days"]:
                        boost += config["recent_success_boost"]
                except (ValueError, TypeError):
                    pass
            
            # 高成功率加成
            if pref.get("use_count", 0) > 0:
                success_rate = pref["success_count"] / pref["use_count"]
                if success_rate >= config["high_success_rate_threshold"]:
                    boost += config["context_match_boost"]
            
            if boost > 0:
                boosts[expert] = boost
        
        return boosts
    
    def track_combination(self, experts: List[str], rating: int, context: str = "") -> Dict[str, Any]:
        """
        追踪专家组合的效果。
        
        Args:
            experts: 专家列表
            rating: 评分 (1-5)
            context: 上下文信息
            
        Returns:
            组合追踪结果
        """
        if len(experts) < 2:
            return {"tracked": False, "reason": "组合专家数量不足"}
        
        combo_key = "+".join(sorted(experts))
        
        # 获取或创建组合记录
        combinations = self.profile.get("expert_combinations", {})
        combo_data = combinations.get(combo_key, {
            "success_count": 0,
            "total_count": 0,
            "success_rate": 0.0,
            "avg_rating": 0.0,
            "last_success": None,
            "contexts": [],
            "examples": []
        })
        
        # 更新组合数据
        combo_data["total_count"] += 1
        
        if rating >= 4:
            combo_data["success_count"] += 1
            combo_data["last_success"] = datetime.now().isoformat()
            if context and context not in combo_data["contexts"]:
                combo_data["contexts"].append(context)
        
        # 更新平均评分
        total = combo_data["total_count"]
        old_total = total - 1
        combo_data["avg_rating"] = (combo_data["avg_rating"] * old_total + rating) / total
        combo_data["success_rate"] = combo_data["success_count"] / total
        
        # 保存更新
        if "expert_combinations" not in self.profile:
            self.profile["expert_combinations"] = {}
        self.profile["expert_combinations"][combo_key] = combo_data
        
        return {
            "tracked": True,
            "combination": combo_key,
            "total_count": combo_data["total_count"],
            "success_rate": combo_data["success_rate"],
            "avg_rating": combo_data["avg_rating"]
        }
    
    def suggest_best_combination(self, context: str = "", count: int = 3) -> List[Dict[str, Any]]:
        """
        根据历史成功组合，推荐最佳专家组合。
        
        Args:
            context: 当前上下文
            count: 返回的组合数量
            
        Returns:
            最佳组合列表
        """
        combinations = self.profile.get("expert_combinations", {})
        
        if not combinations:
            return []
        
        candidates = []
        
        for combo_key, data in combinations.items():
            # 至少使用过2次
            if data["total_count"] < 2:
                continue
            
            # 成功率至少50%
            if data["success_rate"] < 0.5:
                continue
            
            # 检查上下文匹配
            context_match = False
            if context:
                for stored_context in data.get("contexts", []):
                    if stored_context and context:
                        if stored_context in context or context in stored_context:
                            context_match = True
                            break
            
            score = data["success_rate"] * 100 + data["avg_rating"] * 10
            if context_match:
                score += 30  # 上下文匹配加分
            
            candidates.append({
                "combination": combo_key,
                "experts": combo_key.split("+"),
                "success_rate": data["success_rate"],
                "avg_rating": data["avg_rating"],
                "total_count": data["total_count"],
                "context_match": context_match,
                "score": score
            })
        
        # 按分数排序
        candidates.sort(key=lambda x: x["score"], reverse=True)
        
        return candidates[:count]
    
    def get_routing_recommendation(self, question_type: str, context: str = "") -> Dict[str, Any]:
        """
        获取完整的路由推荐。
        
        Args:
            question_type: 问题类型
            context: 上下文
            
        Returns:
            路由推荐字典
        """
        # 获取调整后的权重
        adjusted_weights = self.adjust_weights(question_type)
        
        # 按权重排序
        sorted_experts = sorted(adjusted_weights.items(), key=lambda x: x[1], reverse=True)
        
        # 获取最佳组合
        best_combinations = self.suggest_best_combination(context)
        
        # 获取该问题类型的偏好专家
        question_patterns = self.profile.get("question_patterns", {})
        preferred_experts = []
        if question_type in question_patterns:
            preferred_experts = question_patterns[question_type].get("preferred_experts", [])
        
        return {
            "question_type": question_type,
            "context": context,
            "adjusted_weights": adjusted_weights,
            "top_experts": sorted_experts[:5],
            "recommended_count": self._recommend_count(question_type),
            "best_combinations": best_combinations,
            "preferred_experts": preferred_experts,
            "reasoning": self._generate_reasoning(question_type, sorted_experts[:3])
        }
    
    def _recommend_count(self, question_type: str) -> int:
        """根据问题类型推荐专家数量。"""
        counts = {
            "职业发展": 4,
            "人生规划": 4,
            "情感关系": 3,
            "创业商业": 5,
            "学术研究": 3,
            "通用问题": 3
        }
        return counts.get(question_type, 3)
    
    def _generate_reasoning(self, question_type: str, top_experts: List[Tuple[str, float]]) -> str:
        """生成推荐理由。"""
        if not top_experts:
            return "基于你的画像，没有找到特别偏好的专家，使用通用配置。"
        
        expert_names = [exp[0] for exp in top_experts]
        avg_weight = sum(exp[1] for exp in top_experts) / len(top_experts)
        
        return (
            f"根据你的历史反馈，为「{question_type}」类型问题推荐 "
            f"{'、'.join(expert_names)}。 "
            f"这些专家在你的历史使用中表现良好（平均权重: {avg_weight:.2f}）。"
        )
    
    def get_missing_experts(self, question_type: str) -> List[str]:
        """
        获取该问题类型可能缺失的专家。
        
        基于：
        1. 该类型默认应该有但用户从未使用过的专家
        2. 被频繁标记为"缺失"的专家
        
        Args:
            question_type: 问题类型
            
        Returns:
            可能缺失的专家列表
        """
        # 获取该类型的默认专家
        default_pool = self.DEFAULT_EXPERT_POOL.get(question_type, {})
        default_people = set(default_pool.get("people", []))
        
        # 获取用户已使用的专家
        expert_prefs = self.profile.get("expert_preferences", {})
        used_experts = set(expert_prefs.keys())
        
        # 找出未使用的默认专家
        missing = list(default_people - used_experts)
        
        # 添加被标记为缺失的专家
        for fb in self.profile.get("feedback_history", []):
            for expert in fb.get("missing_experts", []):
                if expert not in missing:
                    missing.append(expert)
        
        return missing[:5]  # 最多返回5个
    
    def calculate_personal_adjustments(self) -> Dict[str, float]:
        """
        基于反馈历史重新计算个人调整值。
        
        Returns:
            新的个人调整字典
        """
        expert_prefs = self.profile.get("expert_preferences", {})
        adjustments = {}
        
        for expert, pref in expert_prefs.items():
            if pref.get("use_count", 0) >= 3:
                # score 范围 -1 到 1，映射到调整值 -0.3 到 0.3
                score = pref.get("score", 0)
                adjustment = score * 0.3
                adjustments[expert] = adjustment
        
        return adjustments
    
    def get_feedback_summary(self) -> Dict[str, Any]:
        """
        获取反馈摘要（用于调试和分析）。
        
        Returns:
            反馈摘要字典
        """
        expert_prefs = self.profile.get("expert_preferences", {})
        combinations = self.profile.get("expert_combinations", {})
        patterns = self.profile.get("question_patterns", {})
        
        # 找出表现最好和最差的专家
        expert_stats = []
        for expert, pref in expert_prefs.items():
            if pref.get("use_count", 0) > 0:
                success_rate = pref["success_count"] / pref["use_count"]
                expert_stats.append({
                    "expert": expert,
                    "use_count": pref["use_count"],
                    "success_rate": success_rate,
                    "avg_rating": pref.get("avg_rating", 0)
                })
        
        expert_stats.sort(key=lambda x: x["success_rate"], reverse=True)
        
        return {
            "total_experts_tracked": len(expert_prefs),
            "total_combinations_tracked": len(combinations),
            "top_performing_experts": expert_stats[:5],
            "low_performing_experts": expert_stats[-5:] if len(expert_stats) >= 5 else [],
            "question_types_covered": len(patterns),
            "personal_adjustments_count": len(self.calculate_personal_adjustments())
        }
