-- Recommendation Service Schema
-- This schema stores all data needed for personalized recommendations

-- Create dedicated schema for recommendation service
CREATE SCHEMA IF NOT EXISTS recommendation;

-- Set search path to use recommendation schema
SET search_path TO recommendation, public;

-- User interactions table (views, carts, purchases, wishlist)
CREATE TABLE IF NOT EXISTS recommendation.rec_user_interactions (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255),
    product_id VARCHAR(255),
    product_handle VARCHAR(255),
    interaction_type VARCHAR(50) NOT NULL, -- view, add_to_cart, purchase, wishlist, search
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rec_interactions_user_id ON recommendation.rec_user_interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_rec_interactions_product ON recommendation.rec_user_interactions(product_handle);
CREATE INDEX IF NOT EXISTS idx_rec_interactions_type ON recommendation.rec_user_interactions(interaction_type);
CREATE INDEX IF NOT EXISTS idx_rec_interactions_timestamp ON recommendation.rec_user_interactions(timestamp DESC);

-- User preferences (learned from behavior)
CREATE TABLE IF NOT EXISTS recommendation.rec_user_preferences (
    user_id VARCHAR(255) PRIMARY KEY,
    category_scores JSONB, -- {"backpack": 0.8, "shirt": 0.3}
    price_min NUMERIC,
    price_max NUMERIC,
    preferred_brands JSONB,
    last_updated TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Product similarities (pre-computed)
CREATE TABLE IF NOT EXISTS recommendation.rec_product_similarities (
    product_id_1 VARCHAR(255) NOT NULL,
    product_id_2 VARCHAR(255) NOT NULL,
    similarity_score FLOAT NOT NULL,
    similarity_type VARCHAR(50) NOT NULL, -- content, collaborative, hybrid
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    PRIMARY KEY (product_id_1, product_id_2, similarity_type)
);

CREATE INDEX IF NOT EXISTS idx_rec_similarities_product1 ON recommendation.rec_product_similarities(product_id_1, similarity_score DESC);

-- Frequently bought together
CREATE TABLE IF NOT EXISTS recommendation.rec_frequently_together (
    product_id_1 VARCHAR(255) NOT NULL,
    product_id_2 VARCHAR(255) NOT NULL,
    co_occurrence_count INT NOT NULL DEFAULT 1,
    confidence_score FLOAT,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    PRIMARY KEY (product_id_1, product_id_2)
);

CREATE INDEX IF NOT EXISTS idx_rec_together_product1 ON recommendation.rec_frequently_together(product_id_1, confidence_score DESC);

-- Recommendation cache (for performance)
CREATE TABLE IF NOT EXISTS recommendation.rec_recommendations_cache (
    cache_key VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255),
    recommendations JSONB NOT NULL,
    algorithm VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_rec_cache_user ON recommendation.rec_recommendations_cache(user_id, expires_at);

-- User segments (for A/B testing)
CREATE TABLE IF NOT EXISTS recommendation.rec_user_segments (
    user_id VARCHAR(255) PRIMARY KEY,
    segment VARCHAR(50) NOT NULL, -- algorithm variant
    assigned_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Analytics tracking
CREATE TABLE IF NOT EXISTS recommendation.rec_analytics (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    recommendation_id VARCHAR(255),
    product_id VARCHAR(255),
    action VARCHAR(50) NOT NULL, -- impression, click, add_to_cart, purchase
    algorithm VARCHAR(50),
    position INT,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rec_analytics_timestamp ON recommendation.rec_analytics(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_rec_analytics_algorithm ON recommendation.rec_analytics(algorithm, action);

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA recommendation TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA recommendation TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA recommendation TO postgres;

COMMENT ON TABLE recommendation.rec_user_interactions IS 'Stores all user interactions with products';
COMMENT ON TABLE recommendation.rec_user_preferences IS 'Learned user preferences from behavior';
COMMENT ON TABLE recommendation.rec_product_similarities IS 'Pre-computed product similarities';
COMMENT ON TABLE recommendation.rec_frequently_together IS 'Products frequently bought together';
COMMENT ON TABLE recommendation.rec_recommendations_cache IS 'Cached recommendations for performance';
COMMENT ON TABLE recommendation.rec_analytics IS 'Analytics for recommendation performance tracking';
