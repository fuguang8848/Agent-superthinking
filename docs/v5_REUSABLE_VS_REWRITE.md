# v5 可复用能力 vs 需重写能力分析

> 版本：v1.0
> 日期：2026-06-05
> 作者：后端工程师

---

## 1. 概述

本文档分析 v5 核心模块中哪些能力可以直接复用到 v6，哪些需要重写。

v6 的核心变化是引入 Multi-Agent 圆桌辩论，要求：
- 专家之间进行真实的来回交锋，而非并行独立输出
- 动态轮次和主持人判断收敛
- 方法论作为工具池供专家调用

---

## 2. 可直接复用到 v6 的能力

### 2.1 Registry 机制

| 能力 | 说明 | 复用方式 |
|------|------|----------|
| 动态发现 | `discover()` 扫描目录加载模块 | ExpertPool 可复用此模式 |
| 接口验证 | `_validate_perspective()` 验证必需属性 | 可改造为验证 Expert 接口 |
| enable/disable | 启用/禁用专家 | ExpertPool 管理专家状态 |
| 配置持久化 | yaml 保存配置 | 专家配置复用此机制 |

**关键类/函数：**
- `Registry.discover()`
- `Registry._validate_perspective()`
- `Registry.enable() / disable()`
- `Registry._load_config() / _save_config()`

### 2.2 ThreadPoolExecutor 并行执行

| 能力 | 说明 | 复用方式 |
|------|------|----------|
| 并行执行 | `ThreadPoolExecutor` 并发调用 | 第一轮并行发言可复用 |
| 超时控制 | `timeout_per_perspective` | 每个专家执行超时 |
| 异常隔离 | 单个失败不影响整体 | 单个专家失败不影响辩论 |

**关键代码：**
```python
with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
    future_to_pid = {
        executor.submit(self._execute_perspective, p, input, context): p.id
        for p in perspectives
    }
```

### 2.3 数据类定义模式

| 数据类 | 字段 | 复用方式 |
|--------|------|----------|
| `RoutingResult` | activated, mode, reason, scores | `DebateState` 可参考 |
| `JuryResult` | outputs, errors, routing_result | `DebateResult` 可参考 |
| `PerspectiveOutput` | analysis, confidence, key_points, tags, warnings | `ExpertStatement` 可参考 |

**模式：使用 `@dataclass` 定义数据结构，便于序列化**

### 2.4 ConflictDetector 冲突检测

| 能力 | 说明 | 复用方式 |
|------|------|----------|
| 关键词矛盾检测 | `CONTRADICTION_KEYWORDS` | 辩论中检测专家分歧 |
| 置信度差异 | `_check_confidence_gaps()` | 检测观点强度差异 |
| 结论分歧 | `_check_divergence()` | 判断是否收敛 |

**关键类：**
- `ConflictDetector.detect(outputs)`
- `Conflict` dataclass
- `ConflictReport` dataclass

### 2.5 ConsensusFinder 共识发现

| 能力 | 说明 | 复用方式 |
|------|------|----------|
| 精确匹配 | `_find_exact_matches()` | 检测专家是否达成共识 |
| 主题匹配 | `THEME_GROUPS` | 归类专家观点 |
| 共识分层 | strong/moderate/weak | 判断收敛程度 |

**关键类：**
- `ConsensusFinder.find(outputs)`
- `ConsensusPoint` dataclass
- `ConsensusReport` dataclass

### 2.6 ExtendedRegistry SKILL 扩展

| 能力 | 说明 | 复用方式 |
|------|------|----------|
| 多目录扫描 | `_discover_skill_perspectives()` | 加载专家定义 |
| `experts/` 结构 | methods/frameworks/people | 专家分类结构 |

---

## 3. 需要重写的能力

### 3.1 Router → Moderator

| v5 Router | v6 Moderator | 原因 |
|-----------|-------------|------|
| `route()` 选择专家 | 初始化专家组合 | v6 需要主持人选择初始阵容 |
| `_route_auto()` 关键词匹配 | 智能选择逻辑 | 需要基于问题类型选择 |
| `_route_force_all()` 全部激活 | 按需邀请专家 | 动态参与是核心特性 |
| 无 | 轮次管理 | v6 需要主持人控制辩论轮次 |
| 无 | 收敛判断 | v6 需要主持人判断是否收敛 |
| 无 | 论点菜单提取 | v6 需要主持人整理论点 |

**新增职责：**
- 宣布论点菜单
- 监控辩论走向
- 判断收敛条件
- 调整专家阵容（加入/请离）
- 向用户询问信息

### 3.2 Jury → DebateOrchestrator

| v5 Jury | v6 DebateOrchestrator | 原因 |
|---------|----------------------|------|
| `think()` 并行执行 | `run_round()` 辩论轮次 | v6 是多轮循环 |
| `_execute_perspective()` | `_call_expert_statement()` | 专家需要"针对"格式 |
| `convene()` 指定执行 | 主持人协调辩论 | 主持人主导交锋 |
| 无 | 管理辩论状态 | 需要记录每轮论点 |
| 无 | 方法论调用 | 专家使用工具池 |

**新增职责：**
- 管理辩论状态（当前轮次、论点历史）
- 调用主持人逻辑
- 管理专家发言顺序
- 收集和存储论点

### 3.3 Fusion → 辩论融合（增强）

| v5 Fusion | v6 融合 | 原因 |
|-----------|---------|------|
| 冲突检测（一次性） | 实时冲突检测 | 每轮都需要检测收敛 |
| 共识发现（一次性） | 动态共识跟踪 | 收敛是渐进过程 |
| Formatter 格式化 | 会议结论生成 | 需要结构化输出 |

**变化：**
- 冲突/共识检测需要支持增量更新
- 新增论点菜单生成逻辑
- 新增会议结论格式

### 3.4 PerspectiveOutput → ExpertStatement

| v5 PerspectiveOutput | v6 ExpertStatement | 变化 |
|---------------------|-------------------|------|
| analysis | statement | 专家发言内容 |
| key_points | arguments | 论点列表 |
| 无 | targets | 针对的专家/论点 |
| 无 | uses_methodology | 使用的方法论 |
| 无 | is_final | 是否最终陈述 |

---

## 4. 能力映射表

| v5 模块 | v6 模块 | 复用度 |
|---------|---------|--------|
| Registry | ExpertPool | 70% - 动态发现复用 |
| Router | Moderator | 30% - 选择逻辑重写 |
| Jury | DebateOrchestrator | 50% - 执行框架复用 |
| ConflictDetector | DebateAnalyzer | 80% - 检测逻辑复用 |
| ConsensusFinder | DebateAnalyzer | 80% - 共识逻辑复用 |
| Formatter | ConclusionGenerator | 40% - 格式化模式复用 |
| LLMRouter | Moderator._select_experts() | 50% - LLM 选择复用 |
| ExtendedRegistry | ExpertPool | 90% - 直接复用 |

---

## 5. v6 新增能力（v5 没有）

| 能力 | 说明 | 实现难度 |
|------|------|----------|
| 论点菜单提取 | 从专家发言提取有效论点 | 中 |
| 收敛算法 | 论点重叠率、新增密度计算 | 高 |
| 用户交互 | 主持人向用户询问信息 | 中 |
| 专家调整 | 动态加入/请离专家 | 中 |
| 外部咨询 | 主持人私下询问专家 | 低 |
| 方法论调用 | 专家使用方法论工具 | 高 |

---

## 6. 建议

### 6.1 优先复用
1. Registry 机制 - ExpertPool
2. ConflictDetector - DebateAnalyzer
3. ConsensusFinder - DebateAnalyzer
4. ThreadPoolExecutor 模式 - DebateOrchestrator

### 6.2 需要重构
1. Router → Moderator（完全重写）
2. Jury → DebateOrchestrator（结构变化大）
3. PerspectiveOutput → ExpertStatement（新增字段）

### 6.3 接口兼容性
v6 应保持对 v5 的单轮退化能力：
- 当 `mode="single"` 时，等同于 v5 的 Jury 执行
- `PerspectiveOutput` 保持兼容
- Registry 发现机制保持不变

---

_文档版本：v5 可复用能力 vs 需重写能力分析 v1.0_
