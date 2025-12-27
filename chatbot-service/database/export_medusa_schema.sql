-- ==============================================
-- SCRIPT: Export Medusa DB Schema to JSON-like format
-- Run này trong pgAdmin để xem cấu trúc các bảng chính
-- ==============================================

-- 1. Liệt kê tất cả tables trong public schema
SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns c WHERE c.table_name = t.table_name AND c.table_schema = 'public') as column_count
FROM information_schema.tables t
WHERE table_schema = 'public' 
AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- 2. Chi tiết các bảng QUAN TRỌNG cho Chatbot

-- === CUSTOMER (khách hàng) ===
SELECT 
    column_name, 
    data_type, 
    character_maximum_length,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'public' AND table_name = 'customer'
ORDER BY ordinal_position;

-- === PRODUCT (sản phẩm) ===
SELECT 
    column_name, 
    data_type, 
    character_maximum_length,
    is_nullable
FROM information_schema.columns 
WHERE table_schema = 'public' AND table_name = 'product'
ORDER BY ordinal_position;

-- === PRODUCT_VARIANT (biến thể sản phẩm - chứa giá) ===
SELECT 
    column_name, 
    data_type, 
    character_maximum_length,
    is_nullable
FROM information_schema.columns 
WHERE table_schema = 'public' AND table_name = 'product_variant'
ORDER BY ordinal_position;

-- === ORDER (đơn hàng) ===
SELECT 
    column_name, 
    data_type, 
    character_maximum_length,
    is_nullable
FROM information_schema.columns 
WHERE table_schema = 'public' AND table_name = 'order'
ORDER BY ordinal_position;

-- === CART (giỏ hàng) ===
SELECT 
    column_name, 
    data_type, 
    character_maximum_length,
    is_nullable
FROM information_schema.columns 
WHERE table_schema = 'public' AND table_name = 'cart'
ORDER BY ordinal_position;

-- 3. Export schema dạng JSON-friendly (chạy riêng từng cái)
SELECT json_agg(
    json_build_object(
        'column', column_name,
        'type', data_type,
        'max_length', character_maximum_length,
        'nullable', is_nullable
    )
) as customer_schema
FROM information_schema.columns 
WHERE table_schema = 'public' AND table_name = 'customer';

-- 4. Xem sample data (5 rows)
-- SELECT * FROM public.customer LIMIT 5;
-- SELECT * FROM public.product LIMIT 5;
-- SELECT * FROM public."order" LIMIT 5;

-- 5. Kiểm tra xem chatbot schema đã tồn tại chưa
SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'chatbot';
