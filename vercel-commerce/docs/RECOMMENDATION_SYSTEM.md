# Simple Recommendation System - Implementation Guide

## Overview
Hệ thống recommendation đơn giản dựa trên tracking hành vi người dùng (product views, add to cart, wishlist).

## Architecture

### 1. Client-side Tracking
**File**: `lib/tracking/user-behavior.ts`
- Track user interactions (view, add_to_cart, wishlist, search)
- Store locally in localStorage (last 100 interactions)
- Async send to backend API

### 2. Tracking Components
**File**: `components/tracking/tracking-wrapper.tsx`
- `ProductViewTracker`: Auto-track khi user xem sản phẩm
- `trackAddToCart()`: Track khi thêm vào giỏ
- `trackWishlist()`: Track wishlist actions
- `trackSearch()`: Track search queries

### 3. Backend API Endpoints

#### `/api/recommendations/track` (POST)
Nhận và log user interactions (có thể lưu vào database sau)

#### `/api/recommendations` (GET)
Trả về personalized recommendations
- Hiện tại: Random products (placeholder)
- Sẽ cải tiến: Content-based, collaborative filtering

### 4. Recommendation Components

#### `PersonalizedRecommendations`
**File**: `components/recommendations/personalized.tsx`
- Hiển thị "Recommended For You" trên homepage
- Fetch từ `/api/recommendations`

#### `RecentlyViewedProducts`
**File**: `components/recommendations/recently-viewed.tsx`
- Hiển thị "Recently Viewed" products
- Lấy từ localStorage

## Current Features

✅ **Implemented:**
- [x] Track product views automatically
- [x] Track add to cart events
- [x] Track wishlist add/remove
- [x] Store interactions in localStorage
- [x] Recently viewed products section
- [x] Personalized recommendations section (random for now)
- [x] API endpoints for tracking

🔄 **Next Steps:**
- [ ] Store interactions in database (Postgres)
- [ ] Implement content-based filtering algorithm
- [ ] Add collaborative filtering
- [ ] Category preference learning
- [ ] Price range preferences
- [ ] "Frequently bought together" logic

## Usage

### Track Product View
```tsx
import { ProductViewTracker } from 'components/tracking/tracking-wrapper';

<ProductViewTracker 
  productId="prod_123"
  productHandle="coffee-mug"
  category="Mugs"
  price="250000"
/>
```

### Track Add to Cart
```tsx
import { trackAddToCart } from 'components/tracking/tracking-wrapper';

trackAddToCart(productId, productHandle, quantity);
```

### Show Recommendations
```tsx
import { PersonalizedRecommendations } from 'components/recommendations/personalized';
import { RecentlyViewedProducts } from 'components/recommendations/recently-viewed';

<RecentlyViewedProducts />
<PersonalizedRecommendations />
```

## Data Structure

### User Interaction
```typescript
{
  productId: "prod_123",
  productHandle: "coffee-mug",
  interactionType: "view" | "add_to_cart" | "wishlist" | "search",
  timestamp: 1234567890,
  sessionId: "session_abc123",
  metadata: {
    category: "Mugs",
    price: "250000",
    // custom fields
  }
}
```

## Database Schema (Future)

```sql
CREATE TABLE user_interactions (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    product_id VARCHAR,
    product_handle VARCHAR,
    interaction_type VARCHAR NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    session_id VARCHAR,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_user_interactions_user_id ON user_interactions(user_id);
CREATE INDEX idx_user_interactions_product ON user_interactions(product_handle);
CREATE INDEX idx_user_interactions_timestamp ON user_interactions(timestamp);
```

## Algorithm Ideas (Future Enhancement)

### 1. Content-Based Filtering
```python
# Tương tự sản phẩm dựa trên:
- Category overlap
- Price range similarity
- Tag similarity
- Description similarity (TF-IDF)
```

### 2. Collaborative Filtering
```python
# User-based:
- Tìm users có lịch sử xem/mua giống nhau
- Gợi ý products mà similar users đã mua

# Item-based:
- "Customers who bought X also bought Y"
- Co-occurrence matrix
```

### 3. Hybrid Approach
```python
final_score = 0.6 * collaborative_score + 0.4 * content_score
```

## Testing

1. **View products**: Vào trang sản phẩm → check localStorage `user_interactions`
2. **Add to cart**: Thêm vào giỏ → check console logs
3. **Wishlist**: Add/remove wishlist → check console logs
4. **Homepage**: Xem "Recently Viewed" và "Recommended For You" sections

## Performance

- ✅ Lightweight: LocalStorage only ~10KB
- ✅ Non-blocking: Async API calls
- ✅ Fast: No database queries yet (all client-side)
- ⚠️ Scaling: Need database when users grow

## Next Phase Implementation

1. Add Postgres table for `user_interactions`
2. Python service for computing recommendations
3. Batch job (cron) to update product similarities
4. Cache recommendations in Redis
5. A/B testing different algorithms
6. Analytics dashboard

## References
- [RECOMMENDATIONS_PLAN.md](../../../docs/RECOMMENDATIONS_PLAN.md)
