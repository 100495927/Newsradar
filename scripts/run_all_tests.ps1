param(
    [switch]$SkipMongoCheck
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$runner = Join-Path $scriptDir "run_backend_tests.ps1"

& $runner -Type all -SkipMongoCheck:$SkipMongoCheck
exit $LASTEXITCODE
