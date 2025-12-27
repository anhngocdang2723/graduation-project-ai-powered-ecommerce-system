# Production build and run for testing
# This eliminates hot reload and React Strict Mode double execution

Write-Host "🔄 Building Next.js for production..." -ForegroundColor Yellow
npm run build

if ($LASTEXITCODE -eq 0) {
    Write-Host "🚀 Starting production server (single thread)..." -ForegroundColor Green
    npm run start
} else {
    Write-Host "❌ Build failed!" -ForegroundColor Red
}