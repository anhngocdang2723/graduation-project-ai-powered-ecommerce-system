-- Recommendation Service Analytics Queries

-- ==========================================
-- User Behavior Analytics
-- ==========================================

-- Total interactions by type
SELECT 
    interaction_type,
    COUNT(*) as count,
    COUNT(DISTINCT user_id) as unique_users
FROM rec_user_interactions
GROUP BY interaction_type
ORDER BY count DESC;

-- Top viewed products
SELECT 
    product_id,
    COUNT(*) as views,
    COUNT(DISTINCT user_id) as unique_viewers
FROM rec_user_interactions
WHERE interaction_type = 'view'
GROUP BY product_id
ORDER BY views DESC
LIMIT 10;

-- Top purchased products
SELECT 
    product_id,
    COUNT(*) as purchases,
    COUNT(DISTINCT user_id) as unique_buyers
FROM rec_user_interactions
WHERE interaction_type = 'purchase'
GROUP BY product_id
ORDER BY purchases DESC
LIMIT 10;

-- Conversion funnel
SELECT 
    COUNT(DISTINCT CASE WHEN interaction_type = 'view' THEN user_id END) as viewers,
    COUNT(DISTINCT CASE WHEN interaction_type = 'add_to_cart' THEN user_id END) as cart_adds,
    COUNT(DISTINCT CASE WHEN interaction_type = 'purchase' THEN user_id END) as buyers,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN interaction_type = 'add_to_cart' THEN user_id END) / 
          NULLIF(COUNT(DISTINCT CASE WHEN interaction_type = 'view' THEN user_id END), 0), 2) as cart_rate,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN interaction_type = 'purchase' THEN user_id END) / 
          NULLIF(COUNT(DISTINCT CASE WHEN interaction_type = 'add_to_cart' THEN user_id END), 0), 2) as conversion_rate
FROM rec_user_interactions;

-- ==========================================
-- User Preferences
-- ==========================================

-- Top categories by user preference
SELECT 
    category,
    COUNT(DISTINCT user_id) as users,
    ROUND(AVG(score), 2) as avg_score,
    ROUND(SUM(score), 2) as total_score
FROM rec_user_preferences
GROUP BY category
ORDER BY total_score DESC;

-- User category preferences
SELECT 
    user_id,
    category,
    score,
    interaction_count
FROM rec_user_preferences
WHERE user_id = 'test_user_001'
ORDER BY score DESC;

-- ==========================================
-- Product Similarities
-- ==========================================

-- Product with most similar products
SELECT 
    product_id,
    COUNT(*) as similar_count,
    ROUND(AVG(similarity_score), 3) as avg_similarity
FROM rec_product_similarities
GROUP BY product_id
ORDER BY similar_count DESC
LIMIT 10;

-- Similar products for a specific product
SELECT 
    similar_product_id,
    similarity_score,
    similarity_type
FROM rec_product_similarities
WHERE product_id = 'prod_01JNDQ13RMVQFQ0RPDQMQQX9XZ'
ORDER BY similarity_score DESC
LIMIT 10;

-- ==========================================
-- Frequently Bought Together
-- ==========================================

-- Top product pairs
SELECT 
    product_id_1,
    product_id_2,
    co_occurrence_count,
    ROUND(confidence, 3) as confidence
FROM rec_frequently_together
ORDER BY co_occurrence_count DESC
LIMIT 10;

-- ==========================================
-- Cache Performance
-- ==========================================

-- Cache entries by algorithm
SELECT 
    algorithm,
    COUNT(*) as cache_entries,
    MIN(created_at) as oldest_entry,
    MAX(created_at) as newest_entry
FROM rec_recommendations_cache
GROUP BY algorithm;

-- Cache hit rate (would need to implement tracking)
SELECT 
    COUNT(*) as total_cached,
    SUM(CASE WHEN created_at > NOW() - INTERVAL '1 hour' THEN 1 ELSE 0 END) as fresh_cache,
    ROUND(100.0 * SUM(CASE WHEN created_at > NOW() - INTERVAL '1 hour' THEN 1 ELSE 0 END) / 
          COUNT(*), 2) as fresh_percentage
FROM rec_recommendations_cache;

-- ==========================================
-- User Segments
-- ==========================================

-- User distribution by segment
SELECT 
    segment_name,
    COUNT(*) as user_count,
    ROUND(AVG(segment_score), 3) as avg_score
FROM rec_user_segments
GROUP BY segment_name
ORDER BY user_count DESC;

-- ==========================================
-- Daily Analytics
-- ==========================================

-- Trending products (last 7 days)
SELECT 
    product_id,
    SUM(view_count) as total_views,
    SUM(cart_count) as total_carts,
    SUM(purchase_count) as total_purchases,
    ROUND(100.0 * SUM(purchase_count) / NULLIF(SUM(cart_count), 0), 2) as conversion_rate
FROM rec_analytics
WHERE date >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY product_id
ORDER BY total_views DESC
LIMIT 10;

-- Daily trend
SELECT 
    date,
    SUM(view_count) as views,
    SUM(cart_count) as carts,
    SUM(purchase_count) as purchases
FROM rec_analytics
WHERE date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY date
ORDER BY date DESC;

-- ==========================================
-- Data Quality Checks
-- ==========================================

-- Check for orphaned interactions (products not in product table)
SELECT DISTINCT ri.product_id
FROM rec_user_interactions ri
LEFT JOIN product p ON ri.product_id = p.id
WHERE p.id IS NULL
LIMIT 10;

-- Check for duplicate similarities
SELECT 
    product_id,
    similar_product_id,
    COUNT(*) as duplicates
FROM rec_product_similarities
GROUP BY product_id, similar_product_id
HAVING COUNT(*) > 1;

-- Check for self-similarities (should not exist)
SELECT COUNT(*)
FROM rec_product_similarities
WHERE product_id = similar_product_id;
