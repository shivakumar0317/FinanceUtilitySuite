$ErrorActionPreference = "Stop"

$ProjectRoot = "D:\FinanceUtilitySuite"
$PackageRoot = Split-Path -Parent $PSScriptRoot

Write-Host "Installing Finance Utility Suite v1.8.1 Package 2..." -ForegroundColor Cyan

if (-not (Test-Path $ProjectRoot)) {
    throw "Project folder not found: $ProjectRoot"
}

$backupSuffix = ".v1.8.0.backup"

$files = @(
    @{ Source = "$PackageRoot\backend\main.py"; Destination = "$ProjectRoot\backend\main.py" },
    @{ Source = "$PackageRoot\backend\config.py"; Destination = "$ProjectRoot\backend\config.py" },
    @{ Source = "$PackageRoot\backend\api\system_routes.py"; Destination = "$ProjectRoot\backend\api\system_routes.py" },
    @{ Source = "$PackageRoot\docker-compose.yml"; Destination = "$ProjectRoot\docker-compose.yml" }
)

foreach ($file in $files) {
    $destination = $file.Destination
    $source = $file.Source

    if ((Test-Path $destination) -and -not (Test-Path "$destination$backupSuffix")) {
        Copy-Item $destination "$destination$backupSuffix"
        Write-Host "Backup created: $destination$backupSuffix"
    }

    $destinationDirectory = Split-Path -Parent $destination
    New-Item -ItemType Directory -Force -Path $destinationDirectory | Out-Null
    Copy-Item $source $destination -Force
    Write-Host "Installed: $destination"
}

Write-Host ""
Write-Host "Package installation complete." -ForegroundColor Green
Write-Host "Next commands:"
Write-Host "  cd D:\FinanceUtilitySuite"
Write-Host "  docker compose build --no-cache backend"
Write-Host "  docker compose up -d"
Write-Host "  docker compose ps"
