<#
Arranca el entorno Docker desde un estado limpio.
Secuencia:
1. Baja el stack y elimina volumenes anonimos.
2. Resetea los datastores persistentes locales.
3. Reconstruye todas las imagenes sin cache.
4. Levanta el stack recreando contenedores.
#>

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDir "..")
$resetScript = Join-Path $scriptDir "reset_datastores_and_rebootstrap.ps1"

Set-Location $repoRoot

function Invoke-Step([string]$message, [scriptblock]$action) {
    Write-Host "[arranque-limpio] $message"
    & $action
    if ($LASTEXITCODE -ne 0) {
        throw "Fallo en paso: $message"
    }
}

Invoke-Step "Bajando stack y limpiando volumenes anonimos..." {
    docker compose down -v --remove-orphans
}

Invoke-Step "Reseteando datastores persistentes..." {
    & $resetScript
}

Invoke-Step "Reconstruyendo imagenes sin cache..." {
    docker compose build --no-cache --pull
}

Invoke-Step "Levantando stack limpio..." {
    docker compose up -d --force-recreate --remove-orphans
}

Write-Host "[arranque-limpio] Estado final:"
docker compose ps
