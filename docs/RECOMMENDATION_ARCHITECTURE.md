# 📘 Giải Thích Chi Tiết Recommendation Service

## 🏗️ Kiến Trúc Tổng Quan

### 1. Hệ Thống Đã Được Tích Hợp Hoàn Toàn

**TẤT CẢ services đã được thêm vào file `docker-compose.yml` tổng** ✅

```yaml
# File: docker-compose.yml (ở thư mục gốc graduation-project)
services:
  postgres:      # Port 5432 - Database chung cho TẤT CẢ services
  redis:         # Port 6379 - Cache chung
  medusa:        # Port 9000 - E-commerce backend
  chatbot:       # Port 8000 - AI chatbot
  chatbot_worker:# Background worker
  recommendation:# Port 8001 - ML recommendation ⭐ MỚI
  pgadmin:       # Port 5050 - Database UI
```

### 2. Cấu Trúc Database

#### ⚠️ QUAN TRỌNG: Không có schema riêng!

Tables recommendation được tạo trong **PUBLIC schema** (schema mặc định của PostgreSQL), **KHÔNG PHẢI** schema riêng!

```
Database: medusa-store
├── Schema: public (DEFAULT)
│   ├── product              (Medusa tables)
│   ├── cart
│   ├── order
│   ├── ...
│   ├── chatbot_context      (Chatbot tables)
│   ├── chatbot_responses
│   ├── rec_user_interactions      ⭐ (Recommendation tables)
│   ├── rec_user_preferences       ⭐
│   ├── rec_product_similarities   ⭐
│   ├── rec_frequently_together    ⭐
│   ├── rec_recommendations_cache  ⭐
│   ├── rec_user_segments          ⭐
│   └── rec_analytics              ⭐
```

#### Tại sao không thấy trong pgAdmin?

**Lý do**: Tables nằm trong schema `public`, không phải schema riêng!

**Cách xem trong pgAdmin**:
1. Mở pgAdmin: http://localhost:5050
2. Login: admin@admin.com / admin
3. Kết nối server "medusa-postgres"
4. Mở: Servers → medusa-postgres → Databases → medusa-store → Schemas → **public** → Tables
5. Tìm tables có prefix `rec_*`

**Hoặc dùng SQL**:
```sql
-- Xem tất cả tables recommendation
SELECT tablename FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename LIKE 'rec_%';
```

## 🔄 Cách Recommendation Service Hoạt Động

### Bước 1: Khởi Động (Startup)

```
docker-compose up -d recommendation
         ↓
Container medusa_recommendation starts
         ↓
init_db.sh chạy tự động
         ↓
Kiểm tra PostgreSQL ready
         ↓
Chạy database/init_schema.sql
         ↓
Tạo 7 tables trong public schema
         ↓
Khởi động FastAPI server (port 8001)
         ↓
Service READY! ✅
```

### Bước 2: User Interaction Tracking

```
User xem sản phẩm trên frontend
         ↓
Frontend gọi: POST /api/recommendations/track
         ↓
Next.js API proxy đến: http://recommendation:8001/track
         ↓
Recommendation service nhận request
         ↓
Lưu vào rec_user_interactions table
         ↓
Tự động update rec_user_preferences (học preferences)
         ↓
Response: { success: true, interaction_id: "..." }
```

**Code Flow**:
```
Frontend (vercel-commerce)
    ↓ HTTP Request
Next.js API Route (/api/recommendations/track)
    ↓ Proxy
Recommendation Service (FastAPI)
    ↓ SQL INSERT
PostgreSQL (public.rec_user_interactions)
```

### Bước 3: Get Recommendations

```
User vào homepage
         ↓
Frontend gọi: GET /api/recommendations?userId=xxx&limit=10
         ↓
Next.js API proxy đến: http://recommendation:8001/recommendations
         ↓
Recommendation Engine xử lý:
  1. Đọc user preferences từ rec_user_preferences
  2. Lấy recent interactions từ rec_user_interactions
  3. Check cache trong rec_recommendations_cache
  4. Nếu không có cache:
     a. Hybrid algorithm (40% content + 60% collaborative)
     b. Query products từ product table
     c. Tính similarity scores
     d. Lưu vào cache
  5. Return top N products
         ↓
Frontend hiển thị recommendations
```

## 🗄️ Chi Tiết Database Schema

### Table: rec_user_interactions
**Mục đích**: Lưu MỌI hành động của user

```sql
CREATE TABLE rec_user_interactions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    session_id TEXT,
    product_id TEXT,
    product_handle TEXT,
    interaction_type TEXT NOT NULL, -- view, add_to_cart, purchase, wishlist
    metadata JSONB,                 -- { category, price, title, ... }
    timestamp TIMESTAMP DEFAULT NOW()
);
```

**Ví dụ data**:
```json
{
  "id": "int_45c4bcd7bdb44dc8acafb8fc85ec7854",
  "user_id": "test_user_001",
  "product_id": "prod_01JNDQ13RMVQFQ0RPDQMQQX9XZ",
  "interaction_type": "view",
  "metadata": {
    "category": "backpacks",
    "price": 2737000,
    "title": "JanSport Superbreak Plus"
  },
  "timestamp": "2024-12-14 08:45:30"
}
```

### Table: rec_user_preferences
**Mục đích**: Học preferences từ interactions

```sql
CREATE TABLE rec_user_preferences (
    user_id TEXT PRIMARY KEY,
    category_scores JSONB,    -- { "backpacks": 1.0, "accessories": 0.5 }
    price_min DECIMAL,        -- Khoảng giá user thích
    price_max DECIMAL,
    preferred_brands JSONB,
    last_updated TIMESTAMP
);
```

**Cách học preferences**:
- View: +1.0 điểm
- Add to cart: +3.0 điểm
- Purchase: +5.0 điểm
- Wishlist: +2.0 điểm

### Table: rec_product_similarities
**Mục đích**: Pre-compute similarities giữa products

```sql
CREATE TABLE rec_product_similarities (
    product_id_1 TEXT,
    product_id_2 TEXT,
    similarity_score FLOAT,     -- 0.0 - 1.0
    similarity_type TEXT,       -- content, collaborative
    updated_at TIMESTAMP,
    PRIMARY KEY (product_id_1, product_id_2, similarity_type)
);
```

**Được tạo bởi batch job**:
```bash
curl -X POST http://localhost:8001/compute/similarities
```

### Table: rec_recommendations_cache
**Mục đích**: Cache kết quả để tăng tốc

```sql
CREATE TABLE rec_recommendations_cache (
    cache_key TEXT PRIMARY KEY,
    user_id TEXT,
    recommendations JSONB,      -- Array of products
    algorithm TEXT,             -- hybrid, trending, etc.
    created_at TIMESTAMP,
    expires_at TIMESTAMP        -- TTL: 1 hour
);
```

## 🔌 Integration với Các Services

### 1. Kết Nối Database

```python
# recommendation-service/app/main.py
DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/medusa-store"
                                        ↑
                                   Container name
                                   (trong Docker network)
```

**Tại sao dùng `@postgres` thay vì `@localhost`?**
- Services trong Docker network giao tiếp qua **container name**
- `postgres` = tên container PostgreSQL trong docker-compose.yml
- Chỉ expose port 5432 ra ngoài để pgAdmin/tools kết nối

### 2. Kết Nối Redis Cache

```python
REDIS_URL = "redis://redis:6379/1"
                    ↑         ↑
              Container    Database 1
                name      (0 = chatbot)
```

### 3. Kết Nối Medusa Backend

```python
MEDUSA_BACKEND_URL = "http://medusa:9000"
                            ↑
                    Medusa container
```

## 📊 Data Flow Complete

### Flow 1: User Browse Product

```
┌──────────────┐
│   Browser    │
│ localhost:   │
│    3000      │
└──────┬───────┘
       │ HTTP GET /product/abc
       ▼
┌──────────────┐
│ Vercel       │
│ Commerce     │ Next.js render product page
│ (Frontend)   │
└──────┬───────┘
       │ Auto tracking component mounted
       ▼
┌──────────────┐
│ POST /api/   │
│ recommend-   │ Next.js API route
│ ations/track │
└──────┬───────┘
       │ Proxy to recommendation service
       ▼
┌──────────────┐
│ Recommend-   │
│ ation Service│ FastAPI (port 8001)
│ (Container)  │
└──────┬───────┘
       │ SQL INSERT
       ▼
┌──────────────┐
│  PostgreSQL  │
│  Container   │ Table: rec_user_interactions
│  (postgres)  │
└──────────────┘
```

### Flow 2: Get Recommendations

```
┌──────────────┐
│   Browser    │ User vào homepage
└──────┬───────┘
       ▼
┌──────────────┐
│ GET /api/    │
│ recommend-   │ Next.js API route
│ ations       │
└──────┬───────┘
       ▼
┌──────────────┐
│ Recommend-   │ 1. Check Redis cache
│ ation Service├──────────────┐
│ (Container)  │              ▼
└──────┬───────┘        ┌──────────┐
       │                │  Redis   │
       │ Cache miss     │ (cache)  │
       │                └──────────┘
       │ 2. Get user preferences
       ▼
┌──────────────┐
│  PostgreSQL  │ Query rec_user_preferences
│  (postgres)  │ Query rec_product_similarities
└──────┬───────┘ Query product table
       │
       │ 3. Run ML algorithm
       ▼
┌──────────────┐
│ scikit-learn │ Calculate scores
│ numpy/pandas │ Rank products
└──────┬───────┘
       │ 4. Cache result
       ▼
┌──────────────┐
│  Redis       │ Store for 1 hour
│  (cache)     │
└──────┬───────┘
       │ 5. Return JSON
       ▼
┌──────────────┐
│   Browser    │ Display recommendations
└──────────────┘
```

## 🐳 Docker Compose Integration

### File Structure

```
graduation-project/
├── docker-compose.yml          ⭐ FILE TỔNG - Chứa TẤT CẢ services
├── my-medusa-store/
│   └── Dockerfile
├── chatbot-service/
│   └── Dockerfile
└── recommendation-service/     ⭐ MỚI
    ├── Dockerfile
    ├── init_db.sh             ⭐ Auto DB init
    └── database/
        └── init_schema.sql    ⭐ Schema definition
```

### Docker Network

```
Network: app_network (bridge)
├── medusa_postgres (postgres:5432)
├── medusa_redis (redis:6379)
├── medusa_backend (medusa:9000)
├── medusa_chatbot (chatbot:8000)
├── medusa_chatbot_worker
├── medusa_recommendation (recommendation:8001) ⭐
└── medusa_pgadmin (pgadmin:5050)
```

**Tất cả containers có thể giao tiếp với nhau qua tên container!**

### Environment Variables

#### Recommendation Service (.env)
```bash
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/medusa-store
REDIS_URL=redis://redis:6379/1
MEDUSA_BACKEND_URL=http://medusa:9000
CONTENT_WEIGHT=0.4
COLLABORATIVE_WEIGHT=0.6
CACHE_TTL=3600
```

#### Frontend (.env.local)
```bash
# Kết nối đến recommendation service
RECOMMENDATION_SERVICE_URL=http://recommendation:8001

# Hoặc từ browser (development)
NEXT_PUBLIC_RECOMMENDATION_URL=http://localhost:8001
```

## 🔍 Cách Verify Setup

### 1. Check Docker Containers
```powershell
docker-compose ps

# Phải thấy:
# medusa_recommendation   Up   0.0.0.0:8001->8001/tcp
```

### 2. Check Database Tables
```powershell
docker exec medusa_postgres psql -U postgres -d medusa-store -c "\dt rec_*"

# Phải thấy 7 tables:
# public | rec_analytics
# public | rec_frequently_together
# public | rec_product_similarities
# public | rec_recommendations_cache
# public | rec_user_interactions
# public | rec_user_preferences
# public | rec_user_segments
```

### 3. Check Service Health
```powershell
curl http://localhost:8001/health

# Response:
# {"status":"healthy","service":"recommendation"}
```

### 4. Check pgAdmin

1. Mở http://localhost:5050
2. Login: admin@admin.com / admin
3. Connect server (đã config sẵn trong servers.json)
4. Navigate: medusa-postgres → Databases → medusa-store → Schemas → **public** → Tables
5. Tìm tables bắt đầu với `rec_`

**Screenshot path**:
```
Servers
└── medusa-postgres
    └── Databases (1)
        └── medusa-store
            └── Schemas (1)
                └── public
                    ├── Tables (50+)  ← Xem ở đây!
                    │   ├── cart
                    │   ├── product
                    │   ├── rec_analytics          ⭐
                    │   ├── rec_user_interactions  ⭐
                    │   └── ...
                    └── Views
```

## 🚀 Deployment Flow

```bash
# 1. Build tất cả services
docker-compose build

# 2. Start theo thứ tự
docker-compose up -d postgres redis     # Database first
docker-compose up -d medusa              # Backend
docker-compose up -d chatbot recommendation  # AI services

# 3. Verify
docker-compose ps
curl http://localhost:8001/health
```

**Hoặc dùng script tự động**:
```powershell
.\deploy_all.ps1
```

## 📝 Tóm Tắt

### ✅ Đã Setup

1. **Docker Compose**: Tất cả services trong 1 file docker-compose.yml
2. **Database**: Tables được tạo trong `public` schema (không phải schema riêng)
3. **Network**: Tất cả containers trong cùng network `app_network`
4. **Auto Init**: Database schema tự động khởi tạo khi container start
5. **Health Checks**: All services có health endpoints

### 🔑 Key Points

- **Database**: Dùng chung PostgreSQL container cho Medusa + Chatbot + Recommendation
- **Schema**: Tables trong `public` schema, prefix `rec_*` để phân biệt
- **Network**: Containers giao tiếp qua tên (postgres, redis, medusa, recommendation)
- **Ports**: Mỗi service expose port riêng (9000, 8000, 8001)
- **Integration**: Frontend proxy requests đến recommendation service qua API routes

### 📍 Đường Dẫn File Quan Trọng

```
graduation-project/
├── docker-compose.yml                    ← Định nghĩa TẤT CẢ services
├── deploy_all.ps1                        ← Script deploy tự động
└── recommendation-service/
    ├── app/main.py                       ← FastAPI endpoints
    ├── app/services/recommendation_engine.py  ← ML algorithms
    ├── app/services/interaction_tracker.py    ← Track & learn
    ├── database/init_schema.sql          ← Database schema
    ├── init_db.sh                        ← Auto initialization
    └── Dockerfile                        ← Container build
```

---

**Kết luận**: Recommendation service đã được **HOÀN TOÀN TÍCH HỢP** vào hệ thống tổng, chia sẻ database với các services khác, và sẵn sàng sử dụng! 🎉
