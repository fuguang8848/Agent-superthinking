# Phase 2.3 测试工程师交接文档

## 任务完成状态
✅ **已完成** — v6 核心模块单元测试（TDD 红端）

## 测试覆盖矩阵

| 模块 | 测试文件 | 测试函数数 | 覆盖率目标 |
|------|----------|------------|------------|
| ExpertPool | test_expert_pool.py | 15 | >=90% |
| MethodologyProvider | test_methodology.py | 12 | >=90% |
| ExternalConsultation | test_external_consultation.py | 10 | >=90% |
| SessionRecorder | test_session_recorder.py | 20 | >=90% |
| UserInteraction | test_user_interaction.py | 15 | >=90% |
| **总计** | **5 个文件** | **72** | — |

## 测试函数分布

### test_expert_pool.py (15 tests)
- TestExpertPoolAddRemove (5): add/remove expert 正确性
- TestExpertPoolConsult (4): consult 同步阻塞行为
- TestExpertPoolSnapshot (4): snapshot 导出状态
- TestExpertPoolEdgeCases (2): 边界条件处理

### test_methodology.py (12 tests)
- TestMethodologyRegistration (3): 18 个方法论注册验证
- TestApplyMethod (5): apply() 返回 Verdict 协议验证
- TestMethodDeclarationParsing (4): 声明解析
- TestSpecificMethodologyCoverage (parametrized): 各方法论覆盖
- TestEdgeCases (3): 异常处理

### test_external_consultation.py (10 tests)
- TestNormalResponse (3): 30s 内正常返回
- TestTimeoutHandling (3): 超时降级
- TestPerRoundLimit (4): 每轮 2 次上限
- TestFailureHistory (5): 失败记录完整性
- TestEdgeCases (3): 边界条件

### test_session_recorder.py (20 tests)
- TestInMemoryRecorder (5): 事件顺序记录
- TestJsonFileRecorder (2): 持久化验证
- TestThreeRoundDump (2): 3 轮完整 dump
- TestSummaryStatistics (5): 关键指标统计
- TestRecorderProtocol (4): 接口协议
- TestEdgeCases (2): 边界条件

### test_user_interaction.py (15 tests)
- TestSyncUserInteraction (5): 阻塞读取
- TestAsyncUserInteraction (5): 非阻塞回调
- TestModeratorRouting (2): 主持人询问路由
- TestEdgeCases (3): 边界条件

## 已知未覆盖项

1. **并发测试**: 未测试 ExpertPool 在多线程环境下的线程安全性
2. **性能基准**: 未包含 pytest-benchmark 性能测试（需后端实现后补充）
3. **集成测试**: 未覆盖 ExpertPool + MethodologyProvider 的交互
4. **错误注入**: 未测试 LLM 调用失败、网络超时等复杂场景

## 运行测试

```bash
cd tests/v6/unit
pytest -v --tb=short

# 带覆盖率
pytest --cov=src.v6.support --cov-report=html
```

## 下一棒建议

1. **backend2**: 实现 src/v6/support/ 下的 5 个模块
2. **backend2**: 确保模块接口与测试 fixture 期望一致
3. **qa2**: 实现 pytest.mark.parametrize 参数化测试扩展
4. **qa2**: 添加性能基准测试 (pytest-benchmark)

## 交接时间
2024-06-05
