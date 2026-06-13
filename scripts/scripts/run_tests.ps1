# -*- coding: utf-8 -*-
<#
.SYNOPSIS
    V6 Test Runner Script (Windows PowerShell)
.DESCRIPTION
    Run v6 test suite with various options for different test categories.
    
    Usage:
        .\run_tests.ps1 -Unit       # Run unit tests only
        .\run_tests.ps1 -E2E       # Run E2E tests only
        .\run_tests.ps1 -Perf       # Run performance benchmarks
        .\run_tests.ps1 -Security   # Run security tests
        .\run_tests.ps1 -Integration # Run integration tests
        .\run_tests.ps1 -All        # Run all tests
        .\run_tests.ps1 -Coverage   # Run with coverage report

.PARAMETER Unit
    Run unit tests only
.PARAMETER E2E
    Run E2E tests only
.PARAMETER Perf
    Run performance benchmarks
.PARAMETER Security
    Run security tests
.PARAMETER Integration
    Run integration tests
.PARAMETER All
    Run all tests (default, excluding performance)
.PARAMETER Coverage
    Include coverage report
.PARAMETER Help
    Show this help message

.EXAMPLE
    .\run_tests.ps1 -All
.EXAMPLE
    .\run_tests.ps1 -Unit -Coverage
.EXAMPLE
    .\run_tests.ps1 -Perf

Exit codes:
    0 - All tests passed
    1 - Tests failed
    2 - Invalid arguments
#>

param(
    [switch]$Unit,
    [switch]$E2E,
    [switch]$Perf,
    [switch]$Security,
    [switch]$Integration,
    [switch]$All,
    [switch]$Coverage,
    [switch]$Help
)

# UTF-8 No BOM encoding for output
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# ──────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

# Colors
$RED = "`e[0;31m"
$GREEN = "`e[0;32m"
$YELLOW = "`e[1;33m"
$BLUE = "`e[0;34m"
$NC = "`e[0m"

# ──────────────────────────────────────────────────────────────────────
# Helper Functions
# ──────────────────────────────────────────────────────────────────────
function Write-Info { param($msg) Write-Host "${BLUE}[INFO]${NC} $msg" }
function Write-Success { param($msg) Write-Host "${GREEN}[PASS]${NC} $msg" }
function Write-Warning { param($msg) Write-Host "${YELLOW}[WARN]${NC} $msg" }
function Write-Error { param($msg) Write-Host "${RED}[FAIL]${NC} $msg" }

function Show-Help {
    Get-Help $MyInvocation.MyCommand.Path -Full | Out-String | Write-Host
    exit 0
}

function Activate-Venv {
    $VenvDir = Join-Path $ProjectRoot ".venv"
    $VenvScripts = Join-Path $VenvDir "Scripts"
    
    if (Test-Path $VenvScripts) {
        Write-Info "Activating virtual environment: $VenvDir"
        & "$VenvScripts\Activate.ps1" -ErrorAction SilentlyContinue
    } else {
        Write-Warning "Virtual environment not found at $VenvDir, using system Python"
    }
}

# ──────────────────────────────────────────────────────────────────────
# Main Script
# ──────────────────────────────────────────────────────────────────────
if ($Help) { Show-Help }

# Determine test suite
$TestSuite = "all"
if ($Unit) { $TestSuite = "unit" }
elseif ($E2E) { $TestSuite = "e2e" }
elseif ($Perf) { $TestSuite = "performance" }
elseif ($Security) { $TestSuite = "security" }
elseif ($Integration) { $TestSuite = "integration" }
elseif ($All) { $TestSuite = "all" }

# Activate venv if exists
Activate-Venv

# Check Python version
try {
    $PythonVersion = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    Write-Info "Python version: $PythonVersion"
} catch {
    Write-Error "Python not found in PATH"
    exit 2
}

# Set environment variables
$env:SKIP_LLM = if ($env:SKIP_LLM) { $env:SKIP_LLM } else { "1" }
$env:PYTHONPATH = "$ProjectRoot;$env:PYTHONPATH"

# Build pytest command
$PytestCmd = "python -m pytest"
$PytestArgs = @()

# Add coverage if requested
if ($Coverage) {
    $PytestArgs += "--cov=src/super_thinking"
    $PytestArgs += "--cov-report=term-missing"
    $PytestArgs += "--cov-report=html"
}

# Add test suite specific options
switch ($TestSuite) {
    "unit" {
        Write-Info "Running UNIT tests..."
        $PytestArgs += @("-v", "--tb=short", "-m", "unit", "tests/v6/unit/")
    }
    "e2e" {
        Write-Info "Running E2E tests..."
        $PytestArgs += @("-v", "--tb=short", "-m", "e2e", "tests/v6/e2e/")
    }
    "performance" {
        Write-Info "Running PERFORMANCE tests..."
        $PytestArgs += @("-v", "--tb=short", "-m", "performance", "--benchmark-only", "tests/v6/performance/")
    }
    "security" {
        Write-Info "Running SECURITY tests..."
        $PytestArgs += @("-v", "--tb=short", "-m", "security", "tests/v6/security/")
    }
    "integration" {
        Write-Info "Running INTEGRATION tests..."
        $PytestArgs += @("-v", "--tb=short", "-m", "integration", "tests/v6/integration/")
    }
    "all" {
        Write-Info "Running ALL tests (excluding performance by default)..."
        $PytestArgs += @("-v", "--tb=short", "-m", "not performance", "tests/v6/")
    }
}

# Change to project directory
Push-Location $ProjectRoot

# Execute pytest
Write-Info "Command: $PytestCmd $($PytestArgs -join ' ')"
Write-Host ""

try {
    & $PytestCmd @PytestArgs
    $exitCode = $LASTEXITCODE
    
    Write-Host ""
    if ($exitCode -eq 0) {
        Write-Success "All $TestSuite tests passed!"
    } else {
        Write-Error "Some $TestSuite tests failed!"
    }
    
    Pop-Location
    exit $exitCode
} catch {
    Write-Error "Failed to run pytest: $_"
    Pop-Location
    exit 1
}
