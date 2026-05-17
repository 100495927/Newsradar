<#
Rebuilds the Docker stack from scratch, waits for health, then runs the test suite.
#>

param(
    [int]$TimeoutSeconds = 600,
    [int]$PollSeconds = 5
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDir "..")
$resetScript = Join-Path $scriptDir "reset_datastores_and_rebootstrap.ps1"

Set-Location $repoRoot

Write-Host "[rebuild-test] docker compose down..."
docker compose down

Write-Host "[rebuild-test] Resetting datastores..."
& $resetScript

Write-Host "[rebuild-test] Building and starting compose..."
docker compose up -d --build

$services = @("mongodb", "rss-worker", "alert-worker", "backend", "frontend")

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

$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
$allHealthy = $false

while ((Get-Date) -lt $deadline) {
    $allHealthy = $true

    foreach ($svc in $services) {
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
    throw "Timeout waiting for compose services to become healthy."
}

Write-Host "[rebuild-test] All services healthy. Running test suite..."
python .\devops_verifica-main\run_tests.py
exit $LASTEXITCODE
