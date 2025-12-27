-- Kiểm tra API key và Sales Channel
-- 1. Xem API keys
SELECT id, token, title, type FROM public.api_key WHERE type = 'publishable';

-- 2. Xem Sales Channels
SELECT id, name, is_disabled FROM public.sales_channel;

-- 3. Xem link giữa API key và Sales Channel
SELECT * FROM public.api_key_sales_channel;

-- 4. Nếu chưa có link, tạo link (thay YOUR_API_KEY_ID và YOUR_SALES_CHANNEL_ID)
-- INSERT INTO public.api_key_sales_channel (api_key_id, sales_channel_id, created_at, updated_at)
-- SELECT 
--     (SELECT id FROM public.api_key WHERE type = 'publishable' LIMIT 1),
--     (SELECT id FROM public.sales_channel WHERE is_disabled = false LIMIT 1),
--     NOW(),
--     NOW()
-- WHERE NOT EXISTS (
--     SELECT 1 FROM public.api_key_sales_channel
-- );
