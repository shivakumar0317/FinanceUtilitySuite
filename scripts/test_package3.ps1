$ErrorActionPreference = "Stop"

$BaseUrl = "http://localhost:8000"

Write-Host "Testing v1.8.2 Package 3..." -ForegroundColor Cyan

$health = Invoke-WebRequest "$BaseUrl/health" -UseBasicParsing

if ($health.StatusCode -ne 200) {
    throw "Health endpoint failed."
}

Write-Host "Health status             : $($health.StatusCode)"
Write-Host "X-Response-Time           : $($health.Headers['X-Response-Time'])"

$statsResponse = Invoke-RestMethod "$BaseUrl/performance/cache/stats" -Method Get

if (-not $statsResponse.success) {
    throw "Cache statistics endpoint returned success=false."
}

Write-Host "Cache enabled             : $($statsResponse.cache.enabled)"
Write-Host "Cache active entries      : $($statsResponse.cache.active_entries)"
Write-Host "Cache hits                : $($statsResponse.cache.hits)"
Write-Host "Cache misses              : $($statsResponse.cache.misses)"
Write-Host "Cache hit ratio           : $($statsResponse.cache.hit_ratio)"
Write-Host "Cache default TTL         : $($statsResponse.cache.default_ttl_seconds) seconds"

$clearResponse = Invoke-RestMethod "$BaseUrl/performance/cache/clear" -Method Post

if (-not $clearResponse.success) {
    throw "Cache clear endpoint returned success=false."
}

Write-Host "Cache clear test          : passed"
Write-Host ""
Write-Host "Package 3 verification passed." -ForegroundColor Green
