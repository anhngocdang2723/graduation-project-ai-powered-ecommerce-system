-- Kiểm tra API keys hiện có
SELECT * FROM public.api_key WHERE type = 'publishable';

-- Nếu không có, tạo mới
-- INSERT INTO public.api_key (id, token, salt, redacted, title, type, created_by, created_at, updated_at)
-- VALUES (
--   'apk_' || replace(gen_random_uuid()::text, '-', ''),
--   'pk_' || encode(gen_random_bytes(32), 'hex'),
--   encode(gen_random_bytes(16), 'hex'),
--   'pk_****',
--   'Storefront Key',
--   'publishable',
--   NULL,
--   NOW(),
--   NOW()
-- );
