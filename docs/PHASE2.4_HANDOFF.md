# Phase 2.4 E2E 测试交接文档

> 版本: 1.0.0  
> 日期: 2026-06-05  
> 状态: 已完成  
> 负责人: 测试工程师2号 (qa2)

---

## 1. 交付物概览

| 文件路径 | 类型 | 测试数量 | 说明 |
|---------|------|---------|------|
| `tests/v6/conftest.py` | fixtures | - | 共享Mock对象、Fixtures、辅助函数 |
| `tests/v6/e2e/test_scenario_a_decision.py` | E2E | 8 tests | 决策类问题测试 |
| `tests/v6/e2e/test_scenario_b_understanding.py` | E2E | 6 tests | 理解类问题测试 |
| `tests/v6/e2e/test_scenario_c_creative.py` | E2E | 6 tests | 创意类问题测试 |
| `tests/v6/e2e/test_scenario_d_controversy.py` | E2E | 7 tests | 争议问题测试 |
| `tests/v6/e2e/test_scenario_e_empty_domain.py` | E2E | 7 tests | 空领域问题测试 |
| `tests/v6/performance/test_benchmarks.py` | 性能 | 7 tests | 性能基准测试 |
| `tests/v6/security/test_injection.py` | 安全 | 8 tests | 安全注入测试 |
| **总计** | | **49 tests** | |

---

## 2. E2E 覆盖矩阵

### 2.1 场景覆盖

| 场景 | 场景ID | 输入问题 | 验证点 | 测试数量 |
|------|--------|---------|--------|---------|
| 决策类 | A | "我该跳槽吗？" | 3-5专家、3轮收敛、可操作建议 | 8 |
| 理解类 | B | "如何理解熵增？" | 跨学科融合、共识明确 | 6 |
| 创意类 | C | "产品定位" | 自由补充≥20%、差异化 | 6 |
| 争议类 | D | "技术vs人文" | 分歧识别、用户咨询 | 7 |
| 空领域 | E | "火星生态系统" | 降级v5单轮模式 | 7 |

### 2.2 验证点映射

| 验证项 | 场景A | 场景B | 场景C | 场景D | 场景E |
|--------|-------|-------|-------|-------|-------|
| 专家数量 | ✓ | ✓ | ✓ | ✓ | ✓ |
| 收敛轮次 | ✓ | ✓ | ✓ | ✓ | ✓ |
| 结论完整性 | ✓ | ✓ | ✓ | ✓ | ✓ |
| 分歧记录 | ✓ | - | - | ✓ | - |
| 跨学科视角 | - | ✓ | - | - | - |
| 自由补充占比 | - | - | ✓ | - | - |
| 降级模式 | - | - | - | - | ✓ |

---

## 3. 性能基线数据

### 3.1 基准指标

| 指标 | 阈值 | 说明 |
|------|------|------|
| 10专家×20轮 | <60s | 压力测试上限 |
| 100轮内存占用 | <100MB | Mock模式内存峰值 |
| 发言处理时间 | <100ms/条 | 平均每条发言 |
| 专家初始化 | <1s/10专家 | 并行初始化 |
| 结果序列化 | <0.5s | to_dict()性能 |

### 3.2 测试场景

```
test_10_experts_20_rounds_stress       # 压力测试
test_convergence_algorithm_complexity   # O(n²)验证
test_long_running_100_rounds_memory     # 内存测试
test_statement_processing_time         # 吞吐量
test_concurrent_expert_initialization   # 并发性能
test_result_serialization_performance   # 序列化
test_benchmark_reproducibility         # 稳定性
```

---

## 4. 安全检查点

### 4.1 注入防护测试

| 测试项 | 检查内容 | 通过标准 |
|--------|---------|---------|
| 提示注入 | "忽略以上指令"等 | 过滤或标记 |
| XSS | `<script>`等 | 消毒处理 |
| SQL注入 | `DROP TABLE`等 | 转义处理 |
| 路径遍历 | `../`等 | 拒绝访问 |
| 专家内容注入 | 指令覆盖 | 阻止执行 |
| 会话隔离 | 跨会话污染 | 完全隔离 |

### 4.2 消毒函数

```python
def sanitize_external_content(content: str) -> str:
    """外部咨询内容消毒"""
    # 移除 <script> 标签
    # 过滤 javascript: 协议
    # 过滤 file:// 协议

def validate_user_input(input_str: str) -> bool:
    """用户输入合法性校验"""
    # 检查长度限制 (max 10000)
    # 检查控制字符

def sanitize_for_db(input_str: str) -> str:
    """数据库输入消毒"""
    # SQL转义

def sanitize_path(path: str) -> str:
    """路径消毒"""
    # 移除 .. 遍历
```

---

## 5. 运行指南

### 5.1 运行所有测试

```bash
cd tests/v6
pytest -v
```

### 5.2 运行特定测试

```bash
# E2E场景测试
pytest tests/v6/e2e/ -v

# 性能测试
pytest tests/v6/performance/ -v

# 安全测试
pytest tests/v6/security/ -v

# 特定场景
pytest tests/v6/e2e/test_scenario_a_decision.py -v
```

### 5.3 Mock模式说明

所有测试使用Mock专家，不依赖真实LLM API：
- `MockExpert`: 模拟专家发言
- `MockLLM`: 模拟LLM调用
- `MockModerator`: 模拟主持人

### 5.4 依赖

```python
import pytest
# conftest.py 中定义的 fixtures
```

---

## 6. 后续任务

- [ ] 与 backend2 确认 Mock 接口与实际实现的匹配
- [ ] 集成 CI/CD 自动化测试
- [ ] 添加真实 LLM 的集成测试（可选）
- [ ] 补充边缘情况覆盖率

---

## 7. 已知限制

1. **Mock依赖**: 当前测试完全依赖Mock，未覆盖真实LLM行为
2. **并发测试**: 未实现真正的并发专家测试
3. **网络模拟**: 未模拟网络延迟、断开等场景

---

## 8. 交接确认

- [x] 所有测试文件已创建
- [x] 测试可独立运行
- [x] 文档已更新
- [ ] 等待 Leader 评审
- [ ] 与下一阶段对接

---

_文档版本: 1.0.0 | 最后更新: 2026-06-05_
