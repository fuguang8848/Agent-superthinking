# 超思考 v6 · 迁移与兼容性策略

> 状态：Phase 1 设计稿
> 日期：2026-06-05
> 范围：v5 → v6 的兼容性矩阵、降级路径、回滚、灰度
> 不变式：**v5 公共 API 完全向后兼容**

---

## 1. 兼容性总目标

| 维度 | 目标 | 风险等级 |
|------|------|----------|
| 公共 API | `Jury().think()`, `Jury().convene()`, `Perspective` 接口 100% 兼容 | 0 |
| 数据结构 | `JuryResult` 字段不变；`PerspectiveOutput` 字段不变 | 0 |
| 配置 | `config.yaml` v5 字段不变；v6 段为可选追加 | 0 |
| 测试 | `tests/test_core.py` 全部继续通过 | 0 |
| 行为 | 旧调用走"v6 单轮非辩论模式"——结果与原 v5 高度一致（仅多 1 轮调度开销） | 1（性能） |
| 第三方 import | 任何 `from super_thinking import ...` 不破坏 | 0 |

---

## 2. 兼容映射矩阵

### 2.1 v5 入口 → v6 路径

| v5 调用 | 实际走 v6 哪条路径 | 最终返回 |
|---------|--------------------|----------|
| `Jury().think(input, ctx, mode="auto")` | `JuryAdapter.adapt` → v6 `DebateSession{mode=NON_DEBATE, max_rounds=1}` | v5 `JuryResult`（`outputs` 仍是 `PerspectiveOutput`） |
| `Jury().think(input, ctx, mode="force_all")` | 同上，但 ExpertPool 强制全开 | 同上 |
| `Jury().think(input, ctx, mode="selective", ids=[...])` | 同上，只激活 ids 中专家 | 同上 |
| `Jury().convene(perspective_ids, input, ctx)` | 直接调用 v5 路径（不走 v6） | v5 `list[PerspectiveOutput]` |
| `Router().route(input, mode)` | 不变 | v5 `RoutingResult` |
| `Registry().register/get/list_enabled` | 不变 | v5 Registry 接口 |

### 2.2 v5 Perspective → v6 Expert

所有 v5 Perspective 通过 `V5PerspectiveAdapter` 转为 v6 Expert：

```
v5 Perspective.think(input, context) -> PerspectiveOutput
                              │
                              ▼
v6 V5PerspectiveAdapter.speak(SpeakPrompt) -> ExpertStatement
                              │
                              ▼
to_v5_jury_result 把 ExpertStatement 转回 PerspectiveOutput
```

字段对应（适配器内部）：

| v6 ExpertStatement 字段 | v5 PerspectiveOutput 字段 |
|-------------------------|---------------------------|
| `content` | `analysis` |
| `confidence` | `confidence` |
| `suggested_arguments[*].claim` | `key_points` |
| `expert_name` | `perspective_name` |
| `expert_id` | `perspective_id` |
| `methodology_call` 摘要 | `metadata["methodology"]` |
| `warnings` | `warnings` |
| `extra` 选 `tags` | `tags` |

### 2.3 v5 fusion 复用

| v5 组件 | v6 复用位置 | 何时调用 |
|---------|-------------|----------|
| `ConflictDetector.detect(outputs)` | 终态合成时 | `Orchestrator.finalize` 中调一次 |
| `ConsensusFinder.find(outputs)` | 终态合成时 | 同上 |
| `Formatter.format(outputs, conflicts, consensus)` | 单轮退化模式 | 旧 v5 JuryResult 输出 |
| `v6.formatter.render_final(consensus, final_stmts)` | 完整辩论模式 | `format_final_consensus` 后 |

---

## 3. v5 Jury 内部如何"看起来没变"

v5 `Jury.think()` 方法做最少改动：

```python
# src/super_thinking/core/jury.py (新增 v6 入口)
from super_thinking.v6.compat import JuryAdapter

class Jury:
    def __init__(self, registry=None, router=None, ..., use_v6: bool | None = None):
        ...
        # 默认 use_v6=None：自动检测（v6 包存在则 True，否则 False）
        self._use_v6 = use_v6

    def think(self, input, context=None, mode="auto", selective_ids=None):
        if self._should_use_v6():
            return JuryAdapter(self).think(input, context, mode, selective_ids)
        # ---- 原 v5 逻辑（保持不变，作为兜底） ----
        return self._legacy_think(input, context, mode, selective_ids)
```

**关键点**：
- 通过环境变量 `SUPER_THINKING_LEGACY=1` 可强制走原 v5 路径
- 通过 `Jury(use_v6=False)` 显式走原路径
- 默认行为：检测到 `super_thinking.v6` 包可用则走 v6 适配

---

## 4. 升级步骤

### 4.1 代码升级（开发者）

```bash
# 1. 拉新代码
git pull origin main

# 2. 安装（仅在已有可选依赖上追加，不新增强制依赖）
pip install -e .                          # 已有；无变化
# 可选（增强校验）：
pip install -e .[pydantic]               # 新增；启用 v6.types.validate()

# 3. 跑现有 v5 测试，确认不破坏
pytest tests/test_core.py -v

# 4. 跑 v6 自己的测试
pytest tests/test_v6/ -v

# 5. 灰度（按需）
# 默认就走 v6 适配；想回退：export SUPER_THINKING_LEGACY=1
```

### 4.2 配置升级（运维）

```yaml
# 旧 config.yaml（保留）
enabled_perspectives:
  - generated_decision
  - ...

# 追加 v6 段（可选）
v6:
  default_max_rounds: 5
  convergence:
    score_threshold: 0.65
  recorder:
    backend: "in_memory"
```

> 不追加 v6 段时，v6 适配器使用代码内默认值；不破坏任何 v5 行为。

### 4.3 调用方升级（应用）

```python
# 旧代码（继续工作，不需改）
from super_thinking import Jury
result = Jury().think("Should I invest in AI?")
for o in result.get_outputs():
    print(o.analysis)

# 新代码（享受 v6 完整辩论）
from super_thinking.v6 import think_v6, DebateConfig
session = think_v6(
    "Should I invest in AI?",
    config=DebateConfig(max_rounds=4),
)
print(session.final_consensus.consensus_points)
print(session.rounds[-1].menu.items)
```

### 4.4 数据迁移（如有持久化）

- v5 没有持久化层（Recorder 是新增），所以**无数据迁移**
- 若用户开始用 `v6.recorder.file_recorder`，文件格式为 JSONL，自行管理

---

## 5. 灰度方案

### 5.1 三档灰度

| 阶段 | 比例 | 配置 | 监控 |
|------|------|------|------|
| 阶段 0：仅 v5 | 100% | `SUPER_THINKING_LEGACY=1` 强制 | v5 现有指标 |
| 阶段 1：v5 兼容 v6 适配（单轮） | 100% | 默认 | 输出对比 v5 vs 适配结果的差异 |
| 阶段 2：v5 兼容 v6 + 部分新调用走完整辩论 | 旧调用仍单轮；新调用用 `think_v6` | 默认 | 监控完整辩论的 LLM 调用次数、session 长度 |

### 5.2 关键回退开关

| 开关 | 作用 | 何时用 |
|------|------|--------|
| `SUPER_THINKING_LEGACY=1` | 强制 v5 原路径 | 适配器有 bug 时立即回退 |
| `Jury(use_v6=False)` | 单次调用级回退 | 进程内灰度 |
| `DebateConfig(mode=NON_DEBATE)` | 走单轮非辩论（仍是 v6 路径） | 不想用完整辩论但要走新 Recorder |
| `DebateConfig(max_rounds=1)` | 完整辩论但只跑 1 轮 | 验证 Moderator 流程时 |

### 5.3 监控指标

| 指标 | 来源 | 告警阈值 |
|------|------|----------|
| 适配后 v5 调用成功率 | Recorder.on_session_end | < 99.9% 告警 |
| 适配后 JuryResult 字段差异数 | 单测断言 | > 0 阻断 |
| 完整辩论平均轮数 | `session.stats["rounds"]` | > 4 提示用户调小 max_rounds |
| 外部咨询超时率 | `ExternalConsultation.timed_out` | > 10% 提示扩容 |
| LLM 调用总次数 | `session.stats["llm_calls"]` | 软监控 |

---

## 6. 回滚计划

### 6.1 立即回滚（分钟级）

```bash
# 1. 切回 v5 路径
export SUPER_THINKING_LEGACY=1
# 2. 重启服务（如果有）
systemctl restart super-thinking
```

效果：v5 调用恢复原行为；v6 调用方报 `ImportError: v6 package disabled`，业务侧可立即降级为 v5。

### 6.2 完整回滚（小时级）

```bash
# 回退到上一个稳定版本
git checkout v5-stable
pip install -e .
```

不修改数据库（无 schema）；不修改 config.yaml（兼容读取）。

### 6.3 数据回滚

- v6 Recorder 是**追加**的（JSONL 文件），可保留也可删除
- v5 无持久化，**无回滚数据**
- 用户 LLM 调用历史（如果用户自己记了）由用户决定

---

## 7. 兼容性测试矩阵

| 维度 | 测试 |
|------|------|
| v5 API 入口 | `Jury().think()` / `Jury().convene()` 各 mode 各跑一次 |
| v5 数据结构 | `JuryResult.outputs` key/value 类型与字段 |
| v5 配置文件 | 不带 `v6:` 段时正常加载 |
| v5 测试套件 | `pytest tests/test_core.py` 全绿 |
| v5 第三方 import | `from super_thinking import Jury, Router, Formatter, ...` |
| v5 实际行为 | 同一 input 跑 v5 vs 适配 v6，对比 `JuryResult.outputs` 字段集（值允许 LLM 不同时） |
| v6 调用方走 v5 兼容 | 走 v6 但 config 强制 `mode=NON_DEBATE` 后，外部仍按 v6 拿 DebateSession |

---

## 8. 破坏性变更评估

> **结论：零破坏性变更（Zero Breaking Change）。**

逐项检查：

| 行为 | v5 表现 | v6 表现 | 是否破坏 |
|------|---------|---------|----------|
| `Jury().think` 返回类型 | `JuryResult` | `JuryResult`（同 v5） | 否 |
| `JuryResult.outputs` 值类型 | `PerspectiveOutput` | `PerspectiveOutput`（来自 ExpertStatement 转换） | 否 |
| `JuryResult.errors` | `dict[str, str]` | `dict[str, str]` | 否 |
| `JuryResult.get_outputs()` | `list[PerspectiveOutput]` | `list[PerspectiveOutput]` | 否 |
| `JuryResult.has_errors()` | bool | bool | 否 |
| `JuryResult.get_perspective_ids()` | `list[str]` | `list[str]` | 否 |
| `Perspective.think(input, ctx)` | 返回 `PerspectiveOutput` | 不变 | 否 |
| `PerspectiveOutput` 字段集 | 7 字段 | 7 字段（不增不减） | 否 |
| `Router.route(input, mode)` | `RoutingResult` | 不变 | 否 |
| `Registry.register/get/...` | 同 v5 | 不变 | 否 |
| `Formatter.format(...)` | 同步返回 `PerspectiveOutput` | 仍可调用；带 `DeprecationWarning` | 仅警告，不破坏 |
| `ConflictDetector.detect(...)` | `ConflictReport` | 不变 | 否 |
| `ConsensusFinder.find(...)` | `ConsensusReport` | 不变 | 否 |
| `config.yaml` 顶层字段 | `enabled_perspectives` | 不变 | 否 |
| `pyproject.toml` 强制依赖 | 同 v5 | 不变 | 否 |
| `pyproject.toml` 可选依赖 | `openclaw`, `langchain` | 新增 `pydantic` | 否（可选） |

---

## 9. 第三方集成影响

### 9.1 OpenClaw

- `pyproject.toml` 的 `[openclaw]` optional-dependency 不变
- 任何 OpenClaw 集成若引用 `super_thinking.core.jury.Jury`，继续可用
- 若要集成 v6，需 OpenClaw 端主动 `from super_thinking.v6 import ...`

### 9.2 LangChain 适配（`pyproject.toml` 的 `[langchain]`）

- 原 v5 LangChain 适配（如果有）继续可用
- v6 新增 `v6.llm.openai_compat.OpenAICompatProvider` 与 LangChain 的 LLM 共存
- 推荐：v6 Provider 复用 LangChain 的 ChatModel（在 v6.llm 适配器里）

### 9.3 examples/

- `examples/feedback_example.md` 是 markdown 文档，不需改
- 若 examples 目录有 `.py` 脚本，走 v5 入口；继续可用

---

## 10. 迁移检查清单（给后端工程师）

- [ ] 在 `src/super_thinking/v6/` 新增代码，**不**触碰 `src/super_thinking/core/`
- [ ] `core/jury.py` 仅追加 `Jury(use_v6=...)` 参数与适配分支，**不**改原 `think` 行为
- [ ] `core/router.py` / `core/registry.py` / `perspectives/*.py` / `fusion/*.py` **不动**
- [ ] `config.yaml` 读取逻辑支持可选 `v6:` 段
- [ ] `tests/test_core.py` 全绿（兼容测试）
- [ ] 新增 `tests/test_v6/` 覆盖 v6 模块
- [ ] `from super_thinking import ...` 与 v5 完全一致
- [ ] Recorder 默认实现不写文件（in_memory），除非显式配置
- [ ] LLM Provider 默认 `openai_compat`，需要 `OPENAI_API_KEY` 或自定义 base_url

---

## 11. 迁移检查清单（给 QA）

- [ ] v5 测试套件 `tests/test_core.py` 通过
- [ ] 跑 `examples/feedback_example.md` 描述的同等流程，输出与 v5 一致
- [ ] 对比 v5 vs v6 适配结果的字段集（`JuryResult` 字段）
- [ ] v6 完整辩论的 Recorder 事件序列与 `v6_DATA_FLOW.md §12` 一致
- [ ] 收敛判定：3 轮满足阈值的脚本化输入，3 轮后 status=CONVERGED
- [ ] 最大轮次兜底：永不收敛的脚本化输入，5 轮后 status=MAX_ROUNDS
- [ ] 用户介入：3 轮未收敛后主持人 ask_user，注入新信息后下一轮收敛
- [ ] 外部咨询：主持人发起咨询超时，session 不崩溃

---

_楚灵 · 迁移策略 Phase 1 · 2026-06-05_
