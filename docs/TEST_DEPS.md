# 测试依赖分析文档

> 项目：超思考 测试环境依赖
> 日期：2026-06-05
> 编写：测试工程师

---

## 一、Python 环境要求

### 1.1 版本要求

| 项目 | 要求 |
|------|------|
| Python 版本 | >= 3.10 |
| 推荐版本 | 3.11 或 3.12 |

### 1.2 pyproject.toml 依赖声明

```toml
[project]
requires-python = ">=3.10"

[project.optional-dependencies]
openclaw = []      # OpenClaw integration hooks
langchain = ["langchain>=0.1.0"]  # LangChain adapter
```

---

## 二、测试框架依赖

### 2.1 核心测试依赖

| 依赖 | 版本 | 用途 | 状态 |
|------|------|------|------|
| `pytest` | - | 主测试框架 | ✅ 已在 pyproject.toml 配置 |
| `pytest-cov` | - | 代码覆盖率 | ❌ 需添加 |
| `pytest-asyncio` | - | 异步测试支持 | ❌ 需添加（v6 辩论可能异步） |
| `pytest-mock` | - | Mock 增强 | ❌ 需添加 |

### 2.2 推荐添加的依赖

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-mock>=3.10.0",
    "pytest-timeout>=2.1.0",
    "pytest-xdist>=3.0.0",  # 并行测试
]
```

### 2.3 AI/LLM 测试依赖

| 依赖 | 版本 | 用途 | 状态 |
|------|------|------|------|
| `unittest.mock` | 内置 | LLM Mock | ✅ Python 内置 |
| `responses` | - | HTTP Mock | ❌ 需添加（LLM API 测试） |
| `aioresponses` | - | 异步 HTTP Mock | ❌ 需添加 |

---

## 三、v6 辩论系统测试依赖

### 3.1 新增依赖需求

| 依赖 | 用途 | 优先级 |
|------|------|--------|
| `pydantic` | 数据模型验证 | 高 |
| `tenacity` | 重试逻辑测试 | 中 |
| ` asyncio` | 异步辩论流程 | 高 |

### 3.2 测试工具建议

| 工具 | 用途 | 建议 |
|------|------|------|
| `faker` | 生成测试数据 | 可选 |
| `hypothesis` | -property 测试 | 高级场景 |
| `tox` | 多环境测试 | 未来考虑 |

---

## 四、项目内模块依赖关系

### 4.1 源代码模块依赖

```
src/super_thinking/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── registry.py          # Registry 类
│   ├── router.py            # Router 类
│   ├── jury.py              # Jury 类
│   ├── extended_registry.py # ExtendedRegistry 类
│   └── llm_router.py        # LLMRouter 类
├── perspectives/
│   ├── __init__.py
│   ├── _interface.py        # PerspectiveOutput
│   └── ...                  # 各专家实现
└── fusion/
    ├── __init__.py
    ├── conflict.py          # ConflictDetector
    └── consensus.py         # ConsensusFinder
```

### 4.2 测试依赖树

```
tests/
├── test_core.py          # 依赖: registry, router, jury, perspective, conflict, consensus
├── test_router.py        # 依赖: extended_registry, llm_router
└── v6/                   # 新增测试
    ├── test_moderator.py          # 依赖: moderator 模块
    ├── test_debate_flow.py        # 依赖: moderator, expert, jury
    ├── test_argument_menu.py      # 依赖: moderator
    ├── test_convergence.py        # 依赖: moderator
    └── test_expert_pool.py        # 依赖: expert_pool
```

---

## 五、测试隔离策略

### 5.1 单元测试隔离

- **Mock 外部依赖**：LLM 调用、网络请求
- **使用 fixtures**：复用 Mock 实例
- **独立数据目录**：测试数据与源码分离

### 5.2 集成测试策略

- **真实依赖**：使用真实的 Registry、Router 等
- **Mock LLM**：使用 FakeLLM 或 MockLLM
- **隔离数据库**：如需持久化，使用临时文件

### 5.3 端到端测试策略

- **真实 LLM 调用**：使用测试 API Key
- **沙盒环境**：与生产环境隔离
- **结果验证**：自动化断言 + 人工复核

---

## 六、测试数据管理

### 6.1 测试数据目录结构

```
tests/
├── fixtures/              # 测试数据文件
│   ├── perspectives/      # 专家配置
│   ├── debates/           # 辩论历史数据
│   └── outputs/           # 期望输出
├── conftest.py           # pytest fixtures
└── v6/
    └── fixtures/         # v6 专用测试数据
```

### 6.2 测试数据格式

```yaml
# tests/fixtures/debates/sample_debate.yaml
debate_id: "test_001"
question: "Should we adopt microservices?"
experts:
  - id: "tech_architect"
    name: "技术架构师"
    initial_view: "..."
context: {}
expected:
  consensus: [...]
  disagreements: [...]
```

---

## 七、环境配置

### 7.1 pytest.ini 配置

```ini
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short"
asyncio_mode = "auto"  # v6 需要
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "e2e: End-to-end tests",
    "slow: Slow running tests",
]
```

### 7.2 conftest.py 示例

```python
# tests/conftest.py
import pytest
import sys
sys.path.insert(0, 'src')

@pytest.fixture
def mock_perspective():
    """Mock perspective for testing."""
    class MockPerspective:
        id = "test_mock"
        name = "Test Mock"
        description = "A mock perspective for testing"
        trigger_keywords = ["test"]
        
        def think(self, input: str, context: dict):
            from super_thinking.perspectives._interface import PerspectiveOutput
            return PerspectiveOutput(
                perspective_id=self.id,
                perspective_name=self.name,
                analysis=f"Mock analysis of: {input[:50]}",
                confidence=0.8,
            )
    return MockPerspective()

@pytest.fixture
def registry(mock_perspective):
    """Fresh registry with mock perspective."""
    from super_thinking.core.registry import Registry
    reg = Registry()
    reg.register(mock_perspective)
    return reg
```

---

## 八、CI/CD 集成

### 8.1 GitHub Actions 工作流

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
      - name: Run tests
        run: pytest --cov=src tests/
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### 8.2 本地开发命令

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行所有测试
pytest

# 带覆盖率
pytest --cov=src --cov-report=html

# 并行测试
pytest -n auto

# 只运行 v6 测试
pytest tests/v6/

# 快速测试（跳过慢速）
pytest -m "not slow"
```

---

## 九、依赖管理最佳实践

1. **明确版本约束**：避免依赖漂移
2. **分离依赖**：`dev` 依赖与生产依赖分离
3. **锁定版本**：生产环境使用 `poetry.lock` 或 `pip-lock`
4. **定期更新**：安全补丁和依赖更新

---

## 十、总结

### 当前状态

| 类型 | 状态 | 说明 |
|------|------|------|
| 核心测试框架 | ✅ | pytest 已配置 |
| 覆盖率工具 | ❌ | 需添加 pytest-cov |
| 异步支持 | ❌ | 需添加 pytest-asyncio |
| CI/CD | ❌ | 需添加 GitHub Actions |

### 建议优先级

1. **高**：添加 `pytest-cov`, `pytest-asyncio`
2. **中**：添加 `pytest-mock`, `responses`
3. **低**：完善 CI/CD 流程

---

_文档版本：1.0_
_最后更新：2026-06-05_
