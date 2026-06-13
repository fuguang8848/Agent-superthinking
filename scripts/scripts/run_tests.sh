#!/usr/bin/env bash
# -*- coding: utf-8 -*-
"""
V6 Test Runner Script (Unix/Linux/macOS)
=========================================
Usage:
    ./scripts/run_tests.sh --unit       # Run unit tests only
    ./scripts/run_tests.sh --e2e        # Run E2E tests only
    ./scripts/run_tests.sh --perf       # Run performance benchmarks
    ./scripts/run_tests.sh --security   # Run security tests
    ./scripts/run_tests.sh --integration # Run integration tests
    ./scripts/run_tests.sh --all        # Run all tests
    ./scripts/run_tests.sh --cov       # Run with coverage report

Exit codes:
    0 - All tests passed
    1 - Tests failed
    2 - Invalid arguments
"""

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Default values
TEST_SUITE=""
RUN_COVERAGE=false
PYTEST_ARGS=()

# ──────────────────────────────────────────────────────────────────────
# Helper Functions
# ──────────────────────────────────────────────────────────────────────
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

show_help() {
    head -40 "$0" | grep "^# " | sed 's/^# //'
}

# ──────────────────────────────────────────────────────────────────────
# Virtual Environment Activation
# ──────────────────────────────────────────────────────────────────────
activate_venv() {
    local venv_dir="$PROJECT_ROOT/.venv"
    local venv_bin=""
    
    # Detect OS and set venv binary path
    if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
        venv_bin="$venv_dir/bin"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        venv_bin="$venv_dir/Scripts"
    fi
    
    if [[ -d "$venv_dir" ]] && [[ -d "$venv_bin" ]]; then
        log_info "Activating virtual environment: $venv_dir"
        source "$venv_dir/bin/activate" 2>/dev/null || source "$venv_dir/Scripts/activate" 2>/dev/null
    else
        log_warning "Virtual environment not found at $venv_dir, using system Python"
    fi
}

# ──────────────────────────────────────────────────────────────────────
# Parse Arguments
# ──────────────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case $1 in
        --unit)
            TEST_SUITE="unit"
            shift
            ;;
        --e2e)
            TEST_SUITE="e2e"
            shift
            ;;
        --perf|--performance)
            TEST_SUITE="performance"
            shift
            ;;
        --security)
            TEST_SUITE="security"
            shift
            ;;
        --integration)
            TEST_SUITE="integration"
            shift
            ;;
        --all)
            TEST_SUITE="all"
            shift
            ;;
        --cov|--coverage)
            RUN_COVERAGE=true
            shift
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 2
            ;;
    esac
done

# Default to all tests if no suite specified
TEST_SUITE="${TEST_SUITE:-all}"

# ──────────────────────────────────────────────────────────────────────
# Setup Python Environment
# ──────────────────────────────────────────────────────────────────────
activate_venv

# Check Python version
PYTHON_VERSION=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "unknown")
log_info "Python version: $PYTHON_VERSION"

# ──────────────────────────────────────────────────────────────────────
# Run Tests
# ──────────────────────────────────────────────────────────────────────
cd "$PROJECT_ROOT"

# Set environment variables
export SKIP_LLM="${SKIP_LLM:-1}"
export PYTHONPATH="$PROJECT_ROOT:${PYTHONPATH:-}"

# Base pytest command
PYTEST_CMD="python -m pytest tests/v6/"

# Add coverage if requested
if [[ "$RUN_COVERAGE" == true ]]; then
    PYTEST_CMD="$PYTEST_CMD --cov=src/super_thinking --cov-report=term-missing --cov-report=html"
fi

# Add test suite specific options
case $TEST_SUITE in
    unit)
        log_info "Running UNIT tests..."
        PYTEST_ARGS=("-v" "--tb=short" "-m" "unit" "tests/v6/unit/")
        ;;
    e2e)
        log_info "Running E2E tests..."
        PYTEST_ARGS=("-v" "--tb=short" "-m" "e2e" "tests/v6/e2e/")
        ;;
    performance)
        log_info "Running PERFORMANCE tests..."
        PYTEST_ARGS=("-v" "--tb=short" "-m" "performance" "--benchmark-only" "tests/v6/performance/")
        ;;
    security)
        log_info "Running SECURITY tests..."
        PYTEST_ARGS=("-v" "--tb=short" "-m" "security" "tests/v6/security/")
        ;;
    integration)
        log_info "Running INTEGRATION tests..."
        PYTEST_ARGS=("-v" "--tb=short" "-m" "integration" "tests/v6/integration/")
        ;;
    all)
        log_info "Running ALL tests (excluding performance by default)..."
        PYTEST_ARGS=("-v" "--tb=short" "-m" "not performance" "tests/v6/")
        ;;
esac

# Execute pytest
log_info "Command: $PYTEST_CMD ${PYTEST_ARGS[*]}"
echo ""

if $PYTEST_CMD "${PYTEST_ARGS[@]}"; then
    echo ""
    log_success "All $TEST_SUITE tests passed!"
    exit 0
else
    echo ""
    log_error "Some $TEST_SUITE tests failed!"
    exit 1
fi
