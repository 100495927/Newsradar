param(
    [ValidateSet("all", "alerts", "rss", "worker")]
    [string]$Type = "all"
)

$ErrorActionPreference = "Stop"

function Write-Info($message) {
    Write-Host "[worker-tests] $message" -ForegroundColor Cyan
}

function Write-Ok($message) {
    Write-Host "[worker-tests] $message" -ForegroundColor Green
}

function Fail($message) {
    Write-Host "[worker-tests] $message" -ForegroundColor Red
    exit 1
}

function Get-PythonPath([string]$repoRoot) {
    $venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
    if (Test-Path -LiteralPath $venvPython) {
        return $venvPython
    }

    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCmd) {
        return $pythonCmd.Source
    }

    Fail "No encuentro Python. Crea el virtualenv en '.venv' o instala Python en PATH."
}

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repoRoot

$pythonExe = Get-PythonPath $repoRoot
$env:PYTHONPATH = "$repoRoot\rss-worker;$repoRoot"

Write-Info "Repo: $repoRoot"
Write-Info "Python: $pythonExe"
Write-Info "Tipo de tests: $Type"

$dependencyCheck = @'
import importlib.util
import sys

required = ["pytest", "pymongo", "feedparser", "dateparser", "croniter"]
missing = [name for name in required if importlib.util.find_spec(name) is None]
if missing:
    print("Faltan dependencias en el entorno Python: " + ", ".join(missing))
    sys.exit(1)
'@

$dependencyCheck | & $pythonExe -
if ($LASTEXITCODE -ne 0) {
    Fail "Instala dependencias con '.\.venv\Scripts\python.exe -m pip install -r requirements.txt'."
}

$targetsByType = @{
    all = @("rss-worker/tests")
    alerts = @("rss-worker/tests/alerts")
    rss = @("rss-worker/tests/rss")
    worker = @("rss-worker/tests/worker")
}

$pytestArgs = @("-m", "pytest", "-q") + $targetsByType[$Type]

Write-Info ("Ejecutando: {0} {1}" -f $pythonExe, ($pytestArgs -join " "))
& $pythonExe @pytestArgs
$exitCode = $LASTEXITCODE

if ($exitCode -eq 0) {
    Write-Ok "Tests del worker completados correctamente."
    exit 0
}

Fail "Pytest terminó con código $exitCode."
