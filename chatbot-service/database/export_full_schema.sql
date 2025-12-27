-- =============================================
-- MEDUSA DB SCHEMA EXPORT - Full Details
-- Chạy TOÀN BỘ script này 1 lần trong pgAdmin
-- Kết quả sẽ hiện ở tab "Data Output"
-- =============================================

-- Output dạng JSON cho tất cả tables quan trọng
WITH table_info AS (
    SELECT 
        t.table_schema,
        t.table_name,
        json_agg(
            json_build_object(
                'column', c.column_name,
                'type', c.data_type,
                'max_length', c.character_maximum_length,
                'nullable', c.is_nullable,
                'default', c.column_default
            ) ORDER BY c.ordinal_position
        ) as columns
    FROM information_schema.tables t
    JOIN information_schema.columns c 
        ON t.table_name = c.table_name AND t.table_schema = c.table_schema
    WHERE t.table_schema IN ('public', 'chatbot')
        AND t.table_type = 'BASE TABLE'
        AND t.table_name IN (
            -- Medusa core tables
            'customer', 'product', 'product_variant', 'product_option',
            'product_option_value', 'product_category', 'product_collection',
            'order', 'order_item', 'cart', 'cart_line_item',
            'region', 'currency', 'store',
            -- Chatbot tables
            'sessions', 'messages', 'settings'
        )
    GROUP BY t.table_schema, t.table_name
),
pk_info AS (
    SELECT 
        tc.table_schema,
        tc.table_name,
        json_agg(kcu.column_name) as primary_keys
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu 
        ON tc.constraint_name = kcu.constraint_name
        AND tc.table_schema = kcu.table_schema
    WHERE tc.constraint_type = 'PRIMARY KEY'
        AND tc.table_schema IN ('public', 'chatbot')
    GROUP BY tc.table_schema, tc.table_name
),
fk_info AS (
    SELECT 
        tc.table_schema,
        tc.table_name,
        json_agg(
            json_build_object(
                'column', kcu.column_name,
                'references_table', ccu.table_name,
                'references_column', ccu.column_name
            )
        ) as foreign_keys
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu 
        ON tc.constraint_name = kcu.constraint_name
    JOIN information_schema.constraint_column_usage ccu 
        ON tc.constraint_name = ccu.constraint_name
    WHERE tc.constraint_type = 'FOREIGN KEY'
        AND tc.table_schema IN ('public', 'chatbot')
    GROUP BY tc.table_schema, tc.table_name
)
SELECT 
    json_build_object(
        'exported_at', NOW(),
        'tables', json_agg(
            json_build_object(
                'schema', ti.table_schema,
                'table', ti.table_name,
                'primary_keys', COALESCE(pk.primary_keys, '[]'::json),
                'foreign_keys', COALESCE(fk.foreign_keys, '[]'::json),
                'columns', ti.columns
            ) ORDER BY ti.table_schema, ti.table_name
        )
    ) as medusa_schema
FROM table_info ti
LEFT JOIN pk_info pk ON ti.table_schema = pk.table_schema AND ti.table_name = pk.table_name
LEFT JOIN fk_info fk ON ti.table_schema = fk.table_schema AND ti.table_name = fk.table_name;
