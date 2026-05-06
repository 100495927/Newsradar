param(
    [ValidateSet("all", "unit", "integration", "api", "email")]
    [string]$Type = "all",
    [switch]$SkipMongoCheck
)

$ErrorActionPreference = "Stop"

function Write-Info($message) {
    Write-Host "[tests] $message" -ForegroundColor Cyan
}

function Write-Ok($message) {
    Write-Host "[tests] $message" -ForegroundColor Green
}

function Write-WarnMsg($message) {
    Write-Host "[tests] $message" -ForegroundColor Yellow
}

function Fail($message) {
    Write-Host "[tests] $message" -ForegroundColor Red
    exit 1
}

function Import-DotEnv([string]$envPath) {
    if (-not (Test-Path -LiteralPath $envPath)) {
        return
    }

    Get-Content -LiteralPath $envPath | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith("#")) {
            return
        }

        $parts = $line -split "=", 2
        if ($parts.Count -ne 2) {
            return
        }

        $name = $parts[0].Trim()
        $value = $parts[1].Trim()
        [Environment]::SetEnvironmentVariable($name, $value, "Process")
    }
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

Import-DotEnv (Join-Path $repoRoot ".env")

$pythonExe = Get-PythonPath $repoRoot
$env:PYTHONPATH = "$repoRoot\backend;$repoRoot"

if (-not $env:MONGO_HOST -or $env:MONGO_HOST -eq "mongodb") {
    $env:MONGO_HOST = "localhost"
}
if (-not $env:MONGO_PORT) {
    $env:MONGO_PORT = "27017"
}
if (-not $env:MONGO_APP_USER) {
    $env:MONGO_APP_USER = "newsradar_app"
}
if (-not $env:MONGO_APP_PASSWORD) {
    $env:MONGO_APP_PASSWORD = "change_me_app_pwd"
}
if (-not $env:MONGO_APP_DB) {
    $env:MONGO_APP_DB = "newsradar"
}

$env:MONGODB_URI = "mongodb://$($env:MONGO_APP_USER):$($env:MONGO_APP_PASSWORD)@$($env:MONGO_HOST):$($env:MONGO_PORT)/$($env:MONGO_APP_DB)?authSource=$($env:MONGO_APP_DB)"

Write-Info "Repo: $repoRoot"
Write-Info "Python: $pythonExe"
Write-Info "Tipo de tests: $Type"
Write-Info "Mongo esperado en $($env:MONGO_HOST):$($env:MONGO_PORT)"

$dependencyCheck = @'
import importlib.util
import sys

required = ["pytest", "croniter", "pymongo", "fastapi", "httpx"]
missing = [name for name in required if importlib.util.find_spec(name) is None]
if missing:
    print("Faltan dependencias en el entorno Python: " + ", ".join(missing))
    sys.exit(1)
'@

$dependencyCheck | & $pythonExe -
if ($LASTEXITCODE -ne 0) {
    Fail "Instala dependencias con '.\.venv\Scripts\python.exe -m pip install -r requirements.txt'."
}

$mongoTypes = @("all", "integration", "api")
if ((-not $SkipMongoCheck) -and ($mongoTypes -contains $Type)) {
    $mongoCheck = @'
import os
import sys
from pymongo import MongoClient

uri = os.environ["MONGODB_URI"]
try:
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
except Exception as exc:
    print(f"No se pudo conectar a MongoDB con {uri}: {exc}")
    sys.exit(1)
'@

    Write-Info "Comprobando conectividad con MongoDB..."
    $mongoCheck | & $pythonExe -
    if ($LASTEXITCODE -ne 0) {
        Fail "MongoDB no es accesible. Si usas Docker Compose desde host local, revisa que MONGO_HOST sea 'localhost' y que el puerto esté publicado."
    }
    Write-Ok "MongoDB accesible."
}

$targetsByType = @{
    all = @("backend/tests")
    unit = @(
        "backend/tests/test_auth.py",
        "backend/tests/test_alertas.py::test_modelo_alerta_invalido"
    )
    integration = @(
        "backend/tests/test_stats.py",
        "backend/tests/test_rss.py",
        "backend/tests/test_api_features.py",
        "backend/tests/test_seed_data.py",
        "backend/tests/test_notification_extensions.py",
        "backend/tests/test_roles_disabled.py",
        "backend/tests/test_alertas.py::test_health_endpoint",
        "backend/tests/test_alertas.py::test_crear_alerta_requiere_autenticacion"
    )
    api = @("backend/tests/api")
    email = @("backend/tests/test_email_send.py")
}

$pytestArgs = @("-m", "pytest", "-q") + $targetsByType[$Type]

Write-Info ("Ejecutando: {0} {1}" -f $pythonExe, ($pytestArgs -join " "))
& $pythonExe @pytestArgs
$exitCode = $LASTEXITCODE

if ($exitCode -eq 0) {
    Write-Ok "Tests completados correctamente."
    exit 0
}

Fail "Pytest terminó con código $exitCode."
