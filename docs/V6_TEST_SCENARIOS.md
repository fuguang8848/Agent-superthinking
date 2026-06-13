# v6 测试场景规划

> 项目：超思考 v6 Multi-Agent 圆桌辩论 测试场景
> 日期：2026-06-05
> 编写：测试工程师

---

## 一、v6 核心功能模块

根据 DELIVERY.md 和 ARCHITECTURE.md，v6 包含以下核心模块：

### 1.1 待测试模块列表

| 模块 | 描述 | 测试优先级 |
|------|------|-----------|
| `Moderator` | 主持人 - 辩论协调者 | P0 |
| `Expert` | 专家 - 辩论参与者 | P0 |
| `ArgumentMenu` | 论点菜单提取 | P0 |
| `ConvergenceDetector` | 收敛判断 | P1 |
| `ExpertPool` | 动态专家池 | P1 |
| `MethodologyPool` | 方法论工具池 | P2 |
| `DebateFlow` | 辩论流程编排 | P0 |
| `MeetingConclusion` | 会议结论生成 | P1 |

---

## 二、功能测试场景

### 2.1 Moderator 模块测试

#### 场景 1：初始化辩论会议

```python
def test_moderator_initialize_debate():
    """
    Given: 用户提出一个问题
    When:  主持人初始化辩论
    Then:  选择专家组合，生成会议ID，状态为 initialized
    """
```

**测试用例：**

| ID | 场景 | 预期结果 |
|----|------|----------|
| MOD-001 | 正常初始化 | 生成唯一会议ID，状态正确 |
| MOD-002 | 空问题 | 抛出 ValidationError |
| MOD-003 | 超长问题 | 截断或报错 |
| MOD-004 | 特殊字符问题 | 正常处理 |

#### 场景 2：论点菜单提取

```python
def test_argument_menu_extraction():
    """
    Given: 专家发言列表
    When:  主持人提取论点菜单
    Then:  生成标准格式的论点菜单
    """
```

**测试用例：**

| ID | 场景 | 预期结果 |
|----|------|----------|
| AM-001 | 有效论点提取 | 四标准全部满足的论点被提取 |
| AM-002 | 过滤泛泛而谈 | 无具体判断的发言被过滤 |
| AM-003 | 过滤无可反驳内容 | 无明确判断被过滤 |
| AM-004 | 过滤无理由发言 | 只有观点无理由被过滤 |
| AM-005 | 过滤无分歧内容 | 与其他专家完全相同的论点被过滤 |

#### 场景 3：收敛判断

```python
def test_convergence_detection():
    """
    Given: 多轮辩论记录
    When:  主持人判断收敛
    Then:  返回收敛状态和信号数据
    """
```

**测试用例：**

| ID | 场景 | 预期结果 |
|----|------|----------|
| CONV-001 | 论点重叠率上升 | 返回 converging |
| CONV-002 | 新论点密度降低 | 返回 converging |
| CONV-003 | 置信度变化趋势 | 计算正确 |
| CONV-004 | 分歧持续 | 返回 not_converging |
| CONV-005 | 达到最大轮次 | 返回 max_rounds_reached |

#### 场景 4：用户询问

```python
def test_user_question_prompt():
    """
    Given: 分歧无法收敛
    When:  主持人向用户询问
    Then:  生成清晰的问题，返回等待状态
    """
```

**测试用例：**

| ID | 场景 | 预期结果 |
|----|------|----------|
| UQ-001 | 生成有效问题 | 问题具体、可回答 |
| UQ-002 | 多分歧点 | 优先询问核心分歧 |
| UQ-003 | 用户回答 | 更新上下文，继续辩论 |

---

### 2.2 Expert 模块测试

#### 场景 1：专家发言格式验证

```python
def test_expert_speech_format():
    """
    Given: 专家生成发言
    When:  验证发言格式
    Then:  必须包含针对格式，可选自由补充
    """
```

**测试用例：**

| ID | 场景 | 预期结果 |
|----|------|----------|
| EXP-001 | 完整针对格式 | 通过验证 |
| EXP-002 | 缺少针对格式 | 格式错误，标记 |
| EXP-003 | 包含自由补充 | 正确识别 |
| EXP-004 | 针对不存在论点 | 标记警告 |

#### 场景 2：专家视角保持

```python
def test_expert_perspective_consistency():
    """
    Given: 多轮辩论
    When:  专家发言
    Then:  保持初始视角一致，不偏离角色
    """
```

**测试用例：**

| ID | 场景 | 预期结果 |
|----|------|----------|
| EXP-010 | 视角一致 | 专家角色保持 |
| EXP-011 | 过度妥协 | 标记警告 |
| EXP-012 | 完全改变立场 | 标记警告 |

---

### 2.3 ExpertPool 模块测试

#### 场景 1：专家加入

```python
def test_expert_join_debate():
    """
    Given: 辩论进行中
    When:  新专家加入
    Then:  同步上下文，专家参与下一轮
    """
```

**测试用例：**

| ID | 场景 | 预期结果 |
|----|------|----------|
| EP-001 | 正式加入 | 上下文同步，参与下一轮 |
| EP-002 | 外部咨询 | 不参与辩论，主持人获取意见 |
| EP-003 | 加入时上下文格式 | 包含核心论点，非完整历史 |

#### 场景 2：专家离开

```python
def test_expert_leave_debate():
    """
    Given: 辩论进行中
    When:  专家主动或被动离开
    Then:  记录离开原因，不再参与后续
    """
```

**测试用例：**

| ID | 场景 | 预期结果 |
|----|------|----------|
| EP-010 | 主动离开 | 标记 exit，记录原因 |
| EP-011 | 被请离（偏离论题） | 标记 removed |
| EP-012 | 离开后发言请求 | 忽略 |

---

### 2.4 DebateFlow 模块测试

#### 场景 1：完整辩论流程

```python
def test_complete_debate_flow():
    """
    Given: 用户问题
    When:  执行完整辩论流程
    Then:  经过初始化→第一轮→多轮→结论
    """
```

**测试用例：**

| ID | 场景 | 预期结果 |
|----|------|----------|
| FLOW-001 | 正常流程 | 初始化→第一轮→N轮→结论 |
| FLOW-002 | 首轮收敛 | 直接进入最终陈述 |
| FLOW-003 | 最大轮次收敛 | 最后进入最终陈述 |
| FLOW-004 | 用户询问后继续 | 暂停→询问→继续 |
| FLOW-005 | 异常中断 | 正确处理，保存状态 |

#### 场景 2：多轮辩论状态

```python
def test_multi_round_state():
    """
    Given: 辩论进行到第N轮
    When:  访问辩论状态
    Then:  返回当前轮次、论点历史、收敛信号
    """
```

**测试用例：**

| ID | 场景 | 预期结果 |
|----|------|----------|
| FLOW-010 | 状态完整 | 包含所有必要信息 |
| FLOW-011 | 历史记录 | 论点菜单可追溯 |
| FLOW-012 | 并发访问 | 状态一致 |

---

## 三、性能测试场景

### 3.1 响应时间基准

| 场景 | 目标 | SLA |
|------|------|-----|
| 单轮辩论响应 | < 5s | 95th percentile |
| 主持人初始化 | < 2s | 95th percentile |
| 论点菜单提取 | < 1s | 95th percentile |
| 收敛判断 | < 500ms | 95th percentile |

### 3.2 压力测试

```python
def test_concurrent_debates():
    """
    Given: 多用户同时发起辩论
    When:  系统处理
    Then:  响应时间符合SLA，无资源泄漏
    """
```

**测试用例：**

| ID | 场景 | 预期结果 |
|----|------|----------|
| PERF-001 | 10 并发辩论 | 响应时间 < 10s |
| PERF-002 | 50 并发辩论 | 系统不崩溃 |
| PERF-003 | 内存泄漏检测 | 运行 1 小时内存稳定 |

---

## 四、安全测试场景

### 4.1 Prompt 注入防护

```python
def test_prompt_injection_protection():
    """
    Given: 恶意输入包含 prompt 注入
    When:  处理专家发言
    Then:  注入被检测或中和，不影响系统行为
    """
```

**测试用例：**

| ID | 注入类型 | 预期结果 |
|----|---------|----------|
| SEC-001 | 角色扮演逃逸 | 系统拒绝或中和 |
| SEC-002 | 指令覆盖 | 忽略恶意指令 |
| SEC-003 | 上下文污染 | 隔离处理 |
| SEC-004 | 特殊字符注入 | 安全转义 |

### 4.2 输入验证

| 场景 | 测试输入 | 预期结果 |
|------|---------|----------|
| 空输入 | "" | 拒绝或默认值 |
| 超长输入 | 100KB 文本 | 截断或拒绝 |
| 恶意URL | `javascript:...` | 转义或拒绝 |
| SQL 注入 | `' OR 1=1 --` | 参数化处理 |
| 路径遍历 | `../../etc/passwd` | 拒绝 |

---

## 五、AI 特有测试场景

### 5.1 幻觉率检测

**目标：** 幻觉率 ≤ 5%

```python
def test_hallucination_detection():
    """
    Given: 专家发言
    When:  检测幻觉内容
    Then:  标记高风险内容，置信度调整
    """
```

**测试用例：**

| ID | 场景 | 预期结果 |
|----|------|----------|
| HALL-001 | 事实性错误 | 标记 low_confidence |
| HALL-002 | 不可验证声明 | 标记 unverified |
| HALL-003 | 统计数据 | 验证来源 |
| HALL-004 | 专业术语误用 | 标记 warning |

### 5.2 一致性测试

```python
def test_cross_expert_consistency():
    """
    Given: 多专家发言
    When:  检查一致性
    Then:  检测矛盾点，标记讨论价值
    """
```

**测试用例：**

| ID | 场景 | 预期结果 |
|----|------|----------|
| CONS-001 | 直接矛盾 | 标记 conflict |
| CONS-002 | 隐含矛盾 | 标记 potential_conflict |
| CONS-003 | 互补观点 | 标记 complementary |
| CONS-004 | 完全一致 | 标记 consensus |

---

## 六、集成测试场景

### 6.1 端到端辩论

```python
@pytest.mark.e2e
def test_end_to_end_debate():
    """
    完整辩论场景测试：
    1. 用户提问
    2. 主持人初始化
    3. 专家第一轮发言
    4. 论点菜单提取
    5. 多轮辩论
    6. 收敛判断
    7. 最终陈述
    8. 会议结论
    9. 用户 LLM 综合
    """
```

### 6.2 异常流程

| 场景 | 测试步骤 | 预期结果 |
|------|---------|----------|
| 专家掉线 | 辩论中专家无响应 | 记录为 failed，主持人决定继续或替换 |
| LLM 超时 | API 调用超时 | 重试或降级处理 |
| 网络中断 | 保存辩论状态 | 恢复后继续 |

---

## 七、测试执行计划

### 7.1 阶段划分

| 阶段 | 内容 | 优先级 |
|------|------|--------|
| Phase 1 | 目录骨架 + Mock | P0 |
| Phase 2 | Moderator 核心测试 | P0 |
| Phase 3 | DebateFlow 集成测试 | P0 |
| Phase 4 | ExpertPool 测试 | P1 |
| Phase 5 | Convergence 测试 | P1 |
| Phase 6 | 性能测试 | P2 |
| Phase 7 | 安全测试 | P2 |
| Phase 8 | AI 对抗性测试 | P2 |

### 7.2 目录结构

```
tests/v6/
├── __init__.py
├── conftest.py              # v6 fixtures
├── test_moderator.py       # 主持人测试
├── test_debate_flow.py     # 辩论流程测试
├── test_argument_menu.py   # 论点菜单测试
├── test_convergence.py     # 收敛判断测试
├── test_expert_pool.py     # 专家池测试
├── test_expert_speech.py   # 专家发言测试
├── test_methodology.py     # 方法论测试
├── fixtures/               # 测试数据
│   ├── debates/           # 辩论数据
│   ├── experts/           # 专家配置
│   └── outputs/           # 期望输出
├── performance/           # 性能测试
│   └── test_benchmarks.py
├── security/              # 安全测试
│   └── test_injection.py
└── ai/                    # AI 特有测试
    └── test_hallucination.py
```

---

## 八、测试覆盖率目标

| 模块 | 覆盖率目标 | 说明 |
|------|-----------|------|
| Moderator | 90% | 核心协调逻辑 |
| DebateFlow | 100% | 关键路径 |
| ExpertPool | 85% | 动态行为 |
| ArgumentMenu | 95% | 规则逻辑 |
| ConvergenceDetector | 80% | 算法逻辑 |

---

## 九、验收标准

### 9.1 功能验收

- [ ] 所有 P0 测试通过
- [ ] 辩论流程端到端可运行
- [ ] 论点菜单提取符合四标准
- [ ] 收敛判断逻辑正确

### 9.2 性能验收

- [ ] 单轮响应 < 5s（95th percentile）
- [ ] 无内存泄漏
- [ ] 10 并发正常运行

### 9.3 安全验收

- [ ] Prompt 注入防护有效
- [ ] 输入验证完整
- [ ] 无高危漏洞

### 9.4 AI 质量验收

- [ ] 幻觉率检测机制就绪
- [ ] 置信度校准逻辑实现

---

_文档版本：1.0_
_最后更新：2026-06-05_
