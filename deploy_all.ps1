# Complete Deployment Script for Windows
# Deploys entire stack with recommendation service

Write-Host "===================================" -ForegroundColor Cyan
Write-Host "   Graduation Project Deployment   " -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan

$services = @("postgres", "redis", "medusa", "chatbot", "recommendation")

# Step 1: Stop all services
Write-Host "`n[1/5] Stopping all services..." -ForegroundColor Yellow
docker-compose down

# Step 2: Build all services
Write-Host "`n[2/5] Building all services..." -ForegroundColor Yellow
docker-compose build

if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}

# Step 3: Start services in order
Write-Host "`n[3/5] Starting services..." -ForegroundColor Yellow

# Start database and cache first
Write-Host "Starting postgres and redis..." -ForegroundColor Gray
docker-compose up -d postgres redis
Start-Sleep -Seconds 10

# Start medusa backend
Write-Host "Starting medusa backend..." -ForegroundColor Gray
docker-compose up -d medusa
Start-Sleep -Seconds 20

# Start AI services
Write-Host "Starting chatbot and recommendation services..." -ForegroundColor Gray
docker-compose up -d chatbot recommendation
Start-Sleep -Seconds 10

# Step 4: Verify services
Write-Host "`n[4/5] Verifying services..." -ForegroundColor Yellow
docker-compose ps

# Step 5: Health checks
Write-Host "`n[5/5] Running health checks..." -ForegroundColor Yellow

# Check Medusa
try {
    $medusa = Invoke-RestMethod -Uri "http://localhost:9000/health" -Method Get -TimeoutSec 5
    Write-Host "✓ Medusa Backend: OK" -ForegroundColor Green
} catch {
    Write-Host "✗ Medusa Backend: Failed" -ForegroundColor Red
}

# Check Chatbot
try {
    $chatbot = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5
    Write-Host "✓ Chatbot Service: OK" -ForegroundColor Green
} catch {
    Write-Host "✗ Chatbot Service: Failed" -ForegroundColor Red
}

# Check Recommendation
try {
    $rec = Invoke-RestMethod -Uri "http://localhost:8001/health" -Method Get -TimeoutSec 5
    Write-Host "✓ Recommendation Service: OK" -ForegroundColor Green
} catch {
    Write-Host "✗ Recommendation Service: Failed" -ForegroundColor Red
}

# Verify database tables
Write-Host "`nVerifying database tables..." -ForegroundColor Yellow
docker exec -it medusa_postgres psql -U postgres -d medusa-store -c "\dt rec_*"

Write-Host "`n===================================" -ForegroundColor Cyan
Write-Host "       Deployment Summary          " -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host "PostgreSQL:       http://localhost:5432" -ForegroundColor White
Write-Host "Redis:            http://localhost:6379" -ForegroundColor White
Write-Host "Medusa Backend:   http://localhost:9000" -ForegroundColor White
Write-Host "Chatbot Service:  http://localhost:8000" -ForegroundColor White
Write-Host "Recommendation:   http://localhost:8001" -ForegroundColor White
Write-Host "Frontend:         http://localhost:3000" -ForegroundColor White
Write-Host "pgAdmin:          http://localhost:5050" -ForegroundColor White
Write-Host "`nAPI Docs:" -ForegroundColor Cyan
Write-Host "  Chatbot:        http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Recommendation: http://localhost:8001/docs" -ForegroundColor White
Write-Host "===================================" -ForegroundColor Cyan

Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Start frontend: cd vercel-commerce && npm run dev" -ForegroundColor White
Write-Host "2. Run tests: .\recommendation-service\test_service.ps1" -ForegroundColor White
Write-Host "3. View logs: docker-compose logs -f <service>" -ForegroundColor White
