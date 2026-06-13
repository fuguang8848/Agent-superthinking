# CI Integration Guide

> **Document Version:** 1.0  
> **Created:** 2024-06-05  
> **Phase:** Phase 3.1 - CI Integration  
> **Author:** QA Team  

---

## 1. Overview

This document describes the CI/CD pipeline for the v6 test suite, including trigger conditions, test execution strategies, and troubleshooting guidelines.

### 1.1 Pipeline Architecture

```
GitHub Actions Workflow: .github/workflows/v6_tests.yml
├── unit-tests (Python 3.10/3.11/3.12 matrix)
├── e2e-tests (Python 3.11)
├── integration-tests (Python 3.11)
├── performance-tests (Python 3.11, opt-in)
└── security-tests (Python 3.11, opt-in)
```

---

## 2. Trigger Conditions Matrix

| Trigger | Unit | E2E | Integration | Performance | Security |
|---------|------|-----|-------------|-------------|----------|
| Push to `main` | ✅ | ✅ | ✅ | ❌ | ❌ |
| Pull Request | ✅ | ✅ | ✅ | ❌ | ❌ |
| `workflow_dispatch` | ✅ | ✅ | ✅ | ✅ | ✅ |
| Commit msg contains `[perf]` | ❌ | ❌ | ❌ | ✅ | ❌ |
| Commit msg contains `[security]` | ❌ | ❌ | ❌ | ❌ | ✅ |

### 2.1 Trigger Examples

```bash
# Trigger performance tests manually
gh workflow run v6_tests.yml --ref main

# Trigger with specific test suite
gh workflow run v6_tests.yml --ref main --field test_suite=performance

# Trigger via commit message
git commit -m "perf: update convergence algorithm"
git push
```

---

## 3. Running Test Subsets

### 3.1 Using pytest Markers

```bash
# Run only unit tests
pytest -m unit tests/v6/

# Run only E2E tests
pytest -m e2e tests/v6/

# Run only integration tests
pytest -m integration tests/v6/

# Run only performance tests
pytest -m performance tests/v6/

# Run only security tests
pytest -m security tests/v6/

# Exclude performance tests (default in CI)
pytest -m "not performance" tests/v6/

# Combine markers
pytest -m "unit and not slow" tests/v6/

# Run v5 compatibility tests
pytest -m v5_compat tests/v6/

# Run v6 normal mode tests
pytest -m v6_normal tests/v6/
```

### 3.2 Using Local Scripts

```bash
# Unix/Linux/macOS
./scripts/run_tests.sh --unit       # Unit tests only
./scripts/run_tests.sh --e2e        # E2E tests only
./scripts/run_tests.sh --perf       # Performance tests
./scripts/run_tests.sh --security   # Security tests
./scripts/run_tests.sh --integration # Integration tests
./scripts/run_tests.sh --all        # All tests
./scripts/run_tests.sh --cov        # With coverage

# Windows PowerShell
.\scripts\run_tests.ps1 -Unit
.\scripts\run_tests.ps1 -E2E
.\scripts\run_tests.ps1 -Perf
.\scripts\run_tests.ps1 -Security
.\scripts\run_tests.ps1 -Integration
.\scripts\run_tests.ps1 -All
.\scripts\run_tests.ps1 -Coverage
```

---

## 4. Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SKIP_LLM` | `1` | Skip tests requiring real LLM API |
| `PYTHONPATH` | project root | Python import path |
| `COVERAGE_FILE` | `.coverage` | Coverage data file location |

### 4.1 Running with Real LLM

```bash
# Enable LLM tests (requires API key)
export SKIP_LLM=0
export OPENAI_API_KEY=sk-...

pytest -m "requires_llm" tests/v6/ -v
```

---

## 5. Failure Troubleshooting

### 5.1 Common Issues

#### Issue: "ModuleNotFoundError: No module named 'super_thinking'"

**Cause:** PYTHONPATH not set correctly.

**Solution:**
```bash
export PYTHONPATH="$(pwd):$PYTHONPATH"
pytest tests/v6/ -v
```

#### Issue: "Permission denied" when running scripts

**Cause:** Script not executable (Unix).

**Solution:**
```bash
chmod +x scripts/run_tests.sh
./scripts/run_tests.sh --all
```

#### Issue: "UnicodeDecodeError" on Windows

**Cause:** PowerShell output encoding issue.

**Solution:**
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
.\scripts\run_tests.ps1 -All
```

#### Issue: "Timeout" during performance tests

**Cause:** Performance tests are slow on CI runners.

**Solution:**
```bash
# Increase timeout
pytest --timeout=600 tests/v6/performance/ -v
```

### 5.2 Debug Mode

```bash
# Run with verbose output
pytest -vv --capture=no tests/v6/unit/test_expert_pool.py -v

# Show local variables on failure
pytest -l tests/v6/unit/test_expert_pool.py -v

# Drop into debugger on failure
pytest --pdb tests/v6/unit/test_expert_pool.py -v

# Show full traceback
pytest --tb=long tests/v6/ -v
```

### 5.3 CI-Specific Debugging

```bash
# Run single job locally
docker run -it --rm \
  -v $(pwd):/workspace \
  -w /workspace \
  python:3.11-slim \
  bash -c "pip install -e . && pytest tests/v6/unit/ -v"
```

---

## 6. Coverage Reports

### 6.1 Local Coverage

```bash
# Generate HTML coverage report
pytest tests/v6/ --cov=src/super_thinking --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### 6.2 CI Coverage

Coverage is automatically uploaded to Codecov when:
1. Tests pass on Python 3.11
2. `coverage.xml` artifact is generated

View coverage at: `https://app.codecov.io/gh/{owner}/{repo}`

---

## 7. Test Categories Reference

### 7.1 Marker Definitions

| Marker | Description | Default CI |
|--------|-------------|------------|
| `unit` | Single-module unit tests | ✅ Run |
| `e2e` | End-to-end scenario tests | ✅ Run |
| `integration` | Multi-module integration tests | ✅ Run |
| `performance` | Benchmark tests | ❌ Opt-in |
| `security` | Security/injection tests | ❌ Opt-in |
| `v5_compat` | v5 compatibility mode tests | ✅ Run |
| `v6_normal` | v6 normal mode tests | ✅ Run |
| `requires_llm` | Tests needing real LLM | ❌ Skip |
| `slow` | Tests >5 seconds | ✅ Run |

### 7.2 Test File Structure

```
tests/v6/
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests
│   ├── test_expert_pool.py
│   ├── test_methodology.py
│   ├── test_external_consultation.py
│   ├── test_session_recorder.py
│   └── test_user_interaction.py
├── e2e/                     # E2E tests
│   ├── test_scenario_a_decision.py
│   ├── test_scenario_b_understanding.py
│   └── ...
├── integration/             # Integration tests
│   ├── test_full_debate_flow.py
│   └── test_v5_compat.py
├── performance/             # Performance tests
│   └── test_benchmarks.py
└── security/                # Security tests
    └── test_injection.py
```

---

## 8. Exit Codes

| Code | Meaning |
|------|---------|
| `0` | All tests passed |
| `1` | Tests failed |
| `2` | Invalid arguments |
| `3` | Collection error |
| `4` | Internal error |

---

## 9. CI Configuration Files

### 9.1 pyproject.toml

```toml
[tool.pytest.ini_options]
testpaths = ["tests/v6"]
addopts = "-v --tb=short --strict-markers"
markers = [
    "unit: Unit tests",
    "e2e: End-to-end tests",
    "integration: Integration tests",
    "performance: Performance benchmarks",
    "security: Security tests",
]
```

### 9.2 GitHub Actions

See `.github/workflows/v6_tests.yml` for complete workflow configuration.

---

*End of CI Integration Guide*
