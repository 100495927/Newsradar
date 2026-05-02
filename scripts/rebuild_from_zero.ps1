<#
Reconstruye el entorno Docker local desde cero.
Secuencia:
1. Baja los contenedores del proyecto.
2. Limpia los datastores persistentes usando el script de reset existente.
3. Vuelve a construir y levantar todo con docker compose.
#>

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDir "..")
$resetScript = Join-Path $scriptDir "reset_datastores_and_rebootstrap.ps1"

Set-Location $repoRoot

Write-Host "[rebuild] Bajando contenedores del proyecto..."
docker compose down

Write-Host "[rebuild] Limpiando datastores persistentes..."
& $resetScript

Write-Host "[rebuild] Reconstruyendo y levantando el stack desde cero..."
docker compose up -d --build

Write-Host "[rebuild] Entorno reconstruido. Puedes comprobar el estado con: docker compose ps"
