$ErrorActionPreference = "Stop"

$ProjectRoot = "D:\FinanceUtilitySuite"
$PackageRoot = Split-Path -Parent $PSScriptRoot
$BackupSuffix = ".v1.8.1.package3.backup"

Write-Host "Installing Finance Utility Suite v1.8.1 Package 3..." -ForegroundColor Cyan

$files = @(
    "backend\main.py",
    "backend\exceptions.py",
    "backend\logging_config.py",
    "backend\middleware\__init__.py",
    "backend\middleware\request_context.py",
    "backend\middleware\request_id.py",
    "backend\middleware\request_logger.py",
    "backend\schemas\error_schema.py"
)

foreach ($relativePath in $files) {
    $source = Join-Path $PackageRoot $relativePath
    $destination = Join-Path $ProjectRoot $relativePath

    if (-not (Test-Path $source)) { throw "Missing package file: $source" }

    if ([IO.Path]::GetFullPath($source) -eq [IO.Path]::GetFullPath($destination)) {
        Write-Host "Skipped self-copy: $relativePath" -ForegroundColor Yellow
        continue
    }

    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $destination) | Out-Null

    if ((Test-Path $destination) -and -not (Test-Path "$destination$BackupSuffix")) {
        Copy-Item $destination "$destination$BackupSuffix"
        Write-Host "Backup created: $destination$BackupSuffix"
    }

    Copy-Item $source $destination -Force
    Write-Host "Installed: $relativePath" -ForegroundColor Green
}

Write-Host "Package 3 installation complete." -ForegroundColor Green
