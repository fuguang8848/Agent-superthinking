# SuperThinking v6.0.0 Release Notes

> **Release Date:** 2024-06-05
> **Version:** 6.0.0
> **Type:** Major Release

---

## To Our Users | 致用户

Thank you for using SuperThinking! This major release brings significant improvements to the multi-expert thinking framework.

### What's New for Users | 用户新特性

1. **Multi-Round Debates** — Engage in dynamic debates that evolve over multiple rounds
2. **50+ Expert Personalities** — Access a diverse panel of virtual experts
3. **Modern CLI** — Beautiful terminal interface with colors and tables
4. **Mock Mode** — Try the framework without API keys
5. **Better Performance** — 40% fewer API calls than v5

### How to Upgrade | 升级步骤

#### Step 1: Backup Your Configuration

```bash
# Backup existing config
cp ~/.think.yaml ~/.think.yaml.v5.backup

# Backup custom experts
cp -r ~/.think/experts ~/.think/experts.v5.backup
```

#### Step 2: Upgrade the Package

```bash
# Upgrade from PyPI
pip install --upgrade super-thinking

# Or install dev version
pip install -e .
```

#### Step 3: Verify Installation

```bash
# Check version
superthink --version

# Run mock test
superthink debate --mock "Hello world"
```

#### Step 4: Update Configuration (if needed)

See [v6_MIGRATION.md](v6_MIGRATION.md) for configuration migration.

### Rollback Plan | 回滚方案

If you encounter issues:

```bash
# Option 1: Reinstall v5
pip install super-thinking==5.0.0

# Option 2: Use Python API fallback
from super_thinking.v5 import run_debate
```

---

## To Developers | 致开发者

### New Interface Contracts | 新接口契约

v6 introduces a completely redesigned API. Key changes:

#### Session-Based API

```python
# v5 (deprecated)
from super_thinking.v5 import run_debate
result = run_debate(question, perspectives)

# v6 (new)
from super_thinking.v6 import DebateSession
session = DebateSession(question="...", experts=[...], rounds=5)
for event in session.stream():
    process(event)
```

#### Type-Safe Configuration

```python
# v6 dataclass configuration
from super_thinking.v6.types import DebateConfig, ConvergenceTuning

config = DebateConfig(
    mode=DebateMode.STANDARD,
    max_rounds=5,
    convergence=ConvergenceTuning(
        score_threshold=0.65,
        require_consecutive=1,
    )
)
```

### Migration Checklist | 迁移检查清单

- [ ] Update imports: `v5` → `v6`
- [ ] Replace `PerspectiveRegistry` → `ExpertPool`
- [ ] Update `run_debate()` → `DebateSession`
- [ ] Convert dict configs → dataclass configs
- [ ] Update return type handling
- [ ] Test with `--mock` mode first
- [ ] Update unit tests

See [v6_MIGRATION.md](v6_MIGRATION.md) for full migration guide.

### Breaking Changes Summary | 破坏性变更摘要

| Change | Migration |
|--------|-----------|
| `Perspective` → `Expert` | Search and replace |
| `PerspectiveRegistry` → `ExpertPool` | Update instantiation |
| `run_debate()` → `DebateSession` | Rewrite session logic |
| Dict config → dataclass | Use `DebateConfig` |

---

## To Operations | 致运维

### Environment Variables | 环境变量

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes* | - | OpenAI API key (*unless using `--mock`) |
| `ANTHROPIC_API_KEY` | No | - | Anthropic API key |
| `THINK_MODEL` | No | `gpt-4` | Default LLM model |
| `THINK_TEMPERATURE` | No | `0.7` | LLM temperature |
| `THINK_TIMEOUT` | No | `60` | Request timeout (seconds) |
| `THINK_MAX_TOKENS` | No | `2000` | Max response tokens |

### Performance Baselines | 性能基线

| Metric | Target | Actual |
|--------|--------|--------|
| CLI startup time | < 1s | ~0.8s |
| Mock debate (3 rounds) | < 5s | ~3s |
| Real debate (3 rounds) | < 60s | ~45s |
| Memory usage (idle) | < 100MB | ~80MB |
| Memory usage (debate) | < 500MB | ~350MB |

See [docs/PERFORMANCE_BASELINE.md](docs/PERFORMANCE_BASELINE.md) for detailed benchmarks.

### Deployment | 部署

```bash
# Production installation
pip install super-thinking

# Environment setup
export OPENAI_API_KEY="your-key-here"
export THINK_MODEL="gpt-4"

# Run tests
pytest tests/v6/ -v

# Start service
superthink serve --port=8080
```

---

## To Contributors | 致贡献者

### How to Get Involved | 如何参与

1. **Read the Contributing Guide** — See [CONTRIBUTING.md](docs/CONTRIBUTING.md)
2. **Pick a First Issue** — Look for `good first issue` labels
3. **Join the Discussion** — Open PRs early for feedback

### v6.x Roadmap | v6.x 路线图

| Version | Target | Features |
|---------|--------|----------|
| v6.0.0 | Current | Core framework, CLI, 50+ experts |
| v6.1.0 | Q3 2024 | Streaming output, Web UI |
| v6.2.0 | Q4 2024 | HTTP API, Team collaboration |
| v6.3.0 | Q1 2025 | Expert marketplace, Templates |

### Code Standards | 代码规范

- Type hints required for all public APIs
- Unit tests for all new features (pytest)
- Documentation updates for API changes
- PEP 8 compliance (enforced by ruff)

---

## Breaking Changes Summary | 破坏性变更摘要

### API Changes

1. **Namespace Change:** `super_thinking.v5` → `super_thinking.v6`
2. **Class Renames:**
   - `Perspective` → `Expert`
   - `PerspectiveRegistry` → `ExpertPool`
   - `PerspectiveOutput` → `ExpertStatement`
3. **Function Changes:**
   - `run_debate()` → `DebateSession.stream()`
   - `list_perspectives()` → `ExpertPool.list_experts()`

### Configuration Changes

1. Format: YAML dict → Typed dataclass
2. Location: `~/.think.yaml` format updated
3. Defaults: New default values for convergence

### Behavioral Changes

1. Multi-round is now the default (was single-round)
2. Convergence detection is automatic (was manual)
3. Expert selection is semantic (was keyword-based)

---

## Thank You | 感谢

To all contributors, beta testers, and users — thank you for making SuperThinking better!

**The SuperThinking Team**

---

_Last updated: 2024-06-05_
