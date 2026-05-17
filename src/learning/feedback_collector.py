"""
FeedbackCollector - 多维度反馈收集器

负责收集、分析和结构化用户对分析结果的反馈。
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class FeedbackTemplate:
    """反馈模板定义。"""
    rating: int = 0  # 1-5
    useful_experts: List[str] = None
    missing_experts: List[str] = None
    helpful_score: int = 0  # 1-5
    note: str = ""
    
    def __post_init__(self):
        if self.useful_experts is None:
            self.useful_experts = []
        if self.missing_experts is None:
            self.missing_experts = []


class FeedbackCollector:
    """
    多维度反馈收集器。
    
    提供：
    - 结构化反馈数据收集
    - 反馈验证
    - 反馈模式提取
    - 反馈模板生成
    """
    
    # 标准追问模板
    DEFAULT_PROMPT_TEMPLATE = """
分析完成，请评价：

1. 总体评分（1-5）：___
2. 哪些视角最有帮助？（如：尼采的反抗精神、加缪的荒谬分析）
3. 哪些视角缺失或不够深入？
4. 结合你的背景，回复有帮助吗？（1-5）
5. 其他建议：

你的背景信息：
- 职业/身份：___
- 当前处境：___
- 核心困惑：___
"""
    
    # 问题类型分类关键词
    QUESTION_TYPE_KEYWORDS = {
        "职业发展": ["职业", "工作", "职场", "跳槽", "加薪", "晋升", "面试", "简历", "job", "career"],
        "人生规划": ["人生", "意义", "目标", "规划", "未来", "迷茫", "life", "purpose"],
        "情感关系": ["情感", "恋爱", "分手", "婚姻", "家庭", "朋友", "relationship", "love"],
        "创业商业": ["创业", "商业", "融资", "市场", "产品", "用户", "startup", "business"],
        "学术研究": ["研究", "论文", "学术", "学科", "研究方法", "research", "thesis"]
    }
    
    def __init__(self, prompt_template: Optional[str] = None):
        """
        初始化 FeedbackCollector。
        
        Args:
            prompt_template: 自定义追问模板
        """
        self.prompt_template = prompt_template or self.DEFAULT_PROMPT_TEMPLATE
    
    def get_prompt_template(self) -> str:
        """
        获取追问模板。
        
        Returns:
            追问模板字符串
        """
        return self.prompt_template
    
    def collect(self, analysis_result: Dict[str, Any], user_response: str = "") -> Dict[str, Any]:
        """
        收集用户反馈并结构化。
        
        Args:
            analysis_result: 分析结果（包含使用的专家等信息）
            user_response: 用户对追问的回答
            
        Returns:
            结构化的反馈数据
        """
        if not user_response:
            return self._create_empty_feedback(analysis_result)
        
        # 解析用户回复
        parsed = self._parse_user_response(user_response)
        
        # 构建反馈数据
        feedback = {
            "question": analysis_result.get("question", ""),
            "question_type": analysis_result.get("question_type", "通用问题"),
            "experts_used": analysis_result.get("experts_used", []),
            "experts_from_people": analysis_result.get("experts_from_people", []),
            "experts_from_methods": analysis_result.get("experts_from_methods", []),
            "experts_from_fields": analysis_result.get("experts_from_fields", []),
            "rating": parsed.get("rating", 0),
            "useful_experts": parsed.get("useful_experts", []),
            "missing_experts": parsed.get("missing_experts", []),
            "helpful_score": parsed.get("helpful_score", 0),
            "note": parsed.get("note", ""),
            "context": parsed.get("context", ""),
            "timestamp": datetime.now().isoformat()
        }
        
        return feedback
    
    def _parse_user_response(self, response: str) -> Dict[str, Any]:
        """
        解析用户回复，提取反馈信息。
        
        支持多种格式：
        - 结构化回答（带序号）
        - 自然语言回答
        
        Args:
            response: 用户回复文本
            
        Returns:
            解析后的反馈字典
        """
        result = {
            "rating": 0,
            "useful_experts": [],
            "missing_experts": [],
            "helpful_score": 0,
            "note": "",
            "context": ""
        }
        
        lines = response.strip().split("\n")
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 解析总体评分
            if any(x in line.lower() for x in ["1.", "总体评分", "总体", "评分"]):
                result["rating"] = self._extract_rating(line)
            
            # 解析有帮助的专家
            elif any(x in line.lower() for x in ["2.", "有帮助", "有用", "视角"]):
                result["useful_experts"] = self._extract_experts(line)
            
            # 解析缺失的专家
            elif any(x in line.lower() for x in ["3.", "缺失", "不够", "缺少"]):
                result["missing_experts"] = self._extract_experts(line)
            
            # 解析帮助度评分
            elif any(x in line.lower() for x in ["4.", "帮助度", "背景"]):
                result["helpful_score"] = self._extract_rating(line)
                # 同时提取上下文
                result["context"] = self._extract_context(line)
            
            # 解析其他建议
            elif any(x in line.lower() for x in ["5.", "建议", "其他"]):
                result["note"] = line.split(":", 1)[-1].strip() if ":" in line else line
            
            # 解析背景信息
            elif any(x in line for x in ["职业", "身份", "处境", "困惑"]):
                result["context"] = self._extract_context(line)
        
        # 如果解析失败，使用默认策略
        if result["rating"] == 0:
            # 尝试从整体情感判断
            if any(x in response.lower() for x in ["很有帮助", "非常好", "太棒了", "很有启发"]):
                result["rating"] = 5
            elif any(x in response.lower() for x in ["有帮助", "不错", "挺好"]):
                result["rating"] = 4
            elif any(x in response.lower() for x in ["一般", "普通"]):
                result["rating"] = 3
            elif any(x in response.lower() for x in ["帮助不大", "不太有用"]):
                result["rating"] = 2
            elif any(x in response.lower() for x in ["没用", "很差", "不满意"]):
                result["rating"] = 1
        
        return result
    
    def _extract_rating(self, text: str) -> int:
        """从文本中提取评分。"""
        import re
        
        # 尝试匹配数字
        numbers = re.findall(r'\d+', text)
        for num in numbers:
            rating = int(num)
            if 1 <= rating <= 5:
                return rating
        
        # 尝试匹配中文数字
        chinese_map = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5}
        for char, num in chinese_map.items():
            if char in text:
                return num
        
        return 0
    
    def _extract_experts(self, text: str) -> List[str]:
        """从文本中提取专家名称列表。"""
        experts = []
        
        # 常见专家关键词
        known_experts = [
            # 哲学/思想家
            "尼采", "加缪", "苏格拉底", "柏拉图", "亚里士多德", "康德", "黑格尔",
            "老子", "孔子", "孟子", "庄子", "王阳明", "佛学", "释迦牟尼",
            # 商业/投资
            "巴菲特", "芒格", "查理芒格", "孙正义", "马斯克", "乔布斯", "贝索斯",
            "马云", "张一鸣", "马化腾", "刘强东",
            # 管理学
            "德鲁克", "稻盛和夫", "杰克韦尔奇", "彼得圣吉",
            # 心理学
            "弗洛伊德", "荣格", "马斯洛", "卡尼曼", "心理学",
            # 科学/方法论
            "费曼", "西蒙", "爱因斯坦", "牛顿", "达尔文",
            # 其他
            "马克思", "毛泽东", "邓小平"
        ]
        
        for expert in known_experts:
            if expert in text:
                experts.append(expert)
        
        return list(set(experts))
    
    def _extract_context(self, text: str) -> str:
        """从文本中提取上下文信息。"""
        context_parts = []
        
        # 提取职业/身份
        if "职业" in text and ":" in text:
            parts = text.split("职业", 1)[-1]
            if ":" in parts:
                context_parts.append(parts.split(":", 1)[-1].strip())
            else:
                context_parts.append(parts.strip())
        
        # 提取处境
        if "处境" in text and ":" in text:
            parts = text.split("处境", 1)[-1]
            if ":" in parts:
                context_parts.append(parts.split(":", 1)[-1].strip())
        
        # 提取困惑
        if "困惑" in text and ":" in text:
            parts = text.split("困惑", 1)[-1]
            if ":" in parts:
                context_parts.append(parts.split(":", 1)[-1].strip())
        
        return "；".join(context_parts)
    
    def _create_empty_feedback(self, analysis_result: Dict) -> Dict[str, Any]:
        """创建空的反馈数据（用户未提供反馈时）。"""
        return {
            "question": analysis_result.get("question", ""),
            "question_type": analysis_result.get("question_type", "通用问题"),
            "experts_used": analysis_result.get("experts_used", []),
            "experts_from_people": analysis_result.get("experts_from_people", []),
            "experts_from_methods": analysis_result.get("experts_from_methods", []),
            "experts_from_fields": analysis_result.get("experts_from_fields", []),
            "rating": 0,
            "useful_experts": [],
            "missing_experts": [],
            "helpful_score": 0,
            "note": "",
            "context": "",
            "timestamp": datetime.now().isoformat()
        }
    
    def validate(self, feedback: Dict) -> bool:
        """
        验证反馈数据完整性。
        
        Args:
            feedback: 反馈数据
            
        Returns:
            是否有效
        """
        required_fields = ["question", "question_type", "experts_used"]
        
        for field in required_fields:
            if field not in feedback:
                return False
        
        # rating 应该在 0-5 之间
        rating = feedback.get("rating", 0)
        if not (0 <= rating <= 5):
            return False
        
        return True
    
    def extract_patterns(self, feedback_list: List[Dict]) -> Dict[str, Any]:
        """
        从多个反馈中提取模式。
        
        Args:
            feedback_list: 反馈列表
            
        Returns:
            模式分析结果
        """
        if not feedback_list:
            return {}
        
        # 统计专家效果
        expert_stats = {}
        for fb in feedback_list:
            for expert in fb.get("useful_experts", []):
                if expert not in expert_stats:
                    expert_stats[expert] = {"useful": 0, "missing": 0, "total": 0}
                expert_stats[expert]["useful"] += 1
                expert_stats[expert]["total"] += 1
            
            for expert in fb.get("missing_experts", []):
                if expert not in expert_stats:
                    expert_stats[expert] = {"useful": 0, "missing": 0, "total": 0}
                expert_stats[expert]["missing"] += 1
                expert_stats[expert]["total"] += 1
        
        # 统计问题类型
        type_stats = {}
        for fb in feedback_list:
            qtype = fb.get("question_type", "通用问题")
            if qtype not in type_stats:
                type_stats[qtype] = {"count": 0, "total_rating": 0, "avg_rating": 0}
            type_stats[qtype]["count"] += 1
            type_stats[qtype]["total_rating"] += fb.get("rating", 0)
        
        for qtype, stats in type_stats.items():
            if stats["count"] > 0:
                stats["avg_rating"] = stats["total_rating"] / stats["count"]
        
        # 找出最佳专家组合
        combination_success = {}
        for fb in feedback_list:
            experts = fb.get("experts_used", [])
            if len(experts) >= 2:
                combo_key = "+".join(sorted(experts))
                rating = fb.get("rating", 0)
                if combo_key not in combination_success:
                    combination_success[combo_key] = {"total_rating": 0, "count": 0, "avg_rating": 0}
                combination_success[combo_key]["total_rating"] += rating
                combination_success[combo_key]["count"] += 1
        
        for combo, stats in combination_success.items():
            if stats["count"] > 0:
                stats["avg_rating"] = stats["total_rating"] / stats["count"]
        
        # 按平均评分排序组合
        sorted_combinations = sorted(
            combination_success.items(),
            key=lambda x: x[1]["avg_rating"],
            reverse=True
        )[:5]
        
        return {
            "expert_effectiveness": dict(sorted(
                expert_stats.items(),
                key=lambda x: x[1]["useful"] - x[1]["missing"],
                reverse=True
            )),
            "question_type_stats": type_stats,
            "best_combinations": sorted_combinations,
            "total_feedbacks": len(feedback_list)
        }
    
    def generate_improvement_suggestions(self, patterns: Dict) -> List[str]:
        """
        基于模式分析生成改进建议。
        
        Args:
            patterns: 模式分析结果
            
        Returns:
            改进建议列表
        """
        suggestions = []
        
        # 分析专家效果
        expert_effect = patterns.get("expert_effectiveness", {})
        for expert, stats in expert_effect.items():
            if stats["missing"] > stats["useful"] * 0.5:
                suggestions.append(
                    f"专家「{expert}」被频繁标记为缺失，建议在相关问题类型中增加该专家的权重"
                )
        
        # 分析问题类型
        type_stats = patterns.get("question_type_stats", {})
        for qtype, stats in type_stats.items():
            if stats["avg_rating"] < 3 and stats["count"] >= 3:
                suggestions.append(
                    f"问题类型「{qtype}」的平均评分较低({stats['avg_rating']:.1f})，"
                    f"建议调整该类型的专家配置"
                )
        
        # 分析组合
        best_combos = patterns.get("best_combinations", [])
        if best_combos:
            top_combo = best_combos[0]
            suggestions.append(
                f"最佳专家组合：{top_combo[0]}（平均评分 {top_combo[1]['avg_rating']:.1f}）"
            )
        
        return suggestions


# 便捷函数
def quick_feedback(analysis_result: Dict, user_input: str) -> Dict:
    """
    快速收集反馈的便捷函数。
    
    Args:
        analysis_result: 分析结果
        user_input: 用户输入
        
    Returns:
        结构化反馈
    """
    collector = FeedbackCollector()
    return collector.collect(analysis_result, user_input)
