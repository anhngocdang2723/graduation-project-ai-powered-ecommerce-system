-- Verify chatbot schema và tables
-- Chạy từng query một để kiểm tra

-- 1. Kiểm tra schema chatbot có tồn tại
SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'chatbot';

-- 2. Liệt kê tất cả tables trong schema chatbot
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'chatbot';

-- 3. Xem cấu trúc table sessions
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_schema = 'chatbot' AND table_name = 'sessions'
ORDER BY ordinal_position;

-- 4. Xem cấu trúc table messages
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_schema = 'chatbot' AND table_name = 'messages'
ORDER BY ordinal_position;

-- 5. Xem cấu trúc table settings
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_schema = 'chatbot' AND table_name = 'settings'
ORDER BY ordinal_position;

-- 6. Kiểm tra default settings đã insert chưa
SELECT * FROM chatbot.settings;

-- 7. Test insert một session (optional)
-- INSERT INTO chatbot.sessions (session_id, customer_email) 
-- VALUES ('test_session_001', 'test@example.com');
-- SELECT * FROM chatbot.sessions;
