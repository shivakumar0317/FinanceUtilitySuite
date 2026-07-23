$ErrorActionPreference = "Stop"
$response = Invoke-WebRequest "http://localhost:8000/health" -UseBasicParsing
$headers = @(
 "X-Content-Type-Options",
 "X-Frame-Options",
 "Referrer-Policy",
 "Permissions-Policy",
 "X-Permitted-Cross-Domain-Policies",
 "Content-Security-Policy"
)
Write-Host "HTTP Status : $($response.StatusCode)"
foreach ($header in $headers) {
    $value = $response.Headers[$header]
    Write-Host "$header : $value"
    if (-not $value) { throw "Missing security header: $header" }
}
Write-Host "Package 2 verification passed." -ForegroundColor Green
