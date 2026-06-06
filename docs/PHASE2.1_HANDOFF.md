# Phase 2.1 交接文档

> 状态：已完成  
> 日期：2026-06-05  
> 负责人：后端工程师2号  

---

## 一、实现模块清单

### 1. types.py — 基础类型定义

**路径**: `src/super_thinking/v6/types.py`

**内容**:
- ID 类型：`SessionId`, `RoundNumber`, `ArgumentId`, `ExpertId`, `MethodId`, `QuestionId`
- 枚举：`SessionStatus`, `SpeakRole`, `ArgumentStatus`, `ModeratorAction`, `DebateMode`
- 配置类：`ConvergenceTuning`, `DebateConfig`
- 数据类：所有核心 dataclass（Argument, ExpertStatement, DebateSession 等）
- Protocol：`Expert`, `ExpertPool`, `MethodologyRegistry`, `SessionRecorder`, `UserInteraction` 等
- 辅助函数：`generate_argument_id`, `generate_session_id`, `now`

**依赖**: 仅标准库 `dataclasses`, `typing`, `enum`, `time`

---

### 2. expert_pool.py — 动态专家池

**路径**: `src/super_thinking/v6/expert_pool.py`

**类**: `ExpertPool`

**接口实现**:
- `register(expert)` — 注册专家
- `unregister(expert_id)` — 注销专家
- `get(expert_id)` — 获取专家
- `list_registered()` — 列出已注册专家
- `activate/deactivate` — 活跃管理
- `active_ids()` — 获取活跃专家 ID
- `list_active()` — 获取活跃专家列表
- `consult(expert_id, prompt, timeout_s, max_chars)` — 同步阻塞咨询
- `consult_with_sync_timeout(...)` — 带超时的咨询实现
- `snapshot()` — 状态导出

**特性**:
- Registry 风格，轻量实现
- 支持热插拔
- 咨询历史记录
- 批量操作支持

**依赖**: `concurrent.futures`（用于超时实现）

---

### 3. methodology.py — 方法论工具池

**路径**: `src/super_thinking/v6/methodology.py`

**类**: `MethodologyRegistry`, `MethodCallParser`, `BaseMethodologyProvider`

**内置方法论** (18个):
| 分类 | 方法论 |
|------|--------|
| 决策类 | 伦理学、博弈论、经济学、运筹学、管理学、法理学、政治哲学、修辞学、控制论 |
| 理解类 | 社会学、人类学、心理学、现象学、语言学、分析哲学、教育学 |
| 创意类 | 美学、叙事学、传播学 |

**接口实现**:
- `register(provider)` — 注册方法论
- `unregister(method_id)` — 注销方法论
- `get(method_id)` — 获取方法论
- `list_all()` — 列出所有方法论
- `suggest_for(claim, top_k)` — 基于关键词推荐方法论
- `call(method_call)` — 执行方法论调用

**声明解析**:
- 支持 `[方法论调用: 伦理学]` 格式
- 支持 `我用X检验` 格式
- 支持简称 `[ETH]` 格式

**依赖**: 仅标准库 `re`, `time`, `logging`

---

### 4. external_consultation.py — 外部咨询

**路径**: `src/super_thinking/v6/external_consultation.py`

**类**: `ExternalConsultationManager`, `ConsultationRecord`, `MockExpertPool`, `MockExpert`

**接口**:
- `consult(expert_id, question, context, timeout_s, max_chars)` — 执行咨询
- `can_consult_this_round()` — 检查是否还可咨询
- `remaining_consults()` — 剩余咨询次数
- `new_round()` — 开始新轮次
- `get_history()` — 获取咨询历史
- `stats()` — 获取统计信息

**特性**:
- 每轮最多 2 次咨询（可配置）
- 单次 30s 超时（可配置）
- 失败自动降级（返回 None）
- 完整咨询历史

**依赖**: `concurrent.futures.ThreadPoolExecutor`

---

### 5. session_recorder.py — 会议记录器

**路径**: `src/super_thinking/v6/session_recorder.py`

**类**:
- `InMemoryRecorder` — 内存记录器（默认）
- `JsonFileRecorder` — JSON 文件记录器
- `SummaryOnlyRecorder` — 轻量摘要记录器

**事件类型**:
| 事件 | 触发时机 |
|------|----------|
| `session_start` | 会话开始 |
| `round_start` | 轮次开始 |
| `statement` | 专家发言 |
| `menu_update` | 菜单构建 |
| `convergence_signal` | 收敛信号 |
| `moderator_decision` | 主持人决策 |
| `user_intervention` | 用户交互 |
| `consult_call` | 外部咨询 |
| `session_end` | 会话结束 |

**接口**:
- `on_session_start(session)` — 会话开始
- `on_round_start(round_num)` — 轮次开始
- `on_statement(stmt)` — 记录发言
- `on_menu_built(menu)` — 记录菜单
- `on_convergence(signal)` — 记录收敛
- `on_decision(decision)` — 记录决策
- `on_user_question(q, r)` — 记录用户交互
- `on_external_consultation(c)` — 记录咨询
- `on_session_end()` — 会话结束
- `to_dict()` — 导出字典
- `to_json()` — 导出 JSON
- `render()` — 渲染 Markdown

**依赖**: `json`, `pathlib`（JsonFileRecorder 需要）

---

### 6. user_interaction.py — 用户交互

**路径**: `src/super_thinking/v6/user_interaction.py`

**类**:
- `AsyncUserInteraction` — CLI/REPL 场景
- `SyncUserInteraction` — 程序化调用场景
- `MockUserInteraction` — 测试场景

**接口**:
- `ask(question)` — 向用户提问
- `on_user_input(text)` — 处理用户输入，返回 `ModeratorDirective`

**辅助函数**:
- `create_yes_no_question()` — 创建是/否问题
- `create_choice_question()` — 创建选择题
- `create_free_question()` — 创建自由回答问题

**依赖**: 仅标准库 `time`

---

## 二、已知限制

### 1. Expert Protocol 兼容性

`expert_pool.py` 中的 `consult()` 方法需要 Expert 实现 `speak(SpeakPrompt)` 接口。
如果传入的 Expert 没有实现完整接口，可能在运行时出错。

**建议**: 使用 `V5PerspectiveAdapter` 将 v5 Perspective 适配为 v6 Expert。

### 2. 超时精度

`ExternalConsultationManager` 使用 `ThreadPoolExecutor` 实现超时。
在 Windows 上，由于线程调度粒度，实际超时可能略大于设定值。

**建议**: 在 Windows 上测试时增加超时容差。

### 3. 方法论 apply_fn

`BaseMethodologyProvider` 中的 `apply_fn` 默认为 None。
如果不提供，方法论将返回简单的格式字符串。

**建议**: 为每个方法论提供完整的 `apply_fn` 实现。

### 4. SessionRecorder 事件完整性

`InMemoryRecorder` 依赖事件调用顺序正确。
如果某些事件未正确触发，记录可能不完整。

**建议**: 在 Orchestrator 中确保事件调用顺序。

### 5. Mock 实现

`MockExpert`, `MockExpertPool`, `MockUserInteraction` 仅用于测试。
不要在生产环境中使用。

---

## 三、测试建议

### 1. 专家池测试

```python
from super_thinking.v6 import ExpertPool, ExpertPool

pool = ExpertPool()
# 测试 add/remove 循环（10+ 专家）
# 测试咨询超时
```

### 2. 方法论测试

```python
from super_thinking.v6 import create_methodology_registry

registry = create_methodology_registry()
# 测试 18 个方法论注册
# 测试声明解析
# 测试 apply 调用
```

### 3. 咨询测试

```python
from super_thinking.v6 import create_consultation_manager

manager = create_consultation_manager(pool, max_per_round=2, timeout_s=30.0)
# 测试超时降级
# 测试每轮上限
```

### 4. 记录器测试

```python
from super_thinking.v6 import InMemoryRecorder

recorder = InMemoryRecorder()
# 模拟 3 轮辩论
# 测试 to_dict / to_json / render
```

---

## 四、下一棒建议

### 1. Orchestrator 实现（后端工程师1号）

Orchestrator 需要整合所有支撑模块：
- 使用 `ExpertPool` 管理专家
- 使用 `MethodologyRegistry` 处理方法论调用
- 使用 `ExternalConsultationManager` 进行外部咨询
- 使用 `SessionRecorder` 记录会话
- 使用 `UserInteraction` 处理用户交互

### 2. Moderator 实现（待分配）

Moderator 需要：
- 调用 `MethodologyRegistry` 建议方法论
- 调用 `ExternalConsultationManager` 请求外部咨询
- 使用 `SessionRecorder` 记录决策

### 3. V5 Adapter 实现（待分配）

需要实现 `V5PerspectiveAdapter` 将 v5 Perspective 适配为 v6 Expert：
```python
class V5PerspectiveAdapter:
    def __init__(self, perspective: Perspective, role_map: dict): ...
    def speak(self, prompt: SpeakPrompt) -> ExpertStatement: ...
```

### 4. LLM Provider 实现（待分配）

需要实现 `LLMProvider` Protocol：
```python
class LLMProvider:
    def complete(self, prompt, system, temperature, max_tokens) -> str: ...
    def complete_json(self, prompt, system, schema) -> dict: ...
```

---

## 五、文件清单

```
src/super_thinking/v6/
├── __init__.py           # 公共 API 导出
├── types.py              # 基础类型定义
├── expert_pool.py       # 动态专家池
├── methodology.py       # 方法论工具池
├── external_consultation.py  # 外部咨询
├── session_recorder.py  # 会议记录器
└── user_interaction.py  # 用户交互
```

---

## 六、版本信息

| 模块 | 版本 | 状态 |
|------|------|------|
| types.py | 0.1.0 | ✅ 完成 |
| expert_pool.py | 0.1.0 | ✅ 完成 |
| methodology.py | 0.1.0 | ✅ 完成 |
| external_consultation.py | 0.1.0 | ✅ 完成 |
| session_recorder.py | 0.1.0 | ✅ 完成 |
| user_interaction.py | 0.1.0 | ✅ 完成 |

---

*本文档为 Phase 2.1 交接说明，供后续开发者参考。*
