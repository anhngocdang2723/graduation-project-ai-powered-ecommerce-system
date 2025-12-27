# 📋 Quick Reference Card - Recommendation System

## 🎯 TL;DR (Too Long; Didn't Read)

### Câu Hỏi 1: Service vận hành như thế nào?
**Trả lời**: 
- Service chạy trong Docker container `medusa_recommendation`
- Port 8001 (FastAPI)
- Tự động khởi tạo database khi start
- Nhận requests từ frontend → Process bằng ML → Trả về recommendations

### Câu Hỏi 2: Database lưu ở đâu?
**Trả lời**:
- Database: `medusa-store` (cùng database với Medusa và Chatbot)
- Schema: `recommendation` (CÓ schema riêng!)
- Tables: 7 tables với prefix `rec_*`
- Xem trong pgAdmin: Schemas → **recommendation** → Tables

### Câu Hỏi 3: Đã tích hợp vào docker-compose.yml chưa?
**Trả lời**: 
- ✅ **ĐÃ TÍCH HỢP HOÀN TOÀN**
- File: `docker-compose.yml` (ở thư mục gốc)
- Service name: `recommendation`
- Cùng network với tất cả services khác

---

## 📍 File Locations

| Mục đích | File Path |
|----------|-----------|
| **Docker config chính** | `graduation-project/docker-compose.yml` |
| **Recommendation code** | `graduation-project/recommendation-service/` |
| **Database schema** | `recommendation-service/database/init_schema.sql` |
| **Auto init script** | `recommendation-service/init_db.sh` |
| **FastAPI app** | `recommendation-service/app/main.py` |
| **ML engine** | `recommendation-service/app/services/recommendation_engine.py` |
| **Deploy script** | `graduation-project/deploy_all.ps1` |

---

## 🗄️ Database Quick Access

### SQL Query: View Tables
```sql
-- Xem tất cả rec tables trong recommendation schema
SELECT tablename FROM pg_tables 
WHERE schemaname = 'recommendation';
```

### PowerShell: Quick Check
```powershell
# Check tables exist in recommendation schema
docker exec medusa_postgres psql -U postgres -d medusa-store -c "SELECT tablename FROM pg_tables WHERE schemaname = 'recommendation';"

# Count interactions
docker exec medusa_postgres psql -U postgres -d medusa-store -c "SELECT COUNT(*) FROM recommendation.rec_user_interactions;"

# View recent data
docker exec medusa_postgres psql -U postgres -d medusa-store -c "SELECT * FROM recommendation.rec_user_interactions LIMIT 5;"
```

### pgAdmin: Navigation Path
```
http://localhost:5050
→ Login: admin@admin.com / admin
→ Servers
  → medusa-postgres
    → Databases
      → medusa-store
        → Schemas
          → recommendation  ← Xem ở đây!
            → Tables
              → rec_* (7 tables)
```

---

## 🐳 Docker Commands

### Service Management
```powershell
# Start all services
docker-compose up -d

# Start recommendation only
docker-compose up -d recommendation

# Restart recommendation
docker-compose restart recommendation

# Check status
docker-compose ps recommendation

# View logs
docker-compose logs -f recommendation

# Stop service
docker-compose stop recommendation
```

### Database Access
```powershell
# Connect to PostgreSQL
docker exec -it medusa_postgres psql -U postgres -d medusa-store

# Once connected:
\dn                           # List all schemas
\dt recommendation.*         # List tables in recommendation schema
\d recommendation.rec_user_interactions  # Describe table structure
SET search_path TO recommendation, public;
SELECT * FROM rec_user_interactions LIMIT 10;
```

---

## 🔌 API Endpoints

### Base URL
```
External: http://localhost:8001
Internal: http://recommendation:8001
```

### Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Health check |
| POST | `/track` | Track user interaction |
| GET | `/recommendations` | Get personalized recommendations |
| GET | `/user/{id}/preferences` | Get user preferences |
| POST | `/compute/similarities` | Batch compute similarities |
| POST | `/compute/user-preferences` | Update all user preferences |
| GET | `/docs` | API documentation |

### Quick Test
```powershell
# Health check
curl http://localhost:8001/health

# Track interaction
curl -X POST http://localhost:8001/track `
  -H "Content-Type: application/json" `
  -d '{
    "user_id": "test",
    "product_handle": "test-product",
    "interaction_type": "view"
  }'

# Get recommendations
curl "http://localhost:8001/recommendations?user_id=test&limit=5"
```

---

## 📊 Database Tables

| Table Name | Purpose | Row Count |
|------------|---------|-----------|
| `recommendation.rec_user_interactions` | Track all user actions | Check: `SELECT COUNT(*) FROM recommendation.rec_user_interactions;` |
| `recommendation.rec_user_preferences` | Learned user preferences | Check: `SELECT COUNT(*) FROM recommendation.rec_user_preferences;` |
| `recommendation.rec_product_similarities` | Pre-computed similarities | Populated by batch job |
| `recommendation.rec_frequently_together` | Products bought together | Populated by batch job |
| `recommendation.rec_recommendations_cache` | Cached recommendations | Auto-populated, TTL 1h |
| `recommendation.rec_user_segments` | User clustering | Future use |
| `recommendation.rec_analytics` | Daily analytics | Future use |

---

## 🔍 Troubleshooting

### Service không start?
```powershell
# Check logs
docker-compose logs recommendation

# Rebuild
docker-compose build --no-cache recommendation
docker-compose up -d recommendation
```

### Không thấy tables trong pgAdmin?
1. ✅ Refresh pgAdmin (right-click → Refresh)
2. ✅ Check trong schema **recommendation**, KHÔNG phải public
3. ✅ Tables có prefix `rec_*`
4. ✅ Chắc chắn đang xem database `medusa-store`
5. ✅ Nếu vẫn không thấy schema `recommendation`, rebuild service:
   ```powershell
   docker-compose build --no-cache recommendation
   docker-compose up -d recommendation
   ```

### Database empty?
```powershell
# Re-init schema (auto via rebuild)
docker-compose build --no-cache recommendation
docker-compose up -d recommendation

# Or manual re-init
docker exec -i medusa_postgres psql -U postgres -d medusa-store < recommendation-service/database/init_schema.sql

# Run test to populate data
.\recommendation-service\test_service.ps1
```

### Recommendations trống?
```powershell
# Check có data không
docker exec medusa_postgres psql -U postgres -d medusa-store -c "SELECT COUNT(*) FROM recommendation.rec_user_interactions;"

# Track some interactions
.\recommendation-service\test_service.ps1

# Get recommendations again
curl "http://localhost:8001/recommendations?user_id=test_user_002&limit=5"
```

---

## 🎯 Integration Points

### Frontend → Recommendation
```typescript
// File: vercel-commerce/app/api/recommendations/route.ts
const RECOMMENDATION_SERVICE_URL = 
  process.env.RECOMMENDATION_SERVICE_URL || 'http://localhost:8001';

const response = await fetch(
  `${RECOMMENDATION_SERVICE_URL}/recommendations?...`
);
```

### Recommendation → Database
```python
# File: recommendation-service/app/main.py
DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/medusa-store"
#                                            ↑
#                                Container name (Docker network)

db_pool = await asyncpg.create_pool(DATABASE_URL)
```

### Recommendation → Redis
```python
# File: recommendation-service/app/config.py
redis_url = "redis://redis:6379/1"
#                    ↑         ↑
#            Container name  Database 1
```

---

## 🚀 Deployment Checklist

- [ ] Build: `docker-compose build recommendation`
- [ ] Start: `docker-compose up -d recommendation`
- [ ] Check logs: `docker-compose logs recommendation`
- [ ] Health check: `curl http://localhost:8001/health`
- [ ] Verify tables: `docker exec medusa_postgres psql -U postgres -d medusa-store -c "SELECT tablename FROM pg_tables WHERE schemaname = 'recommendation';"`
- [ ] Test API: `.\recommendation-service\test_service.ps1`
- [ ] Check pgAdmin: Tables visible in public schema
- [ ] Frontend .env: `RECOMMENDATION_SERVICE_URL=http://recommendation:8001`

---

## 📚 Documentation Links

- **Architecture**: [RECOMMENDATION_ARCHITECTURE.md](RECOMMENDATION_ARCHITECTURE.md)
- **Visual Diagrams**: [VISUAL_ARCHITECTURE.md](VISUAL_ARCHITECTURE.md)
- **Deployment Guide**: [recommendation-service/DEPLOYMENT_GUIDE.md](../recommendation-service/DEPLOYMENT_GUIDE.md)
- **Quick Start**: [recommendation-service/QUICKSTART.md](../recommendation-service/QUICKSTART.md)
- **Test Report**: [recommendation-service/TEST_REPORT.md](../recommendation-service/TEST_REPORT.md)
- **API Docs**: http://localhost:8001/docs

---

## 💡 Key Insights

### 1. Organized Schema Architecture
```
PostgreSQL Container
└── Database: medusa-store
    ├── Schema: public
    │   └── Medusa tables (product, cart, order, ...)
    ├── Schema: chatbot
    │   └── Chatbot tables (messages, sessions, settings)
    └── Schema: recommendation  ← Dedicated schema!
        └── Recommendation tables (rec_*)
```

### 2. Schema Separation Benefits
✅ **Có schema riêng** `recommendation`  
✅ **Tách biệt** rõ ràng với Medusa (public schema)  
✅ **Dễ quản lý** permissions và backup  
✅ **Thống nhất** với chatbot service architecture

### 3. Docker Network Communication
```
Frontend → recommendation:8001    (Container name)
Recommendation → postgres:5432    (Container name)
Recommendation → redis:6379       (Container name)
Recommendation → medusa:9000      (Container name)
```

### 4. Auto Initialization
```
Container start
→ init_db.sh runs
→ Checks PostgreSQL ready
→ Executes init_schema.sql
→ Creates 7 tables
→ Starts FastAPI
→ Ready!
```

---

**Last Updated**: December 14, 2024  
**Status**: ✅ Production Ready  
**All Tests**: PASSED
