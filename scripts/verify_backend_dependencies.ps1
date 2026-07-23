$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

Write-Host "Validating installed Python dependencies..." -ForegroundColor Cyan
docker compose exec -T backend python -m pip check
if ($LASTEXITCODE -ne 0) {
    throw "Dependency validation failed."
}

Write-Host "Checking critical packages..." -ForegroundColor Cyan
docker compose exec -T backend python -c "import bcrypt, openpyxl, fastapi, pandas, sqlalchemy; print('bcrypt:', bcrypt.__version__); print('openpyxl:', openpyxl.__version__); print('fastapi:', fastapi.__version__); print('pandas:', pandas.__version__); print('sqlalchemy:', sqlalchemy.__version__)"
if ($LASTEXITCODE -ne 0) {
    throw "A critical backend package could not be imported."
}

Write-Host "Backend dependency verification passed." -ForegroundColor Green
