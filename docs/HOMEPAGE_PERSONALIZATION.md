# Homepage Personalization Integration

## Overview

Tích hợp recommendation service vào homepage để cá nhân hóa trải nghiệm mua hàng.

## Components Updated

### 1. Homepage Layout
- **3 sản phẩm nổi bật**: Top personalized recommendations
- **Carousel ngang**: Recently viewed + More recommendations

### 2. Client-side Tracking
File: `lib/tracking/user-behavior.ts`

Tracks các hành động:
- `view`: Xem sản phẩm
- `add_to_cart`: Thêm vào giỏ
- `purchase`: Mua hàng
- `wishlist_add`: Thêm wishlist
- `search`: Tìm kiếm

### 3. API Integration

#### Track Endpoint
```typescript
POST /api/recommendations/track
{
  "user_id": "user_123",
  "session_id": "session_456",
  "product_id": "prod_789",
  "interaction_type": "view",
  "metadata": {
    "category": "backpacks",
    "price": 2737000
  }
}
```

#### Get Recommendations
```typescript
GET /api/recommendations?userId=user_123&sessionId=session_456&limit=10
```

Response:
```json
{
  "recommendations": [
    {
      "product_id": "prod_789",
      "title": "JanSport Superbreak",
      "score": 0.95,
      "reason": "Based on your viewing history"
    }
  ],
  "algorithm": "hybrid",
  "personalized": true
}
```

## Implementation Steps

### Step 1: Update Homepage

File: `app/page.tsx`

```typescript
import { PersonalizedRecommendations } from 'components/recommendations/personalized';
import { RecentlyViewed } from 'components/recommendations/recently-viewed';

export default async function HomePage() {
  return (
    <>
      {/* Hero section */}
      <Hero />
      
      {/* 3 sản phẩm nổi bật - Personalized */}
      <Suspense>
        <PersonalizedRecommendations limit={3} variant="grid" />
      </Suspense>
      
      {/* Recently viewed carousel */}
      <Suspense>
        <RecentlyViewed />
      </Suspense>
      
      {/* More personalized recommendations */}
      <Suspense>
        <PersonalizedRecommendations 
          limit={10} 
          variant="carousel"
          title="Recommended for you"
        />
      </Suspense>
      
      {/* Existing sections */}
      <Footer />
    </>
  );
}
```

### Step 2: Personalized Grid Component

File: `components/recommendations/personalized.tsx`

```typescript
'use client';

import { useEffect, useState } from 'react';
import { getRecommendations } from 'lib/tracking/user-behavior';
import Grid from 'components/grid';
import { GridTileImage } from 'components/grid/tile';
import Link from 'next/link';

export function PersonalizedRecommendations({ 
  limit = 3, 
  variant = 'grid',
  title = 'Recommended for you' 
}: { 
  limit?: number; 
  variant?: 'grid' | 'carousel';
  title?: string;
}) {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchRecs() {
      try {
        const recs = await getRecommendations(limit);
        setProducts(recs.recommendations || []);
      } catch (err) {
        console.error('Failed to load recommendations:', err);
      } finally {
        setLoading(false);
      }
    }
    
    fetchRecs();
  }, [limit]);

  if (loading) {
    return <div className="animate-pulse">Loading recommendations...</div>;
  }

  if (products.length === 0) {
    return null;
  }

  if (variant === 'carousel') {
    return (
      <section className="w-full pb-12">
        <h2 className="mb-4 text-2xl font-bold">{title}</h2>
        <div className="overflow-x-auto">
          <div className="flex gap-4">
            {products.map((product) => (
              <Link
                key={product.product_id}
                href={`/product/${product.handle}`}
                className="min-w-[200px]"
              >
                <GridTileImage
                  alt={product.title}
                  label={{
                    title: product.title,
                    amount: product.price,
                    currencyCode: 'VND'
                  }}
                  src={product.thumbnail}
                  fill
                  sizes="200px"
                />
              </Link>
            ))}
          </div>
        </div>
      </section>
    );
  }

  // Grid variant (3 products)
  return (
    <Grid className="grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
      {products.map((product, i) => (
        <Grid.Item key={product.product_id} className="animate-fadeIn">
          <Link
            className="relative block aspect-square h-full w-full"
            href={`/product/${product.handle}`}
          >
            <GridTileImage
              src={product.thumbnail}
              fill
              sizes={
                i === 0
                  ? '(min-width: 1024px) 66vw, 100vw'
                  : '(min-width: 1024px) 33vw, 50vw'
              }
              priority={i === 0}
              alt={product.title}
              label={{
                position: i === 0 ? 'center' : 'bottom',
                title: product.title as string,
                amount: product.price,
                currencyCode: 'VND'
              }}
            />
          </Link>
        </Grid.Item>
      ))}
    </Grid>
  );
}
```

### Step 3: Recently Viewed Component

File: `components/recommendations/recently-viewed.tsx`

Already created ✅

### Step 4: Track Product Views

File: `app/product/[handle]/page.tsx`

```typescript
import { TrackingWrapper } from 'components/tracking/tracking-wrapper';

export default async function ProductPage({ params }: Props) {
  const product = await getProduct(params.handle);
  
  return (
    <TrackingWrapper
      productId={product.id}
      productHandle={product.handle}
      interactionType="view"
      metadata={{
        category: product.category,
        price: product.priceRange.maxVariantPrice.amount,
        title: product.title
      }}
    >
      {/* Product content */}
      <ProductDescription product={product} />
    </TrackingWrapper>
  );
}
```

### Step 5: Track Add to Cart

File: `components/cart/add-to-cart.tsx`

Already updated with tracking ✅

### Step 6: Track Purchases

File: `app/checkout/success/page.tsx`

```typescript
'use client';

import { useEffect } from 'react';
import { trackInteraction } from 'lib/tracking/user-behavior';

export default function CheckoutSuccessPage() {
  useEffect(() => {
    // Track purchase for all items in order
    const orderItems = getOrderItems(); // Get from cart/order
    
    orderItems.forEach(item => {
      trackInteraction({
        productId: item.product_id,
        productHandle: item.handle,
        interactionType: 'purchase',
        metadata: {
          quantity: item.quantity,
          price: item.price
        }
      });
    });
  }, []);
  
  return (
    <div>
      <h1>Order Confirmed!</h1>
      {/* Success content */}
    </div>
  );
}
```

## Testing

### 1. View Products
```bash
# Open homepage
http://localhost:3000

# View product
http://localhost:3000/product/jansport-superbreak-plus-backpack

# Check console logs for tracking events
```

### 2. Check Database
```sql
-- Check tracked interactions
SELECT * FROM rec_user_interactions ORDER BY created_at DESC LIMIT 10;

-- Check user preferences
SELECT * FROM rec_user_preferences;

-- Check recommendations cache
SELECT * FROM rec_recommendations_cache ORDER BY created_at DESC LIMIT 5;
```

### 3. Test API
```bash
# Get recommendations
curl "http://localhost:3000/api/recommendations?userId=user_123&limit=5"

# Track interaction
curl -X POST http://localhost:3000/api/recommendations/track \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "product_id": "prod_789",
    "interaction_type": "view"
  }'
```

## Monitoring

### Frontend Console
```javascript
// Track events in browser console
window.trackingEvents = [];

// Override tracking function to log
const originalTrack = trackInteraction;
trackInteraction = (...args) => {
  window.trackingEvents.push(args);
  return originalTrack(...args);
};

// View all tracked events
console.table(window.trackingEvents);
```

### Backend Logs
```bash
# Watch recommendation service logs
docker-compose logs -f recommendation

# Watch vercel-commerce logs  
docker-compose logs -f vercel-commerce
```

## Algorithms Explained

### Hybrid Algorithm (Default)
```
Score = 0.4 × Content_Score + 0.6 × Collaborative_Score

Content_Score:
- Category match: 0.6
- Title similarity: 0.4

Collaborative_Score:
- Similar users' purchases
- Item-item similarity
```

### Fallback Strategy
1. **New User**: Trending products (most viewed last 7 days)
2. **Few Interactions**: Content-based (category matching)
3. **Active User**: Hybrid (content + collaborative)

## Performance Optimization

### Caching
- Redis cache: 1 hour TTL
- Browser localStorage: Recently viewed
- Database cache table: Pre-computed recommendations

### Batch Jobs
```bash
# Run every 2 AM
0 2 * * * curl -X POST http://localhost:8001/compute/similarities

# Run every 3 AM
0 3 * * * curl -X POST http://localhost:8001/compute/user-preferences
```

## Troubleshooting

### Empty Recommendations
1. Check if tracking is working: `SELECT COUNT(*) FROM rec_user_interactions`
2. Run similarity computation: `curl -X POST http://localhost:8001/compute/similarities`
3. Check service logs: `docker-compose logs recommendation`

### Slow Response
1. Enable caching in config
2. Run batch jobs to pre-compute
3. Add database indexes if needed

### Wrong Recommendations
1. Check user preferences: `SELECT * FROM rec_user_preferences WHERE user_id = 'xxx'`
2. Verify algorithm weights in config
3. Review tracking metadata quality
