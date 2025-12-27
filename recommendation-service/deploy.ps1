# Recommendation Service Deployment Script
# PowerShell version for Windows

Write-Host "===================================" -ForegroundColor Green
Write-Host "Deploying Recommendation Service" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green

# Stop existing containers
Write-Host "`nStopping existing containers..." -ForegroundColor Yellow
docker-compose stop recommendation

# Remove old container
Write-Host "Removing old container..." -ForegroundColor Yellow
docker-compose rm -f recommendation

# Build new image
Write-Host "Building recommendation service..." -ForegroundColor Yellow
docker-compose build recommendation

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nBuild failed!" -ForegroundColor Red
    exit 1
}

# Start service
Write-Host "Starting recommendation service..." -ForegroundColor Yellow
docker-compose up -d recommendation

# Wait for service to be ready
Write-Host "Waiting for service to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check if service is running
Write-Host "`n===================================" -ForegroundColor Green
Write-Host "Checking service status..." -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green
docker-compose ps recommendation

# Check logs
Write-Host "`n===================================" -ForegroundColor Green
Write-Host "Service Logs (last 20 lines):" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green
docker-compose logs --tail=20 recommendation

# Test health endpoint
Write-Host "`n===================================" -ForegroundColor Green
Write-Host "Testing health endpoint..." -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8001/health" -Method Get
    $response | ConvertTo-Json
    Write-Host "`nHealth check: OK" -ForegroundColor Green
} catch {
    Write-Host "`nHealth check failed: $_" -ForegroundColor Red
}

Write-Host "`n===================================" -ForegroundColor Green
Write-Host "Deployment complete!" -ForegroundColor Green
Write-Host "Service is running at: http://localhost:8001" -ForegroundColor Cyan
Write-Host "API docs at: http://localhost:8001/docs" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Green
