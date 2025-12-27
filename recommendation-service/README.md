# Recommendation Service Setup Guide

## Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  Vercel Commerce│─────>│  Recommendation  │─────>│   PostgreSQL    │
│   (Frontend)    │      │    Service       │      │  (rec_* tables) │
│                 │<─────│  (Python/FastAPI)│<─────│                 │
└─────────────────┘      └──────────────────┘      └─────────────────┘
         │                        │
         │                        │
         v                        v
    ┌──────────┐          ┌──────────┐
    │  Medusa  │          │  Redis   │
    │ Backend  │          │  Cache   │
    └──────────┘          └──────────┘
```

## Deployment Steps

### 1. Build and Start Services

```bash
# Build all services
docker-compose build

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f recommendation
```

### 2. Verify Database Schema

```bash
# Connect to PostgreSQL
docker exec -it medusa_postgres psql -U postgres -d medusa-store

# List recommendation tables
\dt rec_*

# Check table structure
\d rec_user_interactions
\d rec_user_preferences
\d rec_product_similarities
```

Expected output:
```
                    List of relations
 Schema |            Name             | Type  |  Owner   
--------+-----------------------------+-------+----------
 public | rec_analytics               | table | postgres
 public | rec_frequently_together     | table | postgres
 public | rec_product_similarities    | table | postgres
 public | rec_recommendations_cache   | table | postgres
 public | rec_user_interactions       | table | postgres
 public | rec_user_preferences        | table | postgres
 public | rec_user_segments           | table | postgres
```

### 3. Test Recommendation Service

```bash
# Health check
curl http://localhost:8001/health

# Track user interaction
curl -X POST http://localhost:8001/track \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "session_id": "session_456",
    "product_id": "prod_789",
    "interaction_type": "view",
    "metadata": {"category": "backpacks"}
  }'

# Get recommendations
curl "http://localhost:8001/recommendations?user_id=user_123&limit=5"
```

### 4. Frontend Integration

Update `.env.local`:
```bash
RECOMMENDATION_SERVICE_URL=http://recommendation:8001
```

The frontend will automatically:
- Track user interactions (view, add_to_cart, purchase, wishlist)
- Fetch personalized recommendations for homepage
- Show recently viewed products
- Display similar products on product pages

## Algorithms

### 1. Hybrid Recommendations (Default)
Combines content-based and collaborative filtering:
- **Content**: 40% weight - matches user's category preferences
- **Collaborative**: 60% weight - learns from similar users' purchases

### 2. Content-Based Filtering
Recommends products similar to what user viewed:
- Category matching (60% weight)
- Title similarity (40% weight)

### 3. Collaborative Filtering
Recommends based on similar users:
- User-user similarity
- Item-item similarity
- Purchase patterns

### 4. Trending Products
Fallback for new users:
- Most viewed in last 7 days
- Highest add-to-cart rate

### 5. Frequently Bought Together
Product bundles:
- Co-occurrence analysis
- Association rules

## Batch Jobs

### Compute Product Similarities

```bash
# Manually trigger
curl -X POST http://localhost:8001/compute/similarities

# Via cron (add to crontab)
0 2 * * * curl -X POST http://localhost:8001/compute/similarities
```

### Update User Preferences

```bash
# Manually trigger
curl -X POST http://localhost:8001/compute/user-preferences

# Via cron
0 3 * * * curl -X POST http://localhost:8001/compute/user-preferences
```

## Monitoring

### Check Service Logs
```bash
docker-compose logs -f recommendation
```

### Database Analytics
```sql
-- Total interactions
SELECT COUNT(*) FROM rec_user_interactions;

-- Top products
SELECT product_id, COUNT(*) as views
FROM rec_user_interactions
WHERE interaction_type = 'view'
GROUP BY product_id
ORDER BY views DESC
LIMIT 10;

-- User preferences
SELECT user_id, category, score
FROM rec_user_preferences
ORDER BY score DESC;

-- Cache hit rate
SELECT COUNT(*) FROM rec_recommendations_cache;
```

### Redis Cache
```bash
# Connect to Redis
docker exec -it medusa_redis redis-cli

# List keys
KEYS rec:*

# Get cached recommendations
GET rec:recommendations:user_123
```

## Configuration

Edit `recommendation-service/app/config.py`:

```python
class Settings:
    # Algorithm weights
    CONTENT_WEIGHT = 0.4
    COLLABORATIVE_WEIGHT = 0.6
    
    # Cache TTL (seconds)
    CACHE_TTL = 3600
    
    # Batch job settings
    SIMILARITY_THRESHOLD = 0.3
    MAX_RECOMMENDATIONS = 50
```

## Troubleshooting

### Service not starting
```bash
# Check logs
docker-compose logs recommendation

# Rebuild
docker-compose build recommendation
docker-compose up -d recommendation
```

### Database connection error
```bash
# Verify PostgreSQL is running
docker ps | grep postgres

# Check connection
docker exec -it medusa_recommendation python -c "import asyncpg; print('OK')"
```

### Empty recommendations
```bash
# Check if tables have data
docker exec -it medusa_postgres psql -U postgres -d medusa-store -c "SELECT COUNT(*) FROM rec_user_interactions;"

# Trigger batch computation
curl -X POST http://localhost:8001/compute/similarities
```

## Production Deployment

### Environment Variables
```bash
DATABASE_URL=postgresql://user:pass@host:5432/dbname
REDIS_URL=redis://host:6379/1
MEDUSA_BACKEND_URL=https://api.yourstore.com
LOG_LEVEL=INFO
```

### Scaling
- Run multiple recommendation service instances
- Use load balancer (nginx/traefik)
- Enable Redis clustering for cache
- Set up PostgreSQL read replicas

### Monitoring
- Prometheus metrics endpoint: `/metrics`
- Grafana dashboards for:
  - Request latency
  - Cache hit rate
  - Algorithm performance
  - Database query time
