$ErrorActionPreference = "Stop"
$ProjectRoot = "D:\FinanceUtilitySuite"
$PackageRoot = Split-Path -Parent $PSScriptRoot
$BackupSuffix = ".v1.8.2.package2.backup"
$MainFile = Join-Path $ProjectRoot "backend\main.py"

$files = @(
 "backend\security.py",
 "backend\security_settings.py",
 "backend\middleware\security_headers.py",
 "backend\middleware\request_size.py",
 "scripts\install_package2.ps1",
 "scripts\test_package2.ps1"
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

if (-not (Test-Path "$MainFile$BackupSuffix")) {
    Copy-Item $MainFile "$MainFile$BackupSuffix"
}

$main = Get-Content $MainFile -Raw
$importLine = "from backend.security import register_security_middleware"
if ($main -notmatch [regex]::Escape($importLine)) {
    $anchor = "from backend.performance_settings import get_performance_settings"
    if ($main -notmatch [regex]::Escape($anchor)) { throw "Expected import anchor not found in backend\main.py" }
    $main = $main.Replace($anchor, "$anchor`r`n$importLine")
}

$registerLine = "register_security_middleware(app)"
if ($main -notmatch [regex]::Escape($registerLine)) {
    $anchor = "register_exception_handlers(app)"
    if ($main -notmatch [regex]::Escape($anchor)) { throw "Expected middleware anchor not found in backend\main.py" }
    $main = $main.Replace($anchor, "$registerLine`r`n$anchor")
}

Set-Content -Path $MainFile -Value $main -Encoding UTF8
Write-Host "Package 2 installation complete." -ForegroundColor Green
