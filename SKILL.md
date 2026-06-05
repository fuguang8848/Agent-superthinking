---
name: ce:superthinking
description: |
  多维度思考框架 v5。具备自我优化能力的AI思考系统。问题 → 读取用户画像 → 智能路由 → 追问 → 分析 → 多维反馈 → 画像更新 → 下次更精准。
  触发词：思考、分析、深度分析、多视角、多维分析
  适用场景：复杂问题、重大决策、风险评估、创意突破、人生困惑
---

# ⚔️ 超思考 · 自优化专家系统 v5

> 不同领域的思想家看待同一个问题，结论往往不同——这种差异本身就是洞察的来源。

## 核心架构：反馈闭环

```
问题输入
    ↓
┌─────────────────────────────────────────┐
│  学习层（Learning Layer）               │
│                                         │
│  Step 1: 读取用户画像                  │
│  Step 2: 基于画像 + 初步路由           │
│  Step 3: 智能推荐（画像权重调整）     │
│  Step 4: 追问获取上下文                │
└─────────────────────────────────────────┘
    ↓
用户选择轨别和粒度
    ↓
激活专家并行分析
    ↓
综合报告
    ↓
┌─────────────────────────────────────────┐
│  反馈层（Feedback Layer）                 │
│                                         │
│  Step 5: 多维反馈收集                  │
│  Step 6: 画像更新                      │
│  Step 7: 组合效果追踪                  │
└─────────────────────────────────────────┘
    ↓
下次路由时读取更新后的画像 → 更精准的推荐
```

**v5 核心升级：**
- **反馈闭环**：用户评价 → 画像更新 → 下次推荐更准
- **用户画像**：记忆偏好、问题模式、专家组合效果
- **智能推荐**：基于画像动态调整专家权重
- **自优化**：系统从每次交互中学习

---

## 用户画像（Profile）

### 数据结构

```yaml
user_profile:
  # 基础信息
  user_id: "youyou"
  name: "优优"
  created_at: "2026-05-17"
  updated_at: "2026-05-17T11:24:00Z"
  
  # 反馈历史
  feedback_history:
    - timestamp: "2026-05-17T11:24:00Z"
      question: "人生的意义是什么"
      question_type: "人生困惑"
      experts_used: ["尼采", "加缪", "萨特", "庄子", "佛陀"]
      rating: 4
      useful_experts: ["尼采", "加缪"]
      missing_experts: []
      context: "30岁，感觉定型了"
      
  # 专家偏好
  expert_preferences:
    尼采:
      score: 0.8      # -1到1，0.8=很喜欢
      use_count: 5
      success_count: 4
    佛陀:
      score: -0.2    # 负数=不太喜欢
      use_count: 2
      success_count: 1
      
  # 问题类型模式
  question_patterns:
    - pattern: "人生困惑"
      keywords: ["意义", "人生", "活着的目的"]
      preferred_experts: ["尼采", "加缪", "萨特"]
      count: 3
        
    - pattern: "职业选择"
      keywords: ["工作", "跳槽", "转行", "职业"]
      preferred_experts: ["芒格", "纳瓦尔", "马斯克"]
      count: 2
      
  # 专家组合效果
  expert_combinations:
    - experts: ["尼采", "加缪", "萨特"]
      success_rate: 0.85
      total_count: 4
      best_contexts: ["30岁危机", "意义困惑"]
      
    - experts: ["芒格", "纳瓦尔"]
      success_rate: 0.9
      total_count: 5
      best_contexts: ["创业决策", "职业选择"]
```

### 画像更新逻辑

```
收到反馈 → 提取关键词 → 更新对应字段

评分 ≥ 4:
  → 专家分数 +0.1
  → 组合成功率 +0.05
  → 问题模式 count +1

评分 ≤ 2:
  → 专家分数 -0.2
  → 组合成功率 -0.1
  → 触发追问："你觉得哪个视角不对？"
```

---

## 完整流程

### Step 1: 读取用户画像

读取该用户的 profile（首次为空则创建默认）

### Step 2: 初步路由 + 画像调整

```
问题："30岁要不要跳槽"

初步路由：哲学团、战略决策团、博弈论

画像调整：
- 用户过去职业类问题偏好：芒格(+0.3)、纳瓦尔(+0.3)
- 芒格历史成功率：0.9 → 提升推荐权重
- 佛陀历史评分：-0.2 → 降低推荐权重

调整后推荐：
优先级1：战略决策团（芒格、纳瓦尔、马斯克）
优先级2：哲学团（尼采、萨特）
优先级3：博弈论
```

### Step 3: 展示路由结果 + 追问

```
┌─────────────────────────────────────────────────┐
│  基于你的画像，推荐如下：                         │
│                                                 │
│  问题类型：职业选择                              │
│  涉及专家团：战略决策团（强推荐）、哲学团        │
│                                                 │
│  画像提示：                                      │
│  - 你之前职业问题用芒格/纳瓦尔效果很好（90%成功率）│
│  - 哲学团在人生困惑类问题表现好                  │
│                                                 │
│  请选择轨别：                                    │
│  [1] 战略决策团（推荐）                         │
│  [2] 双轨组合（战略+哲学）                       │
│  [3] 自定义                                    │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  补充背景：                                      │
│                                                 │
│  1. 你是想离开现有工作，还是有更好的机会？        │
│  2. 跳槽最让你纠结的是什么？                      │
│                                                 │
│  [直接输入背景，或跳过]                           │
└─────────────────────────────────────────────────┘
```

### Step 4: 用户选择 + 回答背景

### Step 5: 专家分析

### Step 6: 多维反馈收集

```
┌─────────────────────────────────────────────────┐
│  分析完成！请帮助改进：                          │
│                                                 │
│  1. 总体评分（1-5）：___                        │
│                                                 │
│  2. 哪些视角最有帮助？                           │
│     （如：芒格的激励分析、纳瓦尔的杠杆思维）     │
│                                                 │
│  3. 哪些视角缺失或不够深入？                     │
│                                                 │
│  4. 这次分析结合你的背景了吗？                   │
│     （1=完全没用，5=非常精准）___                │
│                                                 │
│  5. 其他建议：                                  │
└─────────────────────────────────────────────────┘
```

### Step 7: 画像更新

收到反馈后：
1. 解析评分 → 更新各专家分数
2. 记录有用/缺失专家 → 更新偏好
3. 记录组合 → 更新成功率
4. 记录问题关键词 → 更新问题模式

---

## 自优化机制

### 组合效果追踪

每次分析记录使用的专家组合 + 评分：
```
["芒格", "纳瓦尔"] + 用户评分5 → 成功率 0.9
["尼采", "佛陀"] + 用户评分2 → 成功率 0.3
```

下次遇到类似上下文，优先推荐成功率高的组合。

### 专家动态权重

```
权重计算：
final_weight = base_weight × context_modifier × profile_modifier

base_weight:      基础权重（问题匹配度）
context_modifier: 上下文调整（"30岁"→ 人生/职业权重↑）
profile_modifier: 画像调整（用户历史评分）
```

### 问题模式学习

用户反复问某类问题 → 系统学习该类问题的最佳专家组合

---

## 与旧版区别

| 维度 | v4 | v5 |
|------|-----|-----|
| 用户画像 | 无 | 有，记录偏好 |
| 反馈闭环 | 无 | 有，画像自动更新 |
| 智能推荐 | 基于问题 | 基于问题+画像 |
| 自优化 | 无 | 有，组合效果追踪 |
| 推荐精准度 | 60% | 预期85%+ |

---

## 目录结构

```
Agent-superthinking/
├── SKILL.md                    # 本文件
├── LEARNING.md                 # 自优化系统架构
├── PROFILE_SCHEMA.md          # 用户画像数据结构
├── INDEX_PEOPLE.md
├── INDEX_METHODS.md
├── SCHEMA.md
├── README.md
├── LICENSE
├── profiles/                   # 用户画像存储
│   └── youyou.json           # 示例用户画像
├── src/
│   └── super_thinking/
│       ├── __init__.py
│       ├── core/
│       │   ├── router.py
│       │   └── jury.py
│       ├── learning/        # ← 新增自优化模块
│       │   ├── __init__.py
│       │   ├── profile_manager.py
│       │   ├── feedback_collector.py
│       │   └── routing_optimizer.py
│       └── fusion/
│           ├── conflict.py
│           ├── consensus.py
│           └── formatter.py
└── experts/
    ├── people/
    └── methods/
```

---

## 质量门禁

1. **反馈是否被收集**：分析后必须触发反馈收集
2. **画像是否更新**：收到反馈后必须更新 profile
3. **下次推荐是否参考画像**：路由时必须读取并应用画像权重
4. **隐私保护**：profile 只存储偏好数据，不存储敏感内容

---

## ⚠️ v6 内测版：ContextBoard 专家协作机制

> **内测版本 · 实验性功能 · 不暴露给普通用户**

### 概述

ContextBoard 是 v6 的核心新特性，提供专家间的共享状态板。各专家不是独立输出，而是在共享的 ContextBoard 上发布状态和中间结论，其他专家可以读到这些结论来深化自己的分析。

### 核心概念

```
专家协作阶段：
  THINKING   → 专家正在积极分析
  REVIEWING  → 专家正在审视其他专家的结论
  WAITING   → 专家等待其他专家的结论
  CONCLUDED → 专家已发布最终结论
```

### 数据结构

```python
from super_thinking.team import ContextBoard, TeamIntegration

board = ContextBoard()  # 共享状态板

# 注册专家（指定层）
board.register("buffett", layer=0)   # 第0层：先执行
board.register("morgan", layer=1)    # 第1层：可读到第0层结论
board.register("dalio", layer=1)

# 发布中间结论
board.publish_insight("buffett", "市场风险：X", ExpertStatus.REVIEWING)

# 完成后标记
board.publish_concluded("buffett", "最终结论：分散投资")

# 第1层专家读取第0层结论
insights = board.get_visible_insights("morgan")
# → {"buffett": "最终结论：分散投资"}
```

### TeamIntegration 封装

```python
from super_thinking.team import TeamIntegration

integration = TeamIntegration(board)

# 注册专家
integration.register_expert("buffett", layer=0)
integration.register_expert("dalio", layer=1)

# 发布结论
integration.publish_insight("buffett", "风险评估：...", ExpertStatus.REVIEWING)
integration.publish_concluded("buffett", "最终结论：...")

# 获取其他专家的结论
insights = integration.get_insights_for("dalio")

# 查询状态
integration.is_concluded("buffett")  # True
integration.all_concluded()           # False if others pending
```

### Jury 集成：`think_with_board()`

```python
from super_thinking.core.jury import Jury
from super_thinking.team import ContextBoard

jury = Jury()
board = ContextBoard()

# 定义专家层级
layers = {
    "meta_thinking": 0,   # 第0层：先执行
    "risk_detail": 0,
    "buffett": 1,         # 第1层：可读到第0层结论
    "morgan": 1,
}

result = jury.think_with_board(
    input="Should I invest in Tesla?",
    execution_layers=layers,  # 可选，默认全在第0层
    board=board,
    mode="llm",              # 或 "auto", "force_all"
)

# 分析结果
for output in result.get_outputs():
    print(f"{output.perspective_name}: {output.analysis}")
```

### 分层执行流程

```
第0层执行：
  Expert A ──publish_insight──→ ContextBoard
  Expert B ──publish_insight──→ ContextBoard

第1层执行（可读到第0层结论）：
  Expert C reads: A的结论, B的结论
  Expert C ──publish_insight──→ ContextBoard
```

### ContextBoard 可视化状态

```python
snapshot = board.get_board_state()

snapshot.total_experts   # 总专家数
snapshot.concluded_count # 已完成数
snapshot.entries         # {expert_id: ExpertEntry}
```

### 专家 Entry 结构

```python
@dataclass
class ExpertEntry:
    expert_id: str
    status: ExpertStatus  # THINKING/REVIEWING/WAITING/CONCLUDED
    insight: Optional[str]  # 中间或最终结论
    timestamp: float       # 发布时间戳
    layer: int            # 所属层级
```

### 与 v5 的区别

| 维度 | v5 | v6 内测版 |
|------|-----|----------|
| 专家执行 | 完全独立并行 | 通过 ContextBoard 共享中间结论 |
| 执行顺序 | 全部并行 | 支持分层（layer 0 先执行） |
| 跨专家学习 | 无 | 后层可读先层结论 |
| 反馈闭环 | 有（经验晋升） | 砍掉（内测版不暴露） |
| SupervisorAdapter | 有 | 砍掉（LLM自动路由） |

### 限制

- **内测版**：仅内部测试，不暴露给普通用户
- **不暴露**：不写入文档首页、changelog 等公开材料
- **无持久化**：ContextBoard 在内存中，进程结束即丢失
- **无经验闭环**：不实现经验写入和自动化晋升

### 测试

```bash
cd Agent-superthinking
python -m pytest tests/test_team_integration.py -v
```

### 目录结构（v6 新增）

```
src/super_thinking/
├── team/                      # ← v6 新增
│   ├── __init__.py
│   ├── context_board.py       # 共享状态板
│   └── team_integration.py    # 协作协调层
└── core/
    └── jury.py               # ← 新增 think_with_board()
```

---

_⚔️ 楚灵 · 超思考自优化专家系统 v5 + v6内测(ContextBoard)_

