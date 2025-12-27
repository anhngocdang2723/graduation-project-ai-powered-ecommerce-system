# Recommendation Service Database

## Setup Instructions

### Manual Initialization

If the schema isn't automatically created, run:

```bash
docker exec -i medusa_postgres psql -U postgres -d medusa-store < recommendation-service/database/init_schema.sql
```

### Verify Tables Created

```bash
docker exec -it medusa_postgres psql -U postgres -d medusa-store -c "\dt rec_*"
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

## Database Schema Overview

### User Interactions
- **rec_user_interactions**: Tracks all user actions (view, add_to_cart, purchase, wishlist)
- **rec_user_preferences**: Aggregated user preferences by category

### Product Relationships
- **rec_product_similarities**: Pre-computed similarity scores between products
- **rec_frequently_together**: Products frequently purchased together

### Performance Optimization
- **rec_recommendations_cache**: Cached recommendation results
- **rec_user_segments**: User clustering for collaborative filtering
- **rec_analytics**: Daily analytics for trending products

## Batch Jobs

Run periodic batch jobs to update recommendations:

```bash
# Compute all product similarities
curl -X POST http://localhost:8001/compute/similarities

# Update user preferences
curl -X POST http://localhost:8001/compute/user-preferences
```

Schedule via cron or K8s CronJob for production.
