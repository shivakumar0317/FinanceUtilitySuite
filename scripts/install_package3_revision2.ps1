$ErrorActionPreference = "Stop"

$ProjectRoot = "D:\FinanceUtilitySuite"
$PackageRoot = Split-Path -Parent $PSScriptRoot
$BackupSuffix = ".v1.8.2.package3.revision2.backup"
$MainFile = Join-Path $ProjectRoot "backend\main.py"
$SettingsFile = Join-Path $ProjectRoot "backend\performance_settings.py"

Write-Host "Installing Finance Utility Suite v1.8.2 Package 3 Revision 2..." -ForegroundColor Cyan

$files = @(
    "backend\cache\__init__.py",
    "backend\cache\manager.py",
    "backend\cache\decorators.py",
    "backend\performance_runtime.py",
    "backend\middleware\slow_request.py",
    "backend\api\performance_routes.py",
    "scripts\install_package3_revision2.ps1",
    "scripts\test_package3.ps1"
)

foreach ($relativePath in $files) {
    $source = Join-Path $PackageRoot $relativePath
    $destination = Join-Path $ProjectRoot $relativePath
    if (-not (Test-Path $source)) { throw "Package file missing: $source" }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $destination) | Out-Null
    Copy-Item $source $destination -Force
    Write-Host "Installed: $relativePath" -ForegroundColor Green
}

foreach ($target in @($MainFile, $SettingsFile)) {
    if (-not (Test-Path $target)) { throw "Required project file not found: $target" }
    if (-not (Test-Path "$target$BackupSuffix")) { Copy-Item $target "$target$BackupSuffix" }
}

$settings = Get-Content $SettingsFile -Raw

if ($settings -notmatch '(?m)^\s*slow_request_logging_enabled:\s*bool\s*$') {
    $pattern = '(?m)^(\s*)gzip_compresslevel:\s*int\s*$'
    if (-not [regex]::IsMatch($settings, $pattern)) { throw "Could not locate gzip_compresslevel field." }
    $settings = [regex]::Replace($settings, $pattern, '$0' + "`r`n" + '$1slow_request_logging_enabled: bool' + "`r`n" + '$1slow_request_threshold_ms: int', 1)
}

if ($settings -notmatch 'slow_request_logging_enabled\s*=\s*_bool\(') {
    $pattern = '(?m)^(\s*)gzip_compresslevel\s*=\s*min\(_int\("GZIP_COMPRESSLEVEL",\s*5,\s*1\),\s*9\),\s*$'
    if (-not [regex]::IsMatch($settings, $pattern)) { throw "Could not locate gzip_compresslevel assignment." }
    $settings = [regex]::Replace($settings, $pattern, '$0' + "`r`n" + '$1slow_request_logging_enabled=_bool("SLOW_REQUEST_LOGGING_ENABLED", True),' + "`r`n" + '$1slow_request_threshold_ms=_int("SLOW_REQUEST_THRESHOLD_MS", 500, 1),', 1)
}

Set-Content -Path $SettingsFile -Value $settings -Encoding UTF8
Write-Host "Patched: backend\performance_settings.py" -ForegroundColor Green

$main = Get-Content $MainFile -Raw
$runtimeImport = "from backend.performance_runtime import configure_performance_runtime"
$routeImport = "from backend.api.performance_routes import router as performance_router"

if ($main -notmatch [regex]::Escape($runtimeImport)) {
    $anchor = "from backend.security import register_security_middleware"
    if ($main -notmatch [regex]::Escape($anchor)) { throw "Security import anchor not found in backend\main.py" }
    $main = $main.Replace($anchor, "$anchor`r`n$runtimeImport")
}

if ($main -notmatch [regex]::Escape($routeImport)) {
    $main = $main.Replace($runtimeImport, "$runtimeImport`r`n$routeImport")
}

if ($main -notmatch [regex]::Escape("configure_performance_runtime(app)")) {
    $anchor = "register_security_middleware(app)"
    if ($main -notmatch [regex]::Escape($anchor)) { throw "Security middleware anchor not found in backend\main.py" }
    $main = $main.Replace($anchor, "$anchor`r`nconfigure_performance_runtime(app)")
}

if ($main -notmatch [regex]::Escape("app.include_router(performance_router)")) {
    $matches = [regex]::Matches($main, 'app\.include_router\([^)]+\)')
    if ($matches.Count -eq 0) { throw "No router registration found in backend\main.py" }
    $last = $matches[$matches.Count - 1]
    $main = $main.Insert($last.Index + $last.Length, "`r`napp.include_router(performance_router)")
}

Set-Content -Path $MainFile -Value $main -Encoding UTF8
Write-Host "Patched: backend\main.py" -ForegroundColor Green
Write-Host "Package 3 Revision 2 installation complete." -ForegroundColor Green
