---
name: autonomous-ai-agents:superthinking
description: |
  多维度思考框架 v6。具备自我优化能力的 AI 思考系统。
  问题 → 超级大脑分解 → 多专家协作 → 综合报告 → 经验闭环 → 下次更精准。
  触发词：思考、分析、深度分析、多视角、多维分析、复杂问题
  适用场景：复杂问题、重大决策、风险评估、创意突破、人生困惑
---

# ⚔️ 超思考 · 自优化专家系统 v6

> 不同领域的思想家看待同一个问题，结论往往不同——这种差异本身就是洞察的来源。

---

## v6 新增：超级大脑 + 团队协作

```
用户问题
    ↓
┌─────────────────────────────────────────┐
│  超级大脑层（Supervisor Layer）          │
│  Step 1: 复杂度判断 → 决定是否分解      │
│  Step 2: 问题分类（职业/人生/情感/创业） │
│  Step 3: 专家组合模板 + 画像调整         │
│  Step 4: 分解为专家子任务 DAG            │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  团队协作层（Team Layer）                │
│  Step 5: 各专家注册 ContextBoard        │
│  Step 6: 发布进度 / 洞察 / 结论         │
│  Step 7: 其他专家感知已有结论深化分析    │
└─────────────────────────────────────────┘
    ↓
综合报告 + 经验捕获 → 经验闭环 → 下次更准
```

**v6 核心升级：**
- **超级大脑（SupervisorAdapter）**：将复杂问题分解为专家子任务 DAG，并行执行不同视角簇
- **团队协作（TeamIntegration）**：ContextBoard 机制让各专家视角共享上下文
- **经验闭环（LearningsIntegration）**：捕获交互经验，优化下次专家选择

---

## 核心架构：反馈闭环

```
问题输入
    ↓
┌─────────────────────────────────────────┐
│  学习层（Learning Layer）               │
│  Step 1: 读取用户画像                  │
│  Step 2: 基于画像 + 初步路由           │
│  Step 3: 智能推荐（画像权重调整）      │
│  Step 4: 追问获取上下文               │
└─────────────────────────────────────────┘
    ↓
用户选择轨别和粒度
    ↓
激活专家并行分析
    ↓
综合报告
    ↓
┌─────────────────────────────────────────┐
│  反馈层（Feedback Layer）               │
│  Step 5: 多维反馈收集                  │
│  Step 6: 画像更新                      │
│  Step 7: 组合效果追踪                 │
└─────────────────────────────────────────┘
    ↓
下次路由时读取更新后的画像 → 更精准的推荐
```

---

## 专家体系

40 位专家，3 类来源：

| 类型 | 数量 | 说明 |
|------|------|------|
| 本地人物 | 30 | 哲学/科学/心理/经济/文学/军事/数学/宗教 |
| 方法论框架 | 13 | 复杂系统/博弈论/贝叶斯/信息论等 |
| 外部引用 | 10 | 马斯克/纳瓦尔/芒格/费曼等 |

专家索引：`INDEX.md`（人物）+ `INDEX_METHODS.md`（方法论）

---

## 路由模式

| 模式 | 说明 |
|------|------|
| `auto` | 关键词匹配触发（默认） |
| `force_all` | 激活所有已启用专家 |
| `selective` | 指定专家 ID |

---

## 核心组件

### 1. SupervisorAdapter（超级大脑，问题分解）
- 文件：`src/super_thinking/orchestrator/supervisor_adapter.py`
- 职责：将复杂问题分解为专家子任务 DAG，按复杂度选择并行策略
- 核心方法：`decompose(question, user_id=...)` → `DecomposedQuestion`
- 关键类：`QuestionComplexity`（SIMPLE/MODERATE/COMPLEX/CRITICAL）
- 专家组合模板：按问题类型预定义 required + optional 专家

### 2. TeamIntegration（团队协作，ContextBoard）
- 文件：`src/super_thinking/team/team_integration.py`
- 职责：多专家协作管理层，发布进度/洞察/结论，其他专家可感知深化
- 核心方法：`publish_start()` / `publish_insight()` / `publish_concluded()`
- 协作阶段：`THINKING` → `CONCLUDED` / `WAITING` / `REVIEWING`

### 3. LearningsIntegration（经验闭环）
- 文件：`src/super_thinking/learnings/learnings_integration.py`
- 职责：捕获分析经验，追踪专家组合效果，晋升高价值经验到 SOUL.md
- 核心方法：`capture_analysis_result()` / `get_tips_for_question_type()` / `check_promotions()`
- 晋升规则：某组合使用 ≥5 次且评分 ≥4 → 自动写入 SOUL.md

### 4. Router（路由层）
- 文件：`src/super_thinking/core/router.py`
- 职责：根据输入匹配专家，返回 `RoutingResult`
- **v5 升级**：集成 ProfileManager，路由时读取用户画像调整专家权重

### 5. Jury（协调层）
- 文件：`src/super_thinking/core/jury.py`
- 职责：并行执行多个专家视角，结果聚合
- **v5 升级**：集成 FeedbackCollector，分析后自动生成追问提示
- **v6 升级**：新增 `think_complex()` 方法，集成 Supervisor + Team + Learnings
- 关键方法：
  - `think(input, user_id=...)` → 标准多视角分析（v5）
  - `think_complex(question, user_id, team, learnings)` → 复杂问题模式（v6）

### 6. ProfileManager（用户画像管理器）
- 文件：`src/learning/profile_manager.py`
- 职责：画像 CRUD、问题分类、基于画像的推荐

### 7. FeedbackCollector（反馈收集器）
- 文件：`src/learning/feedback_collector.py`
- 职责：收集多维度反馈，验证完整性

### 8. RoutingOptimizer（路由优化器）
- 文件：`src/learning/routing_optimizer.py`
- 职责：基于反馈调整专家权重，推荐最佳组合

---

## 用户画像

```yaml
user_profile:
  user_id: string
  name: string
  created_at: timestamp
  updated_at: timestamp

  feedback_history: [...]
  expert_preferences:
    "尼采":
      score: 0.8     # -1到1
      use_count: 5
      success_count: 4
  question_patterns:
    "职业发展":
      count: 3
      preferred_experts: ["芒格", "纳瓦尔"]
  expert_combinations:
    "芒格+纳瓦尔":
      success_rate: 0.9
      total_count: 5
  routing_weights:
    default_weights: {...}
    personal_adjustments: {...}
```

---

## config.yaml 更新方法

当前 `enabled_perspectives` 中的测试视角（`generated_*`, `test_*`）可替换为真实专家视角：

```bash
# 查看所有可用的专家视角
cd /home/fuguang/Agent-superthinking
python3 -c "
import sys; sys.path.insert(0, 'src')
from super_thinking.core.registry import Registry
r = Registry()
all_ids = [p.id for p in r.list_all()]
enabled = [p.id for p in r.list_enabled()]
print('All:', all_ids)
print('Enabled:', enabled)
"

# 更新 config.yaml（将 your_perspective_id 替换为真实 ID）
# 建议保留 meta_thinking 用于元认知
```

---

## 目录结构

```
Agent-superthinking/
├── SKILL.md              # 本文件
├── INDEX.md              # 人物专家索引（路由真相源）
├── INDEX_METHODS.md      # 方法论框架索引
├── LEARNING.md           # 自优化系统架构
├── PROFILE_SCHEMA.md     # 画像数据结构
├── PROFILES.md           # 用户画像使用指南
├── src/
│   ├── learning/         # 自优化层
│   │   ├── profile_manager.py
│   │   ├── feedback_collector.py
│   │   ├── routing_optimizer.py
│   │   └── expert_combination_tracker.py
│   ├── super_thinking/
│   │   ├── core/
│   │   │   ├── router.py      # 路由层
│   │   │   ├── registry.py
│   │   │   └── jury.py        # 协调层（含 v6 think_complex）
│   │   ├── orchestrator/
│   │   │   └── supervisor_adapter.py  # v6 超级大脑
│   │   ├── team/
│   │   │   └── team_integration.py    # v6 团队协作
│   │   ├── learnings/
│   │   │   └── learnings_integration.py  # v6 经验闭环
│   │   └── perspectives/       # 专家视角实现
│   └── learning/              # learning 层入口
└── experts/              # 专家知识库（MD 文件）
```

---

## 使用示例

### v5 标准模式（think）

```python
import sys
sys.path.insert(0, '/home/fuguang/Agent-superthinking/src')

from super_thinking.core.jury import Jury, get_jury
from super_thinking.core.router import get_router
from learning import ProfileManager, FeedbackCollector

# 初始化（完整集成版）
pm = ProfileManager('/home/fuguang/Agent-superthinking/profiles/')
fc = FeedbackCollector()
jury = get_jury(profile_manager=pm, feedback_collector=fc)

# Step 1: 分析
result = jury.think("30岁要不要跳槽？", user_id="default")
print(f"激活专家: {result.analysis_metadata['experts_used']}")
print(f"问题类型: {result.analysis_metadata['question_type']}")

# Step 2: 追问（打印 followup_prompt 让用户评价）
print("追问提示:", result.followup_prompt)

# Step 3: 提交反馈 → 画像更新
feedback_result = jury.submit_feedback("default", {
    "analysis_metadata": result.analysis_metadata,
    "user_response": "评分4，尼采和加缪的视角最有帮助，缺少商业视角"
})
print("画像更新:", feedback_result)

# 下次路由时，尼采/加缪权重自动提升
result2 = jury.think("人生的意义是什么？", user_id="default")
print(f"路由调整: {result2.routing_result.reason}")
```

### v6 超级大脑模式（think_complex）

```python
import sys
sys.path.insert(0, '/home/fuguang/Agent-superthinking/src')

from super_thinking.core.jury import Jury, get_jury
from super_thinking.core.router import get_router
from super_thinking.orchestrator import SupervisorAdapter
from super_thinking.team import TeamIntegration
from super_thinking.learnings import LearningsIntegration
from learning import ProfileManager

# 初始化
pm = ProfileManager('/home/fuguang/Agent-superthinking/profiles/')
jury = get_jury(profile_manager=pm)
team = TeamIntegration()
learnings = LearningsIntegration()

# 超级大脑模式：复杂问题分解 + 多专家协作 + 经验闭环
result = jury.think_complex(
    question="40岁职场人，创业还是继续打工？",
    user_id="default",
    team=team,
    learnings=learnings,
)

# 打印分解计划
plan = result["decomposed_plan"]
print(f"问题类型: {plan['question_type']}")
print(f"复杂度: {plan['complexity']}")
print(f"分解为 {len(plan['subtasks'])} 个子任务")
print(f"执行层级: {plan['execution_layers']}")

# 打印团队协作摘要
board = result["team_session"]
print(f"团队进度: {board['progress']}")
print(f"各阶段专家: {board['by_phase']}")

# 打印综合报告摘要
synthesis = result["synthesis"]
print(f"关键角度: {synthesis['key_angles']}")
print(f"警示思维陷阱: {synthesis['warnings']}")

# 打印经验捕获结果
if result["learnings"]:
    print(f"经验提示: {result['learnings']['tip']}")
```

### 单独使用 SupervisorAdapter

```python
from super_thinking.orchestrator import SupervisorAdapter

adapter = SupervisorAdapter()
plan = adapter.decompose("要不要转行做AI？", user_id="default")

print(f"复杂度: {plan.complexity.value}")
print(f"问题类型: {plan.question_type}")
print(f"专家组合: {[st.expert_name for st in plan.subtasks]}")
print(f"执行层级: {plan.execution_layers}")
print(f"关键角度: {plan.key_angles}")
print(f"警示: {plan.warnings}")
```

---

## 完整工作流

```
用户问题 → Jury.think_complex(user_id="default")
    ↓
SupervisorAdapter.decompose() → 复杂度判断 + 专家组合 + DAG
    ↓
TeamIntegration.register_experts() → ContextBoard 注册
    ↓
按 execution_layers 并行执行各专家视角
    ↓
TeamIntegration 发布 CONCLUDED 状态
    ↓
Jury._synthesize_results() → 综合报告
    ↓
LearningsIntegration.capture_analysis_result() → 经验记录
    ↓
(可选) LearningsIntegration.check_promotions() → 高价值经验晋升 SOUL.md
```

---

## 复杂度等级与策略

| 等级 | 触发关键词 | 策略 |
|------|-----------|------|
| `SIMPLE` | 是什么/介绍/简单说说 | 单专家直接回答 |
| `MODERATE` | 分析/对比/评价/选择 | 3-4专家并行分析 |
| `COMPLEX` | 创业/转型/人生规划/重大决策 | 全专家协作 + 多轮深化 |
| `CRITICAL` | 投资/风险/大额/高风险 | 三角验证 + 警示检查 |

---

## 专家组合模板（按问题类型）

| 问题类型 | Required | Optional |
|---------|----------|----------|
| 职业发展 | 稻盛和夫, 德鲁克 | 乔布斯, 查理芒格, 马斯克 |
| 人生规划 | 尼采, 加缪 | 苏格拉底, 王阳明, 孔子 |
| 情感关系 | 佛学视角, 心理学视角 | 孔子, 亚里士多德 |
| 创业商业 | 巴菲特, 查理芒格 | 孙正义, 马斯克, 马云 |
| 学术研究 | 费曼, 西蒙 | 学科专家 |
| 通用问题 | 苏格拉底 | 亚里士多德, 孔子, 尼采 |

---

## JuryResult 关键字段

| 字段 | 说明 |
|------|------|
| `outputs` | 各专家视角的输出（PerspectiveOutput） |
| `analysis_metadata` | 分析元数据：问题、专家列表、问题类型、是否应用了画像 |
| `followup_prompt` | 反馈收集提示（来自 FeedbackCollector） |
| `team_context` | 团队协作上下文（来自 TeamIntegration） |
| `get_experts_used()` | 提取所有使用的专家名称 |

---

## 经验闭环机制

1. **捕获**：`capture_analysis_result(question_type, experts_used, rating)`
   - 相同专家组合 + 相同问题类型 → 合并计数
   - rating ≥ 4 计入成功次数

2. **查询**：`get_tips_for_question_type(question_type)`
   - 返回历史评分 ≥3.5 的专家组合提示
   - 格式：「尼采+加缪」历史评分 4.2/5，成功率 80%（5次使用）

3. **晋升**：`check_promotions()`
   - 使用次数 ≥5 且评分 ≥4 → 写入 SOUL.md
   - 晋升后标记 resolved=true，避免重复写入

4. **摘要**：`get_learning_summary(days=7)`
   - 按问题类型统计次数、平均评分、组合数
   - 列出各类别最佳专家组合

---

## config.yaml 更新方法

1. **反馈是否被收集**：分析后必须触发反馈收集
2. **画像是否更新**：收到反馈后必须更新 profile
3. **下次推荐是否参考画像**：路由时必须读取并应用画像权重
4. **隐私保护**：profile 只存储偏好数据，不存储敏感内容

---

_⚔️ 楚灵 · 超思考自优化专家系统 v6_
