param(
    [switch]$SkipMongoCheck
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendRunner = Join-Path $scriptDir "run_backend_tests.ps1"
$workerRunner = Join-Path $scriptDir "run_worker_tests.ps1"

& $backendRunner -Type all -SkipMongoCheck:$SkipMongoCheck
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

& $workerRunner -Type all
exit $LASTEXITCODE
