<#
Resetea el stack Docker lo mas limpio posible, reconstruye sin cache y ejecuta los tests.
#>

param(
    [int]$TimeoutSeconds = 600,
    [int]$PollSeconds = 5,
    [string[]]$TestArgs = @()
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDir "..")
$resetScript = Join-Path $scriptDir "reset_datastores_and_rebootstrap.ps1"
$composeServices = @("mongodb", "rss-worker", "alert-worker", "backend", "frontend")
$testRunner = Join-Path $repoRoot "devops_verifica-main\run_tests.py"
$timings = [ordered]@{}
$totalTimer = [System.Diagnostics.Stopwatch]::StartNew()

Set-Location $repoRoot

function Invoke-Step([string]$message, [scriptblock]$action) {
    Write-Host "[rebuild-test] $message"
    & $action
    if ($LASTEXITCODE -ne 0) {
        throw "Fallo en paso: $message"
    }
}

function Get-ComposeContainerId([string]$service) {
    $id = docker compose ps -q $service 2>$null
    if ($null -eq $id) {
        return $null
    }
    return ($id | Select-Object -First 1).Trim()
}

function Get-ContainerStatus([string]$containerId) {
    $state = (docker inspect -f "{{.State.Status}}" $containerId 2>$null).Trim()
    $health = (docker inspect -f "{{if .State.Health}}{{.State.Health.Status}}{{end}}" $containerId 2>$null).Trim()
    return @{ State = $state; Health = $health }
}

function Show-ComposeStatus() {
    Write-Host "[rebuild-test] Estado actual de contenedores:"
    docker compose ps
}

function Measure-Step([string]$name, [scriptblock]$action) {
    $timer = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        & $action
    }
    finally {
        $timer.Stop()
        $timings[$name] = $timer.Elapsed
    }
}

function Format-Duration([TimeSpan]$duration) {
    return "{0:00}:{1:00}:{2:00}.{3:000}" -f [int]$duration.TotalHours, $duration.Minutes, $duration.Seconds, $duration.Milliseconds
}

function Show-TimingSummary([int]$exitCode) {
    $totalTimer.Stop()
    Write-Host ""
    Write-Host "[rebuild-test] Resumen de tiempos:"
    foreach ($entry in $timings.GetEnumerator()) {
        Write-Host ("[rebuild-test]   {0,-18} {1}" -f $entry.Key, (Format-Duration $entry.Value))
    }
    Write-Host ("[rebuild-test]   {0,-18} {1}" -f "total", (Format-Duration $totalTimer.Elapsed))
    Write-Host "[rebuild-test] Exit code: $exitCode"
}

$scriptExitCode = 0
$testExitCode = 0

try {
    Measure-Step "borrar" {
        Invoke-Step "Bajando stack y eliminando volumenes anonimos..." {
            docker compose down -v
        }

        Invoke-Step "Borrando datos persistentes locales..." {
            & $resetScript
        }
    }

    Measure-Step "build" {
        Invoke-Step "Reconstruyendo imagenes sin cache..." {
            docker compose build --no-cache --pull
        }
    }

    Measure-Step "levantar" {
        Invoke-Step "Levantando stack con recreacion forzada..." {
            docker compose up -d --force-recreate
        }

        $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
        $allHealthy = $false

        while ((Get-Date) -lt $deadline) {
            $allHealthy = $true

            foreach ($svc in $composeServices) {
                $cid = Get-ComposeContainerId $svc
                if (-not $cid) {
                    $allHealthy = $false
                    break
                }

                $status = Get-ContainerStatus $cid
                if ($status.State -ne "running") {
                    $allHealthy = $false
                    break
                }

                if ($status.Health -and $status.Health -ne "healthy") {
                    if ($status.Health -eq "unhealthy") {
                        throw "Service $svc is unhealthy."
                    }
                    $allHealthy = $false
                    break
                }
            }

            if ($allHealthy) {
                break
            }

            Start-Sleep -Seconds $PollSeconds
        }

        if (-not $allHealthy) {
            Show-ComposeStatus
            throw "Timeout waiting for compose services to become healthy."
        }
    }

    Show-ComposeStatus

    if (-not (Test-Path -LiteralPath $testRunner)) {
        throw "No se encontro el runner de tests en $testRunner"
    }

    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCmd) {
        throw "No se encontro 'python' en PATH para ejecutar el verificador."
    }

    $testCommand = @($testRunner) + $TestArgs
    Write-Host "[rebuild-test] Servicios sanos. Ejecutando tests: python $($testCommand -join ' ')"
    Measure-Step "tests" {
        & $pythonCmd.Source @testCommand
        $script:testExitCode = $LASTEXITCODE
    }
    $scriptExitCode = $testExitCode
}
catch {
    $scriptExitCode = 1
    Write-Host "[rebuild-test] ERROR: $($_.Exception.Message)" -ForegroundColor Red
}
finally {
    Show-TimingSummary $scriptExitCode
}

exit $scriptExitCode
