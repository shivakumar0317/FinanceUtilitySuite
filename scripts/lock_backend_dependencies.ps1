$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

Write-Host "Checking the backend container..." -ForegroundColor Cyan
$running = docker compose ps --status running --services
if ($LASTEXITCODE -ne 0 -or $running -notcontains "backend") {
    throw "The backend service is not running. Start it with: docker compose up -d"
}

Write-Host "Exporting exact package versions from the tested backend container..." -ForegroundColor Cyan
$header = @(
    "# Finance Utility Suite v1.8.1 backend dependency lock"
    "# Generated from the tested Docker backend container."
    "# Do not edit manually; regenerate with scripts/lock_backend_dependencies.ps1."
    ""
)

$freeze = docker compose exec -T backend python -m pip freeze
if ($LASTEXITCODE -ne 0) {
    throw "Unable to export dependencies from the backend container."
}

$lockPath = Join-Path $projectRoot "requirements-web.lock.txt"
($header + $freeze) | Set-Content -Path $lockPath -Encoding utf8

Write-Host "Created: requirements-web.lock.txt" -ForegroundColor Green
Write-Host "Next: run scripts/verify_backend_dependencies.ps1" -ForegroundColor Yellow
