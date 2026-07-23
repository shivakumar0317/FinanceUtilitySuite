$ErrorActionPreference = "Stop"
$ProjectRoot = "D:\FinanceUtilitySuite"
$PackageRoot = Split-Path -Parent $PSScriptRoot
$BackupSuffix = ".v1.8.2.package1.backup"

$files = @(
 "backend\main.py",
 "backend\performance_settings.py",
 "backend\middleware\response_time.py",
 "backend\utils\cache.py"
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
    }
    Copy-Item $source $destination -Force
    Write-Host "Installed: $relativePath" -ForegroundColor Green
}
Write-Host "Package 1 installation complete." -ForegroundColor Green
