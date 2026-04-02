<#
Herramienta de limpieza de persistencia local (MongoDB + Elasticsearch).
Resultado esperado: se eliminan unicamente los ficheros de datos persistentes.
No ejecuta build ni arranque de contenedores.
#>

$ErrorActionPreference = "Stop"

Write-Host "[reset] Limpiando datos persistentes de MongoDB y Elasticsearch..."
if (Test-Path "./data/mongodb/data") {
  Get-ChildItem "./data/mongodb/data" -Force | Where-Object { $_.Name -ne ".gitkeep" } | Remove-Item -Recurse -Force
}
if (Test-Path "./data/mongodb/configdb") {
  Get-ChildItem "./data/mongodb/configdb" -Force | Where-Object { $_.Name -ne ".gitkeep" } | Remove-Item -Recurse -Force
}
if (Test-Path "./data/elasticsearch/data") {
  Get-ChildItem "./data/elasticsearch/data" -Force | Where-Object { $_.Name -ne ".gitkeep" } | Remove-Item -Recurse -Force
}

Write-Host "[reset] Limpieza completada (solo borrado de datos)."