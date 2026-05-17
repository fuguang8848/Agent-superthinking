# 用户画像数据结构 v1.0

> 定义超级思考系统中用户画像的完整数据结构

---

## 概述

用户画像是超级思考自我优化的核心数据载体，记录用户的历史交互、偏好设置、问题模式等信息。

---

## 完整数据结构

```yaml
# 用户画像 v1.0

## 基本信息
user_id: string              # 用户唯一标识
name: string                 # 用户昵称
created_at: timestamp        # 创建时间
updated_at: timestamp        # 更新时间
version: string              # 画像版本号

## 反馈历史
feedback_history:
  - id: string               # 反馈记录ID
    timestamp: datetime      # 反馈时间
    question: string         # 用户问题
    question_type: string    # 问题类型
    experts_used: [string]   # 使用的专家列表
    experts_from_people: [string]    # 来自"人物"的专家
    experts_from_methods: [string]   # 来自"方法论"的专家
    experts_from_fields: [string]    # 来自"学科"的专家
    rating: int              # 总体评分 (1-5)
    useful_experts: [string] # 有用的专家
    missing_experts: [string] # 缺失的专家
    helpful_score: int       # 对用户的帮助度 (1-5)
    note: string             # 用户备注
    context: string          # 用户提供的背景上下文
    response_time_ms: int    # 响应时间(毫秒)

## 专家偏好
expert_preferences:
  # 格式: expert_name: preference_data
  "苏格拉底":
    score: float             # 偏好分数 (-1 to 1)
    use_count: int           # 使用次数
    success_count: int       # 成功次数
    fail_count: int          # 失败次数
    last_used: datetime      # 上次使用时间
    avg_rating: float        # 平均评分
    contexts: [string]       # 成功的上下文类型
  "尼采":
    score: float
    use_count: int
    success_count: int
    fail_count: int
    last_used: datetime
    avg_rating: float
    contexts: [string]
  # ... 其他专家类似结构

## 问题类型模式
question_patterns:
  "职业发展":
    count: int               # 该类型问题总数
    last_asked: datetime     # 上次提问时间
    preferred_experts: [string]  # 该类型的偏好专家
    avg_rating: float        # 该类型问题平均评分
    examples: [string]       # 问题示例
  "人生规划":
    count: int
    last_asked: datetime
    preferred_experts: [string]
    avg_rating: float
    examples: [string]
  "情感关系":
    count: int
    last_asked: datetime
    preferred_experts: [string]
    avg_rating: float
    examples: [string]
  "创业商业":
    count: int
    last_asked: datetime
    preferred_experts: [string]
    avg_rating: float
    examples: [string]
  "学术研究":
    count: int
    last_asked: datetime
    preferred_experts: [string]
    avg_rating: float
    examples: [string]
  "通用问题":
    count: int
    last_asked: datetime
    preferred_experts: [string]
    avg_rating: float
    examples: [string]

## 专家组合效果
expert_combinations:
  # 组合键: "专家1+专家2+专家3" (排序后)
  "尼采+加缪+苏格拉底":
    success_count: int       # 成功次数
    total_count: int        # 总使用次数
    success_rate: float    # 成功率
    avg_rating: float       # 平均评分
    last_success: datetime  # 上次成功时间
    contexts: [string]      # 成功的上下文类型
    examples: [string]      # 成功案例
  "巴菲特+芒格+孙正义":
    success_count: int
    total_count: int
    success_rate: float
    avg_rating: float
    last_success: datetime
    contexts: [string]
    examples: [string]
  # ... 其他组合

## 路由权重
routing_weights:
  # 默认权重 (问题类型 -> 专家 -> 权重)
  default_weights:
    "职业发展":
      "稻盛和夫": 0.9
      "德鲁克": 0.9
      "乔布斯": 0.8
      "查理芒格": 0.7
    "人生规划":
      "尼采": 0.9
      "加缪": 0.9
      "苏格拉底": 0.8
      "王阳明": 0.7
    "情感关系":
      "佛学视角": 0.9
      "心理学视角": 0.9
      "孔子": 0.7
    "创业商业":
      "巴菲特": 0.9
      "查理芒格": 0.9
      "孙正义": 0.8
      "马斯克": 0.7
    "学术研究":
      "费曼": 0.9
      "西蒙": 0.8
      "学科专家": 0.9
  
  # 基于此用户的个性化调整
  personal_adjustments:
    "尼采": 0.15            # 该用户特别喜欢尼采
    "巴菲特": -0.2          # 该用户对巴菲特不太感兴趣
    # ...
  
  # 动态调整系数
  dynamic_boost:
    recent_success: 0.1     # 最近成功加成
    context_match: 0.2      # 上下文匹配加成
    streak_bonus: 0.05      # 连续使用加成

## 用户背景 (可选)
user_background:
  profession: string       # 职业
  industry: string         # 行业
  education: string        # 教育背景
  interests: [string]      # 兴趣领域
  goals: [string]          # 目标
  values: [string]         # 价值观
  constraints: [string]    # 约束条件

## 统计信息
statistics:
  total_questions: int     # 总问题数
  total_feedback: int      # 总反馈数
  avg_rating_all: float    # 总体平均评分
  most_used_experts: [string]  # 最常用专家 Top 5
  most_successful_type: string # 评分最高的问题类型
  active_days: int         # 活跃天数
  last_active: datetime    # 最后活跃时间
```

---

## 字段说明

### user_id
- 类型: string
- 格式: UUID 或平台用户ID
- 示例: `"user_abc123"` 或 `"wechat_openid_xxx"`

### question_type
- 类型: string
- 枚举值:
  - `职业发展`
  - `人生规划`
  - `情感关系`
  - `创业商业`
  - `学术研究`
  - `通用问题`

### expert_preferences.score
- 类型: float
- 范围: -1.0 to 1.0
- 语义:
  - `1.0`: 强烈偏好，每次都很有用
  - `0.5`: 轻度偏好
  - `0.0`: 无偏好
  - `-0.5`: 轻度不喜欢
  - `-1.0`: 强烈不喜欢，会主动回避

### expert_combinations 组合键
- 格式: 专家名用 `+` 连接，名字按字母排序
- 示例: `"巴菲特+查理芒格+孙正义"`
- 查找时需要统一排序后再查询

---

## 计算公式

### 专家最终权重
```
final_weight(expert, question_type) = 
    default_weights[question_type][expert] 
    + personal_adjustments.get(expert, 0)
    + dynamic_boost(context_match) 
    + dynamic_boost(recent_success)
```

### 组合成功率
```
success_rate(combination) = 
    success_count / total_count (if total_count > 0)
    else 0.0
```

### 推荐分数
```
recommendation_score(expert, user, question_type) =
    base_score * 
    (1 + expert_preferences[expert].score) * 
    (1 + routing_weights.personal_adjustments.get(expert, 0)) *
    context_match_bonus *
    recency_bonus
```

---

## 默认值

```python
DEFAULT_PROFILE = {
    "version": "1.0",
    "created_at": "now",
    "updated_at": "now",
    "feedback_history": [],
    "expert_preferences": {},
    "question_patterns": {
        "职业发展": {"count": 0, "preferred_experts": []},
        "人生规划": {"count": 0, "preferred_experts": []},
        "情感关系": {"count": 0, "preferred_experts": []},
        "创业商业": {"count": 0, "preferred_experts": []},
        "学术研究": {"count": 0, "preferred_experts": []},
        "通用问题": {"count": 0, "preferred_experts": []}
    },
    "expert_combinations": {},
    "routing_weights": {
        "default_weights": {...},
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
```

---

## 存储建议

### 推荐存储格式
- **主存储**: JSON 文件 (便于调试和查看)
- **生产环境**: PostgreSQL JSONB 或 MongoDB
- **缓存**: Redis (热点数据)

### 文件命名
```
{user_id}.json
```

### 存储路径
```
profiles/
├── default.json      # 默认模板
└── users/
    ├── {user_id_1}.json
    ├── {user_id_2}.json
    └── ...
```

---

## 版本迁移

当数据结构需要升级时：

1. 在 `version` 字段标记版本号
2. 添加迁移脚本处理旧版本
3. 保持向后兼容

```python
def migrate_profile(profile: dict) -> dict:
    current_version = profile.get("version", "1.0")
    
    if current_version == "1.0":
        # 迁移 1.0 -> 1.1
        profile = migrate_1_0_to_1_1(profile)
        current_version = "1.1"
    
    # 未来更多迁移...
    
    profile["version"] = current_version
    return profile
```

---

_此文档定义了超级思考系统用户画像的完整数据结构，是实现自我优化系统的基础。_
