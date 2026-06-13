# Phase 2.5 交接文档

> 日期：2026-06-06
> 状态：核心辩论模块实现完成
> 负责人：后端工程师2号

## 已实现模块清单

### 核心辩论模块（Phase 2.5）

| 模块文件 | 功能 | 状态 |
|---------|------|------|
| `argument_menu.py` | 论点菜单 + StructuredExtractor + merge/compute | ✅ 完成 |
| `expert_statement.py` | 双轨发言解析 + 验证器 | ✅ 完成 |
| `convergence.py` | 收敛算法实现（0.4·overlap + 0.4·(1−density) + 0.2·(1−drift)）| ✅ 完成 |
| `moderator.py` | 主持人编排逻辑 | ✅ 完成 |
| `orchestrator.py` | 顶层协调器入口 | ✅ 完成 |
| `compat.py` | v5 兼容层 | ✅ 完成 |
| `__init__.py` | 公共 API 导出 | ✅ 完成 |
| `types.py` | 补充完整类型定义 | ✅ 完成 |

### 支撑模块（Phase 2.1）

| 模块文件 | 功能 | 状态 |
|---------|------|------|
| `expert_pool.py` | 动态专家池 | ✅ 已完成 |
| `methodology.py` | 18 个方法论内置注册 | ✅ 已完成 |
| `external_consultation.py` | 外部咨询（30s 超时降级）| ✅ 已完成 |
| `session_recorder.py` | InMemory + JsonFile Recorder | ✅ 已完成 |
| `user_interaction.py` | Async/Sync/Mock 实现 | ✅ 已完成 |

---

## 核心算法说明

### 收敛算法

```python
score = 0.4·overlap + 0.4·(1−new_arg_density) + 0.2·(1−drift)
```

**参数说明：**
- `overlap`: Jaccard 相似度（论点 claim 文本交集/并集）
- `new_arg_density`: 每专家平均新论点数量（归一化到 [0,1]）
- `drift`: 跨专家平均置信度漂移

**收敛条件：**
- 软收敛：`score >= 0.65` 持续 `require_consecutive=1` 轮
- 硬收敛：`overlap >= 0.70` 且 `new_arg_density <= 0.50`

### 双轨发言格式

```text
针对"论点A"的反驳内容...

【自由补充】
补充的观点...
```

---

## 与 v5 兼容示例

### 环境变量控制
```python
import os
os.environ["SUPER_THINKING_LEGACY"] = "1"  # 启用 v5 兼容模式
```

### 单轮非辩论模式
```python
from super_thinking.v6 import DebateConfig, DebateMode, run_debate

config = DebateConfig(
    mode=DebateMode.NON_DEBATE,  # 等价于 v5 Jury().think()
    max_rounds=1,
)
session = run_debate(question, config, ...)
```

### v6 多轮辩论模式
```python
from super_thinking.v6 import DebateConfig, DebateMode, run_debate

config = DebateConfig(
    mode=DebateMode.STANDARD,
    max_rounds=5,
    convergence=ConvergenceTuning(
        score_threshold=0.65,
        require_consecutive=1,
    ),
)
session = run_debate(question, config, ...)
```

---

## 已知限制

1. **LLM Provider 未实现**：需要第三方提供 LLM 实现（OpenAI/Anthropic 等）
2. **专家注册需手动**：ExpertPool.suggest_for 依赖 trigger_keywords 匹配
3. **方法论调用需完善**：MethodologyProvider.call 的实际执行逻辑需与 LLM 集成
4. **JSON 文件记录器**：路径处理在 Windows 上可能有兼容性问题
5. **单元测试覆盖率**：收敛算法有基本测试，moderator/orchestrator 需补充

---

## 下一棒建议

### 高优先级

1. **LLMProvider 实现**
   - 位置：`src/super_thinking/v6/llm/`
   - 参考：`src/super_thinking/v6/llm/provider.py`（Protocol 定义）
   - 需要实现：OpenAI / Anthropic / 本地模型适配

2. **V5PerspectiveAdapter 实现**
   - 位置：`src/super_thinking/v6/expert/v5_adapter.py`
   - 参考：v6_INTERFACES.md 4.1 节
   - 将 v5 Perspective 适配为 v6 Expert

3. **单元测试补充**
   - `test_convergence.py`：收敛算法边界测试
   - `test_moderator.py`：决策逻辑测试
   - `test_orchestrator.py`：完整流程测试

### 中优先级

4. **CLI 界面**
   - 位置：`src/super_thinking/v6/cli/`
   - 参考：`src/super_thinking/v6/cli/` 目录
   - 实现交互式辩论界面

5. **方法论增强**
   - 完善 18 个方法论的实现细节
   - 添加方法论组合推荐

---

## 文件位置

```
src/super_thinking/v6/
├── __init__.py          # 公共 API
├── types.py             # 基础类型 + Protocol
├── argument_menu.py      # 论点菜单
├── expert_statement.py  # 发言解析
├── convergence.py       # 收敛算法
├── moderator.py         # 主持人
├── orchestrator.py      # 协调器
├── compat.py           # v5 兼容
├── expert_pool.py      # (Phase 2.1)
├── methodology.py       # (Phase 2.1)
├── external_consultation.py  # (Phase 2.1)
├── session_recorder.py # (Phase 2.1)
└── user_interaction.py # (Phase 2.1)
```

---

## 验证清单

- [x] 18 个方法论可注册
- [x] ExpertPool 支持 add/remove 循环
- [x] Recorder 可记录 3 轮辩论并 dump JSON
- [x] 同步咨询 30s 超时降级
- [x] 收敛算法按公式实现
- [x] 双轨发言解析器可用
- [x] v5 兼容模式可切换
- [ ] 单元测试覆盖（待补充）

---

**后端工程师2号 · 2026-06-06**
