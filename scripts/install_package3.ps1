$ErrorActionPreference = "Stop"

$ProjectRoot = "D:\FinanceUtilitySuite"
$PackageRoot = Split-Path -Parent $PSScriptRoot
$BackupSuffix = ".v1.8.2.package3.backup"
$MainFile = Join-Path $ProjectRoot "backend\main.py"
$SettingsFile = Join-Path $ProjectRoot "backend\performance_settings.py"

Write-Host "Installing Finance Utility Suite v1.8.2 Package 3..." -ForegroundColor Cyan

if (-not (Test-Path $ProjectRoot)) {
    throw "Project folder not found: $ProjectRoot"
}

$files = @(
    "backend\cache\__init__.py",
    "backend\cache\manager.py",
    "backend\cache\decorators.py",
    "backend\performance_runtime.py",
    "backend\middleware\slow_request.py",
    "backend\api\performance_routes.py",
    "scripts\install_package3.ps1",
    "scripts\test_package3.ps1"
)

foreach ($relativePath in $files) {
    $source = Join-Path $PackageRoot $relativePath
    $destination = Join-Path $ProjectRoot $relativePath

    if (-not (Test-Path $source)) {
        throw "Package file missing: $source"
    }

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

foreach ($target in @($MainFile, $SettingsFile)) {
    if (-not (Test-Path $target)) {
        throw "Required project file not found: $target"
    }

    if (-not (Test-Path "$target$BackupSuffix")) {
        Copy-Item $target "$target$BackupSuffix"
        Write-Host "Backup created: $target$BackupSuffix" -ForegroundColor DarkGray
    }
}

# Patch performance_settings.py
$settings = Get-Content $SettingsFile -Raw

$fieldAnchor = "gzip_minimum_size: int"
$newFields = @"
gzip_minimum_size: int
    cache_enabled: bool
    cache_default_ttl: int
    slow_request_logging_enabled: bool
    slow_request_threshold_ms: int
"@

if ($settings -notmatch "cache_enabled: bool") {
    if ($settings -notmatch [regex]::Escape($fieldAnchor)) {
        throw "Expected settings field anchor not found: $fieldAnchor"
    }

    $settings = $settings.Replace($fieldAnchor, $newFields.TrimEnd())
}

$assignmentAnchor = 'gzip_minimum_size=_as_int("GZIP_MINIMUM_SIZE", 1024),'
$newAssignments = @'
gzip_minimum_size=_as_int("GZIP_MINIMUM_SIZE", 1024),
        cache_enabled=_as_bool("CACHE_ENABLED", True),
        cache_default_ttl=_as_int("CACHE_DEFAULT_TTL", 300),
        slow_request_logging_enabled=_as_bool(
            "SLOW_REQUEST_LOGGING_ENABLED",
            True,
        ),
        slow_request_threshold_ms=_as_int(
            "SLOW_REQUEST_THRESHOLD_MS",
            500,
        ),
'@

if ($settings -notmatch "cache_enabled=_as_bool") {
    if ($settings -notmatch [regex]::Escape($assignmentAnchor)) {
        throw "Expected settings assignment anchor not found: $assignmentAnchor"
    }

    $settings = $settings.Replace($assignmentAnchor, $newAssignments.TrimEnd())
}

Set-Content -Path $SettingsFile -Value $settings -Encoding UTF8
Write-Host "Patched: backend\performance_settings.py" -ForegroundColor Green

# Patch main.py imports
$main = Get-Content $MainFile -Raw

$runtimeImport = "from backend.performance_runtime import configure_performance_runtime"
if ($main -notmatch [regex]::Escape($runtimeImport)) {
    $anchor = "from backend.security import register_security_middleware"

    if ($main -notmatch [regex]::Escape($anchor)) {
        throw "Expected main.py import anchor not found: $anchor"
    }

    $main = $main.Replace($anchor, "$anchor`r`n$runtimeImport")
}

$routeImport = "from backend.api.performance_routes import router as performance_router"
if ($main -notmatch [regex]::Escape($routeImport)) {
    $anchor = "from backend.performance_runtime import configure_performance_runtime"
    $main = $main.Replace($anchor, "$anchor`r`n$routeImport")
}

# Patch middleware registration
$runtimeCall = "configure_performance_runtime(app)"
if ($main -notmatch [regex]::Escape($runtimeCall)) {
    $anchor = "register_security_middleware(app)"

    if ($main -notmatch [regex]::Escape($anchor)) {
        throw "Expected main.py middleware anchor not found: $anchor"
    }

    $main = $main.Replace($anchor, "$anchor`r`n$runtimeCall")
}

# Patch router registration
$routerCall = "app.include_router(performance_router)"
if ($main -notmatch [regex]::Escape($routerCall)) {
    $matches = [regex]::Matches($main, 'app\.include_router\([^)]+\)')

    if ($matches.Count -eq 0) {
        throw "No app.include_router(...) anchor found in backend\main.py"
    }

    $last = $matches[$matches.Count - 1]
    $insertAt = $last.Index + $last.Length
    $main = $main.Insert($insertAt, "`r`n$routerCall")
}

Set-Content -Path $MainFile -Value $main -Encoding UTF8
Write-Host "Patched: backend\main.py" -ForegroundColor Green

Write-Host ""
Write-Host "Package 3 installation complete." -ForegroundColor Green
Write-Host "Next:"
Write-Host "  cd D:\FinanceUtilitySuite"
Write-Host "  docker compose build --no-cache backend"
Write-Host "  docker compose up -d"
Write-Host "  docker compose ps"
Write-Host "  powershell -ExecutionPolicy Bypass -File .\scripts\test_package3.ps1"
