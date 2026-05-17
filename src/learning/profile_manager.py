"""
ProfileManager - 用户画像管理器

负责用户画像的 CRUD 操作，以及基于画像的推荐生成。
"""

from pathlib import Path
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, List, Any


class ProfileManager:
    """
    管理用户画像的核心类。
    
    提供：
    - 画像的创建、读取、更新
    - 基于画像的专家推荐
    - 画像数据的持久化
    """
    
    # 默认画像模板
    DEFAULT_TEMPLATE = {
        "version": "1.0",
        "created_at": None,
        "updated_at": None,
        "feedback_history": [],
        "expert_preferences": {},
        "question_patterns": {
            "职业发展": {"count": 0, "preferred_experts": [], "avg_rating": 0.0},
            "人生规划": {"count": 0, "preferred_experts": [], "avg_rating": 0.0},
            "情感关系": {"count": 0, "preferred_experts": [], "avg_rating": 0.0},
            "创业商业": {"count": 0, "preferred_experts": [], "avg_rating": 0.0},
            "学术研究": {"count": 0, "preferred_experts": [], "avg_rating": 0.0},
            "通用问题": {"count": 0, "preferred_experts": [], "avg_rating": 0.0}
        },
        "expert_combinations": {},
        "routing_weights": {
            "default_weights": {
                "职业发展": {"稻盛和夫": 0.9, "德鲁克": 0.9, "乔布斯": 0.8, "查理芒格": 0.7},
                "人生规划": {"尼采": 0.9, "加缪": 0.9, "苏格拉底": 0.8, "王阳明": 0.7},
                "情感关系": {"佛学视角": 0.9, "心理学视角": 0.9, "孔子": 0.7},
                "创业商业": {"巴菲特": 0.9, "查理芒格": 0.9, "孙正义": 0.8, "马斯克": 0.7},
                "学术研究": {"费曼": 0.9, "西蒙": 0.8, "学科专家": 0.9}
            },
            "personal_adjustments": {},
            "dynamic_boost": {
                "recent_success": 0.1,
                "context_match": 0.2,
                "streak_bonus": 0.05
            }
        },
        "user_background": {},
        "statistics": {
            "total_questions": 0,
            "total_feedback": 0,
            "avg_rating_all": 0.0,
            "most_used_experts": [],
            "most_successful_type": None,
            "active_days": 0,
            "last_active": None
        }
    }
    
    # 问题类型关键词映射
    QUESTION_TYPE_KEYWORDS = {
        "职业发展": ["职业", "工作", "职场", "跳槽", "加薪", "晋升", "面试", "简历", "job", "career"],
        "人生规划": ["人生", "意义", "目标", "规划", "未来", "迷茫", "life", "purpose"],
        "情感关系": ["情感", "恋爱", "分手", "婚姻", "家庭", "朋友", "relationship", "love"],
        "创业商业": ["创业", "商业", "融资", "市场", "产品", "用户", "startup", "business"],
        "学术研究": ["研究", "论文", "学术", "学科", "研究方法", "research", "thesis"]
    }
    
    def __init__(self, profile_dir: str = "profiles/"):
        """
        初始化 ProfileManager。
        
        Args:
            profile_dir: 画像存储目录路径
        """
        self.profile_dir = Path(profile_dir)
        self.profile_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_profile_path(self, user_id: str) -> Path:
        """获取用户画像文件路径。"""
        return self.profile_dir / f"{user_id}.json"
    
    def _create_default_profile(self, user_id: str) -> Dict:
        """创建默认画像。"""
        profile = {
            "user_id": user_id,
            **self.DEFAULT_TEMPLATE.copy()
        }
        profile["created_at"] = datetime.now().isoformat()
        profile["updated_at"] = datetime.now().isoformat()
        return profile
    
    def get_profile(self, user_id: str) -> Dict:
        """
        获取用户画像，如果不存在则创建新的。
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户画像字典
        """
        path = self._get_profile_path(user_id)
        if path.exists():
            try:
                profile = json.loads(path.read_text(encoding="utf-8"))
                return profile
            except (json.JSONDecodeError, IOError):
                # 文件损坏，创建新画像
                return self._create_default_profile(user_id)
        return self._create_default_profile(user_id)
    
    def _save_profile(self, user_id: str, profile: Dict) -> None:
        """保存用户画像到磁盘。"""
        profile["updated_at"] = datetime.now().isoformat()
        path = self._get_profile_path(user_id)
        path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
    
    def create_profile(self, user_id: str, name: Optional[str] = None) -> Dict:
        """
        创建新用户画像。
        
        Args:
            user_id: 用户ID
            name: 用户名称（可选）
            
        Returns:
            创建的画像字典
        """
        profile = self._create_default_profile(user_id)
        if name:
            profile["name"] = name
        self._save_profile(user_id, profile)
        return profile
    
    def update_profile(self, user_id: str, feedback: Dict) -> Dict:
        """
        使用反馈更新用户画像。
        
        Args:
            user_id: 用户ID
            feedback: 反馈数据字典
            
        Returns:
            更新后的画像
        """
        profile = self.get_profile(user_id)
        
        # 1. 添加到反馈历史
        feedback_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            **feedback
        }
        profile["feedback_history"].append(feedback_entry)
        
        # 2. 更新专家偏好
        self._update_expert_preferences(profile, feedback)
        
        # 3. 更新问题模式
        self._update_question_patterns(profile, feedback)
        
        # 4. 更新专家组合
        self._update_expert_combinations(profile, feedback)
        
        # 5. 更新统计信息
        self._update_statistics(profile, feedback)
        
        # 6. 重新计算路由权重
        self._recalculate_routing_weights(profile)
        
        self._save_profile(user_id, profile)
        return profile
    
    def _update_expert_preferences(self, profile: Dict, feedback: Dict) -> None:
        """更新专家偏好。"""
        useful_experts = feedback.get("useful_experts", [])
        missing_experts = feedback.get("missing_experts", [])
        rating = feedback.get("rating", 3)
        
        all_experts = useful_experts + missing_experts
        
        for expert in all_experts:
            if expert not in profile["expert_preferences"]:
                profile["expert_preferences"][expert] = {
                    "score": 0.0,
                    "use_count": 0,
                    "success_count": 0,
                    "fail_count": 0,
                    "last_used": None,
                    "avg_rating": 0.0,
                    "contexts": []
                }
            
            pref = profile["expert_preferences"][expert]
            pref["use_count"] += 1
            pref["last_used"] = datetime.now().isoformat()
            
            if expert in useful_experts:
                pref["success_count"] += 1
                pref["score"] = min(1.0, pref["score"] + 0.1)  # 增加偏好
                context = feedback.get("context", "")
                if context and context not in pref["contexts"]:
                    pref["contexts"].append(context)
            else:
                pref["fail_count"] += 1
                pref["score"] = max(-1.0, pref["score"] - 0.15)  # 降低偏好
            
            # 更新平均评分
            total = pref["success_count"] + pref["fail_count"]
            pref["avg_rating"] = (pref["avg_rating"] * (total - 1) + rating) / total
    
    def _update_question_patterns(self, profile: Dict, feedback: Dict) -> None:
        """更新问题模式。"""
        question_type = feedback.get("question_type", "通用问题")
        rating = feedback.get("rating", 3)
        
        if question_type in profile["question_patterns"]:
            pattern = profile["question_patterns"][question_type]
            pattern["count"] += 1
            
            # 更新平均评分
            old_total = pattern["count"] - 1
            if old_total > 0:
                pattern["avg_rating"] = (pattern["avg_rating"] * old_total + rating) / pattern["count"]
            else:
                pattern["avg_rating"] = rating
            
            # 如果这次效果好，更新偏好专家
            if rating >= 4:
                experts = feedback.get("experts_used", [])
                for expert in experts:
                    if expert not in pattern["preferred_experts"]:
                        pattern["preferred_experts"].append(expert)
    
    def _update_expert_combinations(self, profile: Dict, feedback: Dict) -> None:
        """更新专家组合效果。"""
        experts = feedback.get("experts_used", [])
        if len(experts) < 2:
            return
        
        # 生成组合键（排序后用+连接）
        combo_key = "+".join(sorted(experts))
        rating = feedback.get("rating", 3)
        context = feedback.get("context", "")
        
        if combo_key not in profile["expert_combinations"]:
            profile["expert_combinations"][combo_key] = {
                "success_count": 0,
                "total_count": 0,
                "success_rate": 0.0,
                "avg_rating": 0.0,
                "last_success": None,
                "contexts": [],
                "examples": []
            }
        
        combo = profile["expert_combinations"][combo_key]
        combo["total_count"] += 1
        
        if rating >= 4:
            combo["success_count"] += 1
            combo["last_success"] = datetime.now().isoformat()
            if context and context not in combo["contexts"]:
                combo["contexts"].append(context)
        
        combo["success_rate"] = combo["success_count"] / combo["total_count"]
        combo["avg_rating"] = (combo["avg_rating"] * (combo["total_count"] - 1) + rating) / combo["total_count"]
    
    def _update_statistics(self, profile: Dict, feedback: Dict) -> None:
        """更新统计信息。"""
        stats = profile["statistics"]
        stats["total_questions"] += 1
        stats["total_feedback"] += 1
        stats["last_active"] = datetime.now().isoformat()
        
        # 更新总体平均评分
        old_total = stats["total_feedback"] - 1
        rating = feedback.get("rating", 3)
        if old_total > 0:
            stats["avg_rating_all"] = (stats["avg_rating_all"] * old_total + rating) / stats["total_feedback"]
        else:
            stats["avg_rating_all"] = rating
        
        # 更新最常用专家
        experts = feedback.get("experts_used", [])
        current_most = stats["most_used_experts"]
        for expert in experts:
            if expert not in current_most:
                current_most.append(expert)
        # 保留使用次数最多的前5个
        expert_counts = {}
        for fb in profile["feedback_history"]:
            for exp in fb.get("experts_used", []):
                expert_counts[exp] = expert_counts.get(exp, 0) + 1
        stats["most_used_experts"] = sorted(expert_counts.keys(), key=lambda x: expert_counts[x], reverse=True)[:5]
        
        # 更新评分最高的问题类型
        best_type = None
        best_rating = 0.0
        for qtype, pattern in profile["question_patterns"].items():
            if pattern["count"] > 0 and pattern["avg_rating"] > best_rating:
                best_rating = pattern["avg_rating"]
                best_type = qtype
        stats["most_successful_type"] = best_type
    
    def _recalculate_routing_weights(self, profile: Dict) -> None:
        """重新计算路由权重（基于反馈调整个人偏好）。"""
        personal = profile["routing_weights"]["personal_adjustments"]
        
        for expert, pref in profile["expert_preferences"].items():
            if pref["use_count"] >= 3:  # 至少使用3次才有参考价值
                # score 从 -1 到 1，映射到调整值 -0.3 到 0.3
                adjustment = pref["score"] * 0.3
                personal[expert] = adjustment
    
    def classify_question(self, question: str) -> str:
        """
        根据问题内容分类问题类型。
        
        Args:
            question: 用户问题
            
        Returns:
            问题类型字符串
        """
        question_lower = question.lower()
        
        for qtype, keywords in self.QUESTION_TYPE_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in question_lower:
                    return qtype
        
        return "通用问题"
    
    def get_recommendations(self, user_id: str, question: str) -> Dict[str, Any]:
        """
        基于用户画像和问题内容，生成专家推荐。
        
        Args:
            user_id: 用户ID
            question: 用户问题
            
        Returns:
            包含推荐专家和权重信息的字典
        """
        profile = self.get_profile(user_id)
        question_type = self.classify_question(question)
        
        # 获取该问题类型的默认权重
        default_weights = profile["routing_weights"]["default_weights"].get(question_type, {})
        personal_adj = profile["routing_weights"]["personal_adjustments"]
        dynamic_boost = profile["routing_weights"]["dynamic_boost"]
        
        # 计算最终权重
        recommendations = {}
        
        for expert, base_weight in default_weights.items():
            # 基础权重
            weight = base_weight
            
            # 应用个人调整
            if expert in personal_adj:
                weight += personal_adj[expert]
            
            # 应用动态加成
            if expert in profile["expert_preferences"]:
                pref = profile["expert_preferences"][expert]
                # 最近成功加成
                if pref.get("last_used"):
                    last_used = datetime.fromisoformat(pref["last_used"])
                    days_since = (datetime.now() - last_used).days
                    if days_since <= 7:
                        weight += dynamic_boost["recent_success"]
                
                # 成功率加成
                if pref["use_count"] > 0:
                    success_rate = pref["success_count"] / pref["use_count"]
                    if success_rate >= 0.8:
                        weight += dynamic_boost["context_match"]
            
            recommendations[expert] = round(weight, 3)
        
        # 如果问题有上下文，检查是否有成功组合
        context_matches = self._find_similar_context_combinations(profile, question)
        
        return {
            "question_type": question_type,
            "question": question,
            "experts": recommendations,
            "top_experts": sorted(recommendations.items(), key=lambda x: x[1], reverse=True)[:5],
            "context_matches": context_matches,
            "profile_stats": {
                "total_questions": profile["statistics"]["total_questions"],
                "avg_rating": profile["statistics"]["avg_rating_all"],
                "most_used": profile["statistics"]["most_used_experts"][:3]
            }
        }
    
    def _find_similar_context_combinations(self, profile: Dict, context: str) -> List[Dict]:
        """查找上下文中类似的成功专家组合。"""
        matches = []
        
        for combo_key, combo_data in profile["expert_combinations"].items():
            if combo_data["success_rate"] >= 0.7 and combo_data["total_count"] >= 2:
                for stored_context in combo_data.get("contexts", []):
                    if stored_context and context and (
                        stored_context in context or context in stored_context
                    ):
                        matches.append({
                            "combination": combo_key,
                            "success_rate": combo_data["success_rate"],
                            "avg_rating": combo_data["avg_rating"]
                        })
                        break
        
        return sorted(matches, key=lambda x: x["success_rate"], reverse=True)[:3]
    
    def delete_profile(self, user_id: str) -> bool:
        """
        删除用户画像。
        
        Args:
            user_id: 用户ID
            
        Returns:
            是否删除成功
        """
        path = self._get_profile_path(user_id)
        if path.exists():
            path.unlink()
            return True
        return False
    
    def list_profiles(self) -> List[str]:
        """
        列出所有用户画像ID。
        
        Returns:
            用户ID列表
        """
        return [p.stem for p in self.profile_dir.glob("*.json")]
    
    def get_statistics_summary(self, user_id: str) -> Dict:
        """
        获取用户统计摘要。
        
        Args:
            user_id: 用户ID
            
        Returns:
            统计摘要字典
        """
        profile = self.get_profile(user_id)
        stats = profile["statistics"]
        
        # 计算活跃天数
        active_days = set()
        for fb in profile["feedback_history"]:
            if "timestamp" in fb:
                dt = datetime.fromisoformat(fb["timestamp"])
                active_days.add(dt.date())
        
        return {
            "total_questions": stats["total_questions"],
            "total_feedback": stats["total_feedback"],
            "avg_rating": round(stats["avg_rating_all"], 2),
            "active_days": len(active_days),
            "most_used_experts": stats["most_used_experts"],
            "most_successful_type": stats["most_successful_type"],
            "expert_count": len(profile["expert_preferences"]),
            "combination_count": len(profile["expert_combinations"])
        }
