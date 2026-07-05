# test_redis.ps1
Write-Host "🔍 Checking Redis status..." -ForegroundColor Yellow

# Check if Redis process is running
$redisProcess = Get-Process -Name "redis-server" -ErrorAction SilentlyContinue
if ($redisProcess) {
    Write-Host "✅ Redis is running (Process ID: $($redisProcess.Id))" -ForegroundColor Green
} else {
    Write-Host "❌ Redis is NOT running" -ForegroundColor Red
}

# Check if port 6379 is listening
$portCheck = netstat -ano | findstr ":6379"
if ($portCheck) {
    Write-Host "✅ Port 6379 is listening" -ForegroundColor Green
    Write-Host $portCheck
} else {
    Write-Host "❌ Port 6379 is not listening" -ForegroundColor Red
}

# Check Redis installation
$redisPaths = @(
    "C:\Redis\redis-server.exe",
    "C:\Program Files\Redis\redis-server.exe"
)

foreach ($path in $redisPaths) {
    if (Test-Path $path) {
        Write-Host "✅ Found Redis at: $path" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "To start Redis manually:" -ForegroundColor Cyan
Write-Host "  cd C:\Redis" -ForegroundColor Gray
Write-Host "  .\redis-server.exe" -ForegroundColor Gray