-- Reset all recommendation data for demo
-- This will clear all user interactions, preferences, cache, etc.

SET search_path TO recommendation, public;

-- Clear all tables
TRUNCATE TABLE recommendation.rec_analytics CASCADE;
TRUNCATE TABLE recommendation.rec_frequently_together CASCADE;
TRUNCATE TABLE recommendation.rec_product_similarities CASCADE;
TRUNCATE TABLE recommendation.rec_recommendations_cache CASCADE;
TRUNCATE TABLE recommendation.rec_user_interactions CASCADE;
TRUNCATE TABLE recommendation.rec_user_preferences CASCADE;
TRUNCATE TABLE recommendation.rec_user_segments CASCADE;

-- Verify all tables are empty
SELECT 'rec_analytics' as table_name, COUNT(*) as count FROM recommendation.rec_analytics
UNION ALL
SELECT 'rec_frequently_together', COUNT(*) FROM recommendation.rec_frequently_together
UNION ALL
SELECT 'rec_product_similarities', COUNT(*) FROM recommendation.rec_product_similarities
UNION ALL
SELECT 'rec_recommendations_cache', COUNT(*) FROM recommendation.rec_recommendations_cache
UNION ALL
SELECT 'rec_user_interactions', COUNT(*) FROM recommendation.rec_user_interactions
UNION ALL
SELECT 'rec_user_preferences', COUNT(*) FROM recommendation.rec_user_preferences
UNION ALL
SELECT 'rec_user_segments', COUNT(*) FROM recommendation.rec_user_segments;
