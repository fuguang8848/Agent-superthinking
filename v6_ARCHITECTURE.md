# 超思考 v6 Multi-Agent 圆桌辩论 · 架构设计

> 状态：Phase 1 设计稿
> 日期：2026-06-05
> 适用范围：项目根目录所有 v6_*.md 文档的"骨架"
> 设计基线：`DELIVERY.md` + `ARCHITECTURE.md` + `MODERATOR.md` + v5 现有源码

---

## 一、设计目标与不变式

### 1.1 目标

把 v5 的「路由→并行专家分析→融合」单轮独立输出，升级为 v6 的「主持人组织+多轮辩论+收敛判断+动态专家池+方法论调用」。

### 1.2 不变式（设计必须满足）

| # | 不变式 | 说明 |
|---|--------|------|
| I1 | **向后兼容** | `from super_thinking import Jury; Jury().think(...)` 调用行为不破坏 |
| I2 | **纯标准库优先** | 核心模块仅依赖 Python ≥ 3.10 标准库；`pydantic` 可选；`yaml` 用于配置 |
| I3 | **可测试性** | 每个决策点都接收 Protocol 注入；可被纯 mock 单测，不依赖真实 LLM/网络 |
| I4 | **可观察性** | `SessionRecorder` 记录：每轮菜单、所有专家发言、收敛信号、最终结论 |
| I5 | **可扩展性** | 动态专家池支持热插拔，注册新专家无需改主持人/编排器 |
| I6 | **可移植性** | 单一 Python 进程内运行；无外部服务依赖；可作为库被嵌入任何宿主 |
| I7 | **确定性入口** | 主持人 LLM 调用走 Provider 注入；离线测试可注入 DeterministicProvider |
| I8 | **轮次有界** | 最大轮次硬上限（默认 5），防止无界循环 |

### 1.3 明确"待定"项的决策

| 待定项 | 决策 | 理由 |
|--------|------|------|
| 收敛算法 | 三指标加权：`score = 0.4·overlap + 0.4·(1−new_arg_density) + 0.2·(1−drift)`，阈值 0.65 持续 ≥ 1 轮 | 兼顾"重叠上升"与"新增放缓"，权重重叠 > 密度 > 漂移 |
| 最大轮次默认 | **5 轮**（与 ARCHITECTURE 一致），可配置 | 与上游文档对齐，避免歧义 |
| 每轮专家发言 | **并行获取发言，按专家 ID 字典序稳定写入 Round** | 复用 v5 ThreadPoolExecutor；外部行为"等价于顺序"；可测性高 |
| 论点菜单提取 | **双轨**：(a) 结构化解析器（纯函数）做有效性四标准机械过滤；(b) Moderator LLM 做语义评估+编号分配 | 既可单测，又有语义灵活度 |
| 外部咨询调用方式 | **同步阻塞**，每轮最多 2 次、单次超时 30s；接口预留 `AsyncExternalConsultation` 协议 | 纯标准库友好；简化可测性；未来可升级 |

---

## 二、核心架构图

### 2.1 总体分层

```
┌──────────────────────────────────────────────────────────────────────┐
│  宿主应用 (CLI / Web / Notebook / Agent Runtime)                      │
└────────────────────────────┬─────────────────────────────────────────┘
                             │ 1 次 think(question, ...) 调用
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Entry API (v6 entrypoint)                                            │
│    └─ think_v6() / convene_v6() / Jury().think() (v5 兼容)            │
└────────────────────────────┬─────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Session Orchestrator（v6 编排层）                                    │
│    ├─ DebateSession (会话状态机)                                     │
│    ├─ Round Runner    (轮次执行器)                                    │
│    └─ Finalization    (终态/总结/合成)                                │
└──┬──────────────┬──────────────┬──────────────┬──────────────┬───────┘
   │              │              │              │              │
   ▼              ▼              ▼              ▼              ▼
┌────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│Moderator│  │ExpertPool│  │Expert    │  │Methodology│ │Session  │
│ 主持人  │  │ 动态池   │  │ Adapters │  │ Registry  │ │Recorder │
└────┬───┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
     │           │             │             │             │
     ▼           ▼             ▼             ▼             ▼
   LLM         Registry     v5 Perspective  Method       File/Mem
  Provider    (热插拔)       /v6 Expert    Provider      /Stream
```

### 2.2 模块依赖关系（依赖方向向下，不允许反向依赖）

```
v6.entrypoint          ← 外部 API
  └─ v6.orchestrator   ← 会话/轮次/终态
       ├─ v6.moderator ← 主持人决策
       │    ├─ v6.debate     ← 数据结构 (Round/Argument/Statement)
       │    └─ v6.convergence← 收敛算法
       ├─ v6.pool       ← 专家池
       │    └─ v6.expert_adapter ← 包装 v5 Perspective / 原生 v6 Expert
       ├─ v6.methods    ← 方法论池
       ├─ v6.recorder   ← 记录器
       ├─ v6.interaction← 用户交互
       └─ v6.llm        ← LLM Provider 抽象（可注入）

v6.compat             ← v5 Jury 兼容适配器（v5 entrypoint 调用这里）
v6.types              ← 所有跨模块共享的 Dataclass / Protocol 定义
```

---

## 三、v6 目录结构

### 3.1 落地目录（建议）

```
src/super_thinking/
├── __init__.py                  # 同时导出 v5 与 v6 公共 API
├── core/                        # v5 core（保持原样）
│   ├── router.py
│   ├── registry.py
│   ├── jury.py                  # v5 Jury，内部委托 v6.compat
│   ├── llm_router.py
│   └── extended_registry.py
├── perspectives/                # v5 perspectives（保持原样）
│   ├── _interface.py
│   ├── ...
│   └── verification.py
├── fusion/                      # v5 fusion（保持原样，但 Formatter 升级为可选）
│   ├── formatter.py
│   ├── conflict.py
│   └── consensus.py
│
└── v6/                          # v6 全新包
    ├── __init__.py              # 导出 think_v6 / DebateSession / Moderator 等
    │
    ├── types.py                 # 所有 Dataclass / Protocol 集中定义
    │                            #   - Argument, ArgumentMenu, ExpertStatement
    │                            #   - Round, DebateSession, DebateConfig
    │                            #   - ConvergenceSignal, ModeratorDecision
    │                            #   - MethodologyCall, ExternalConsultation
    │                            #   - RosterChange, UserQuestion, UserResponse
    │
    ├── entrypoint.py            # think_v6() / convene_v6() 顶层 API
    │
    ├── orchestrator.py          # DebateSession 状态机 + RoundRunner
    │
    ├── moderator/
    │   ├── __init__.py
    │   ├── moderator.py         # Moderator 主类
    │   ├── prompt.py            # 主持人 prompt 模板常量
    │   ├── argument_extractor.py# 结构化论点解析器（纯函数）
    │   └── menu_builder.py      # 论点菜单构造器
    │
    ├── convergence/
    │   ├── __init__.py
    │   ├── detector.py          # ConvergenceDetector
    │   └── signals.py           # 信号计算辅助
    │
    ├── expert/
    │   ├── __init__.py
    │   ├── expert.py            # Expert Protocol + ExpertStatement 输出
    │   ├── v5_adapter.py        # 把 v5 Perspective 包装为 v6 Expert
    │   └── native.py            # 原生 v6 Expert 抽象基类
    │
    ├── pool/
    │   ├── __init__.py
    │   └── expert_pool.py       # ExpertPool：热插拔、动态增删
    │
    ├── methods/
    │   ├── __init__.py
    │   ├── registry.py          # MethodologyRegistry
    │   ├── provider.py          # MethodologyProvider Protocol
    │   └── builtin.py           # 18 个方法论的内置 Provider
    │
    ├── interaction/
    │   ├── __init__.py
    │   ├── user_interaction.py  # UserInteraction Protocol
    │   ├── cli_interaction.py   # 命令行默认实现
    │   └── directive.py         # ModeratorDirective 解析
    │
    ├── recorder/
    │   ├── __init__.py
    │   ├── recorder.py          # SessionRecorder Protocol
    │   ├── in_memory.py         # 内存记录器（默认）
    │   └── file_recorder.py     # 文件记录器（JSONL 追加写）
    │
    ├── llm/
    │   ├── __init__.py
    │   ├── provider.py          # LLMProvider Protocol
    │   ├── deterministic.py     # DeterministicProvider（测试用）
    │   └── openai_compat.py     # OpenAI 兼容 Provider（可选）
    │
    ├── compat/
    │   ├── __init__.py
    │   ├── jury_adapter.py      # v5 Jury → v6 兼容入口
    │   └── v5_degenerate.py     # 把 v6 跑成"1 轮非辩论模式"
    │
    └── prompts/                 # 主持人/专家/方法论的 prompt 模板
        ├── moderator_system.md
        ├── expert_initial.md
        ├── expert_rebuttal.md
        ├── expert_final.md
        ├── external_consult.md
        └── menu_extraction.md
```

### 3.2 v5 与 v6 的物理隔离

| 项 | v5 | v6 |
|------|----|----|
| 入口命名 | `think()`, `Jury()` | `think_v6()`, `DebateSession` |
| 数据结构 | `PerspectiveOutput`, `JuryResult` | `ExpertStatement`, `Round`, `Argument` |
| 决策方式 | 路由 → 融合（无中间决策） | 路由 → 主持人 → 多轮循环 → 收敛 |
| 专家协议 | `Perspective.think(input, ctx) -> PerspectiveOutput` | `Expert.speak(prompt) -> ExpertStatement` |
| 轮次 | 1 轮 | 1 轮（兼容） + N 轮（完整） |
| LLM 调用 | 内置/隐式 | 显式 Provider 注入 |

---

## 四、v5 → v6 模块映射与兼容策略

### 4.1 复用而非重写

| v5 模块 | v6 复用方式 | 备注 |
|---------|-------------|------|
| `core/registry.py` `Registry` | 透传为 v6 `ExpertPool._registry` 内核 | 不破坏动态发现能力 |
| `core/router.py` `Router` | 用作 v6 "初始专家选择器" | `mode=auto` 仍可用 |
| `perspectives/_interface.py` `Perspective` | 通过 `V5PerspectiveAdapter` 适配为 v6 `Expert` | 100% 兼容旧实现 |
| `perspectives/*.py`（20+ 个具体专家） | 全部自动以"正式参与"模式参与 v6 辩论 | 无需修改专家代码 |
| `fusion/conflict.py` `ConflictDetector` | v6 在终态时复用产出最终 `ConflictReport` | 重新走专家级 keyword 冲突 |
| `fusion/consensus.py` `ConsensusFinder` | v6 在终态时复用产出最终 `ConsensusReport` | 论点级共识 |
| `fusion/formatter.py` `Formatter` | 升级为可选 `v6.formatter`；保留原类以避免破坏 import | 通过 DeprecationWarning 提示迁移 |
| `config.yaml` | v6 段追加（`v6:` 节点），不破坏 v5 字段 | YAML 解析保持兼容 |
| `tests/test_core.py` | 全部 v5 测试继续通过 | 兼容即正确性 |

### 4.2 兼容适配器（v5 Jury 走 v6 的"单轮退化"路径）

```
Jury().think(input, ctx, mode)
    └─ v6.compat.jury_adapter.adapt()
         ├─ 创建 DebateSession，max_rounds=1, debate_mode="non_debate"
         ├─ 用 v5 Router 选专家
         ├─ 第一轮让所有专家以 "initial" 角色发言（不互相针对）
         ├─ 跳过收敛判断（直接 enter_final）
         └─ 把 v6 终态转换为 v5 JuryResult（同名字段）
              ├─ outputs: dict[str, PerspectiveOutput]   ← 从 ExpertStatement 转换
              ├─ errors:  dict[str, str]
              ├─ routing_result: RoutingResult          ← 透传
              └─ total_perspectives / successful / failed
```

效果：
- 旧调用方代码、测试代码、examples 完全不需修改
- v5 JuryResult 字段全部保留，第三方 import 不破坏
- 性能开销：多一次"非辩论"轮次调度，但无 LLM 增量（仍是一次 think(input)）

### 4.3 废弃/迁移矩阵

| API | 状态 | 迁移路径 |
|-----|------|----------|
| `Jury.think()` | **保留**（v5 入口） | 无需迁移 |
| `Jury.convene()` | **保留** | 无需迁移 |
| `JuryResult.outputs` | **保留** | 内部类型从 v5 → v6 转换的副本 |
| `Perspective` 接口 | **保留** | 仍可注册；推荐新专家实现 v6 `Expert` |
| `Formatter.format()` | **保留但 DeprecationWarning** | 改用 `v6.formatter.render_final()` |
| `ConflictDetector.detect()` | **保留** | 仍在终态时使用 |
| `ConsensusFinder.find()` | **保留** | 仍在终态时使用 |
| `Router.route()` | **保留** | 仍为 v6 初始专家选择器 |

无破坏性变更（No Breaking Changes）。

---

## 五、模块边界与职责

### 5.1 `v6.entrypoint` — 顶层 API

**职责**：对外暴露 `think_v6()`、`convene_v6()`、构造 `DebateSession`。**不**做业务决策。

```python
def think_v6(
    question: str,
    *,
    config: DebateConfig | None = None,
    llm: LLMProvider | None = None,
    expert_pool: ExpertPool | None = None,
    recorder: SessionRecorder | None = None,
    interaction: UserInteraction | None = None,
    context: dict | None = None,
) -> DebateSession: ...
```

### 5.2 `v6.orchestrator` — 会话状态机

**职责**：管理 `DebateSession` 生命周期，调度 Round，驱动 Moderator 决策。

**关键不变量**：
- 一次会话只允许一个 Moderator 决策在跑（线程安全可用锁）
- 轮次推进遵守 Moderator 的 `decision.action`
- 任何异常都要让 session 进入 `aborted` 并通知 Recorder

### 5.3 `v6.moderator` — 主持人

**职责**：把控全局——组织辩论、整理论点菜单、判断收敛、调整阵容、用户交互、方法论指引。

**不**做的事：
- 不直接调用 LLM 生成"我自己"的发言
- 不管理会话状态机（那是 Orchestrator 的事）
- 不存储发言历史（只读）

### 5.4 `v6.convergence` — 收敛判断

**职责**：纯计算模块，给定 Round 列表 → `ConvergenceSignal`。**不**做主持人决策。

### 5.5 `v6.expert` + `v6.pool` — 专家

- `Expert` Protocol：定义 `speak(prompt) -> ExpertStatement`
- `ExpertPool`：注册、注销、增删到会话、初始建议（基于关键词）

### 5.6 `v6.methods` — 方法论池

- `MethodologyProvider` Protocol
- `MethodologyRegistry`：管理所有方法论；提供按 ID/关键词查询
- 主持人/专家可通过 `MethodologyCall` 调用，结果以 `MethodologyResult` 返回并**注入**到下一轮 prompt

### 5.7 `v6.interaction` — 用户交互

- `UserInteraction` Protocol：`ask(question) -> response`
- `ModeratorDirective`：把用户输入解析为主持人可执行指令

### 5.8 `v6.recorder` — 记录器

- `SessionRecorder` Protocol：定义 7 个事件钩子
- 2 个内置实现：内存、JSONL 文件
- 必须能 `render()` 给人看、`to_dict()` 给机器读

### 5.9 `v6.llm` — LLM Provider 抽象

- `LLMProvider` Protocol：`complete(prompt) -> str`
- `DeterministicProvider`：测试用，固定返回脚本化内容
- `OpenAICompatProvider`：可选，外部 LLM 接入

### 5.10 `v6.compat` — v5 兼容层

- `JuryAdapter`：让 v5 `Jury.think()` 跑 v6 单轮退化模式
- `to_v5_jury_result(session) -> JuryResult`：类型转换

---

## 六、关键设计原则（如何应用不变式）

| 不变式 | 应用方式 |
|--------|---------|
| I1 向后兼容 | `v6.compat` + 不修改 v5 源码（仅在 `core/jury.py` 内追加 1 行委托即可） |
| I2 纯标准库 | 用 `dataclasses` + `typing.Protocol`；`pydantic` 仅为可选验证层；并发用 `concurrent.futures` |
| I3 可测试性 | 所有外部依赖（LLM/Recorder/Interaction/Methodology）都是 Protocol，构造时注入；测试中替换为 Fake |
| I4 可观察性 | 7 个 Recorder 钩子覆盖全生命周期；`to_dict()` 输出 JSON 兼容 schema |
| I5 可扩展性 | `ExpertPool.register()` 热插拔；新专家无需碰 Moderator/Orchestrator |
| I6 可移植性 | 单进程、零外部服务；只需 Python ≥ 3.10；可选 `pydantic` 装上即可启用验证 |
| I7 确定性入口 | LLMProvider 注入；测试时 DeterministicProvider 返回写死内容 |
| I8 轮次有界 | `DebateConfig.max_rounds` 硬限制；`Orchestrator` 强制在达到上限时 enter_final |

---

## 七、配置扩展

`config.yaml` 在 v5 字段之上追加 `v6:` 节点：

```yaml
# v5 字段（保留不变）
enabled_perspectives:
  - generated_decision
  - generated_meta
  - magi_debate
  - meta_thinking
  - ...

# v6 新增字段
v6:
  default_max_rounds: 5            # 默认最大轮次
  default_min_experts: 3           # 初始专家最少
  default_max_experts: 6           # 初始专家最多
  max_external_consultations_per_round: 2
  external_consultation_timeout_s: 30
  convergence:
    score_threshold: 0.65           # 综合得分阈值
    require_consecutive: 1          # 需连续 N 轮达标
    overlap_hard_threshold: 0.7     # 硬收敛：重叠率阈值
    new_arg_hard_threshold: 0.5     # 硬收敛：新增论点密度阈值
    weights:
      overlap: 0.4
      new_arg_density: 0.4
      confidence_drift: 0.2
  recorder:
    backend: "in_memory"            # "in_memory" | "file" | "noop"
    file_path: "./.v6_sessions.jsonl"
  llm:
    provider: "openai_compat"       # "openai_compat" | "deterministic"
    model: "gpt-4o-mini"
    temperature: 0.2
```

配置解析：`v6.config.load_v6_config()` 返回 `DebateConfig` dataclass。

---

## 八、错误模型

### 8.1 错误分类

| 类别 | 例子 | 处理 |
|------|------|------|
| `ConfigError` | max_rounds < 1、score 权重和 ≠ 1.0 | 构造时即抛 |
| `ExpertError` | 专家超时、LLM 返回空、格式违规 | 单专家失败不中断，记录 errors，进入下一轮 |
| `MethodologyError` | 未知 method、参数缺失 | 当作 `misuse` 返回，不影响辩论 |
| `UserInteractionTimeout` | 用户长时间不答 | 进入 `user_hold` 状态，超时配置可强制 enter_final |
| `LLMError` | 网络/限流/解析失败 | Moderator 降级为"基于已收集信息"决策 |
| `SessionError` | 状态机非法转移 | 抛 `InvalidStateTransition`；Recorder 记录后 abort |

### 8.2 异常 vs 返回值

- **业务异常**（专家失败、菜单解析失败）→ 返回值携带 `errors` / `warnings`，**不**抛
- **配置/状态机错误** → 抛 `ConfigError` / `InvalidStateTransition`
- **第三方错误**（LLM 5xx）→ 由 Provider 内部重试/降级；最终失败抛出 `LLMError`

---

## 九、性能与成本

- **可移植性优先**：单进程、纯 Python，并发靠线程池
- **延迟**：首轮发言用 `ThreadPoolExecutor` 并行；轮次间 LLM 串行（主持人）
- **成本**：与 ARCHITECTURE §2.12 对齐，**不计成本，质量优先**
- **可观测的成本统计**：Recorder 在 session 末尾输出 `stats` 字段（每轮 LLM 调用次数、专家发言数、外部咨询数）

---

## 十、ADR（架构决策记录）

### ADR-001：辩论形式 = 结构化圆桌（Model C）

**背景**：v5 是单轮独立输出，专家互不知晓。v6 要求真实交锋。
**选项**：
- A. 顺序接力（ContextBoard，已在 DELIVERY 排除）
- B. 自由发言（无结构）
- C. 结构化圆桌：每轮菜单+针对性发言+自由补充

**决策**：C。

**理由**：与 ARCHITECTURE §2.1/§2.2/§2.6 完全一致；Model C 是唯一能形成"有结构的交锋"的形式。

**后果**：需要主持人 LLM 解析论点（结构化解析器 + LLM 语义评估双轨）。

### ADR-002：主持人 LLM 解析 + 结构化解析器 双轨

**背景**：纯 LLM 解析可灵活但难测；纯规则解析快但语义不灵。
**决策**：双轨。
**理由**：结构化解析器（纯函数）保证可单测；LLM 解析（注入式）保证灵活度。
**后果**：需要 `LLMProvider` 协议与 `DeterministicProvider` 测试替身。

### ADR-003：旧 Jury 走 v6 单轮退化模式

**背景**：必须保持 v5 调用不破坏（不变式 I1）。
**决策**：v5 `Jury.think()` 委托 `v6.compat.jury_adapter.adapt()`。
**理由**：单一代码路径，避免维护两套逻辑。
**后果**：v5 行为多一次"非辩论"轮次调度（无 LLM 增量），性能开销可忽略。

### ADR-004：同步阻塞外部咨询

**背景**：DELIVERY §9 列为待定。
**决策**：同步阻塞，每轮上限 2 次。
**理由**：纯标准库友好、简化可测、主持人暂停辩论后才调用，不构成性能瓶颈。
**后果**：保留 `AsyncExternalConsultation` 协议以便未来升级。

### ADR-005：专家发言 = 并行获取 + 字典序稳定写入

**背景**：DELIVERY/ARCHITECTURE 未明确每轮专家发言串并行。
**决策**：并发调用 `Expert.speak()`，收集后按 `expert_id` 字典序排序再写入 Round。
**理由**：与 v5 `Jury` 行为一致；外部观察等价于"按固定顺序发言"；可测性高。
**后果**：测试中可直接用 `FakeExpert` 列表，每轮发言顺序确定。

---

## 十一、与其他 v6_*.md 文档的关系

| 文档 | 关注 |
|------|------|
| v6_ARCHITECTURE.md（本文） | 模块边界、目录结构、兼容策略、ADR |
| v6_INTERFACES.md | 每个 Protocol / Dataclass 的字段与签名 |
| v6_DATA_FLOW.md | 端到端数据走向的 mermaid 图 |
| v6_MIGRATION.md | v5 → v6 升级步骤、回滚路径、灰度方案 |
| v6_TEST_PLAN.md | 每个模块的可 mock 边界、确定性测试点 |

---

_楚灵 · 架构设计 Phase 1 · 2026-06-05_
