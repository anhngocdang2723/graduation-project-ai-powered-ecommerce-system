-- =============================================
-- CHATBOT DATABASE SCHEMA
-- Run this script in pgAdmin to create tables
-- Compatible with Medusa v2 database structure
-- =============================================

-- Create schema for chatbot (isolated from Medusa tables)
CREATE SCHEMA IF NOT EXISTS chatbot;

-- =============================================
-- 1. Chat Sessions - Lưu phiên chat
-- Links to public.customer (Medusa's customer table)
-- =============================================
CREATE TABLE IF NOT EXISTS chatbot.sessions (
    id VARCHAR(255) PRIMARY KEY DEFAULT 'chat_' || replace(gen_random_uuid()::text, '-', ''),
    session_id VARCHAR(100) NOT NULL UNIQUE,
    -- Link to Medusa customer (nullable for guest users)
    customer_id VARCHAR(255) REFERENCES public.customer(id) ON DELETE SET NULL,
    customer_email VARCHAR(255),
    customer_name VARCHAR(255),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'active',  -- active, ended, escalated
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================
-- 2. Chat Messages - Lưu tin nhắn
-- =============================================
CREATE TABLE IF NOT EXISTS chatbot.messages (
    id VARCHAR(255) PRIMARY KEY DEFAULT 'msg_' || replace(gen_random_uuid()::text, '-', ''),
    session_id VARCHAR(100) NOT NULL REFERENCES chatbot.sessions(session_id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,  -- user, assistant, system
    content TEXT NOT NULL,
    intent VARCHAR(50),  -- product_inquiry, order_tracking, create_order, general
    tokens_used INTEGER DEFAULT 0,
    response_time_ms INTEGER,  -- Thời gian phản hồi (ms)
    metadata JSONB DEFAULT '{}'::jsonb,  -- Lưu products, actions, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================
-- 3. Chatbot Settings - Cấu hình chatbot (Admin)
-- =============================================
CREATE TABLE IF NOT EXISTS chatbot.settings (
    id VARCHAR(255) PRIMARY KEY DEFAULT 'setting_' || replace(gen_random_uuid()::text, '-', ''),
    key VARCHAR(100) NOT NULL UNIQUE,
    value JSONB NOT NULL,
    description TEXT,
    updated_by VARCHAR(255),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default settings
INSERT INTO chatbot.settings (key, value, description) VALUES
    ('enabled', 'true', 'Enable/disable chatbot'),
    ('model', '"qwen-max"', 'AI model to use'),
    ('welcome_message', '"Xin chào! Tôi là trợ lý AI. Tôi có thể giúp gì cho bạn?"', 'Welcome message'),
    ('max_tokens', '2000', 'Maximum tokens per response')
ON CONFLICT (key) DO NOTHING;

-- =============================================
-- INDEXES for better query performance
-- =============================================
CREATE INDEX IF NOT EXISTS idx_chatbot_sessions_customer ON chatbot.sessions(customer_id);
CREATE INDEX IF NOT EXISTS idx_chatbot_sessions_status ON chatbot.sessions(status);
CREATE INDEX IF NOT EXISTS idx_chatbot_sessions_created ON chatbot.sessions(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_chatbot_messages_session ON chatbot.messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chatbot_messages_created ON chatbot.messages(created_at DESC);

-- =============================================
-- VIEW: Recent sessions for Admin Dashboard
-- =============================================
CREATE OR REPLACE VIEW chatbot.v_recent_sessions AS
SELECT 
    s.id,
    s.session_id,
    s.customer_id,
    s.customer_email,
    s.customer_name,
    s.status,
    s.started_at,
    COUNT(m.id) as message_count,
    MAX(m.created_at) as last_message_at
FROM chatbot.sessions s
LEFT JOIN chatbot.messages m ON s.session_id = m.session_id
GROUP BY s.id
ORDER BY s.started_at DESC;

-- =============================================
-- DONE! Run this in pgAdmin Query Tool
-- =============================================
