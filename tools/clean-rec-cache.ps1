# Reset all demo data for presentation
# This script clears:
# 1. Recommendation service data (user interactions, preferences, cache)
# 2. Chatbot conversation history

Write-Host "🔄 Resetting demo data..." -ForegroundColor Yellow

# 1. Reset recommendation service
Write-Host "`n1️⃣ Clearing recommendation service data..." -ForegroundColor Cyan
docker exec medusa_postgres psql -U postgres -d medusa-store -f /tmp/reset_demo_data.sql

# Copy reset script to container first
docker cp recommendation-service/database/reset_demo_data.sql medusa_postgres:/tmp/reset_demo_data.sql

# Execute reset
docker exec medusa_postgres psql -U postgres -d medusa-store -f /tmp/reset_demo_data.sql

Write-Host "✅ Recommendation data cleared" -ForegroundColor Green

# 2. Reset chatbot conversations (if you have a table for it)
Write-Host "`n2️⃣ Clearing chatbot conversation history..." -ForegroundColor Cyan
docker exec medusa_postgres psql -U postgres -d medusa-store -c "TRUNCATE TABLE chatbot.conversation_history CASCADE;" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Chatbot history cleared" -ForegroundColor Green
} else {
    Write-Host "⚠️  No chatbot history table found (skipped)" -ForegroundColor Yellow
}

# 3. Clear browser session/cookies reminder
Write-Host "`n3️⃣ Manual steps:" -ForegroundColor Cyan
Write-Host "   - Clear browser cookies/session for localhost:3000" -ForegroundColor White
Write-Host "   - Restart recommendation service: cd recommendation-service && docker compose restart" -ForegroundColor White
Write-Host "   - Refresh frontend pages" -ForegroundColor White

Write-Host "`n✨ Demo reset complete!" -ForegroundColor Green
Write-Host "You can now start fresh demo with clean data" -ForegroundColor White
