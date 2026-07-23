$ErrorActionPreference = "Stop"
$response = Invoke-WebRequest "http://localhost:8000/health" -UseBasicParsing
Write-Host "HTTP Status      : $($response.StatusCode)"
Write-Host "X-Request-ID     : $($response.Headers['X-Request-ID'])"
Write-Host "X-Response-Time  : $($response.Headers['X-Response-Time'])"
Write-Host "Content-Encoding : $($response.Headers['Content-Encoding'])"
if (-not $response.Headers["X-Response-Time"]) { throw "X-Response-Time header is missing." }
Write-Host "Package 1 verification passed." -ForegroundColor Green
