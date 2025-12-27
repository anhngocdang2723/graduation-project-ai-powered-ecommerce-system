-- Sample data for Collaborative Filtering
-- Insert sample user interactions to demonstrate collaborative filtering recommendations

SET search_path TO recommendation, public;

-- Sample users and their interaction patterns
-- User 1: Interested in backpacks
INSERT INTO recommendation.rec_user_interactions (id, user_id, session_id, product_id, product_handle, interaction_type, timestamp, metadata)
VALUES 
    (gen_random_uuid()::text, 'sample_user_1', 'session_001', NULL, 'unisex-adult-nike-heritage-backpack-b0992x6s9w', 'view', NOW() - INTERVAL '5 days', '{}'),
    (gen_random_uuid()::text, 'sample_user_1', 'session_001', NULL, 'unisex-adult-nike-heritage-backpack-b0992x6s9w', 'add_to_cart', NOW() - INTERVAL '5 days', '{}'),
    (gen_random_uuid()::text, 'sample_user_1', 'session_001', NULL, 'unisex-adult-nike-heritage-backpack-b0992x6s9w', 'purchase', NOW() - INTERVAL '5 days', '{"order_id": "sample_order_1"}'),
    (gen_random_uuid()::text, 'sample_user_1', 'session_002', NULL, 'unisex-classic-3-stripes-backpack-backpack-b09n2pjxrz', 'view', NOW() - INTERVAL '4 days', '{}'),
    (gen_random_uuid()::text, 'sample_user_1', 'session_002', NULL, 'unisex-classic-3-stripes-backpack-backpack-b09n2pjxrz', 'wishlist', NOW() - INTERVAL '4 days', '{}'),
    (gen_random_uuid()::text, 'sample_user_1', 'session_003', NULL, 'laptop-backpack-for-men-women-water-resistant-travel-bag-with-usb-charging-port-anti-theft-business-computer-daypack-for-work-and-college-b074kv9tt4', 'view', NOW() - INTERVAL '3 days', '{}')
ON CONFLICT (id) DO NOTHING;

-- User 2: Similar taste to User 1 (backpacks)
INSERT INTO recommendation.rec_user_interactions (id, user_id, session_id, product_id, product_handle, interaction_type, timestamp, metadata)
VALUES 
    (gen_random_uuid()::text, 'sample_user_2', 'session_004', NULL, 'unisex-adult-nike-heritage-backpack-b0992x6s9w', 'view', NOW() - INTERVAL '6 days', '{}'),
    (gen_random_uuid()::text, 'sample_user_2', 'session_004', NULL, 'unisex-adult-nike-heritage-backpack-b0992x6s9w', 'add_to_cart', NOW() - INTERVAL '6 days', '{}'),
    (gen_random_uuid()::text, 'sample_user_2', 'session_005', NULL, 'laptop-backpack-for-men-women-water-resistant-travel-bag-with-usb-charging-port-anti-theft-business-computer-daypack-for-work-and-college-b074kv9tt4', 'view', NOW() - INTERVAL '5 days', '{}'),
    (gen_random_uuid()::text, 'sample_user_2', 'session_005', NULL, 'laptop-backpack-for-men-women-water-resistant-travel-bag-with-usb-charging-port-anti-theft-business-computer-daypack-for-work-and-college-b074kv9tt4', 'purchase', NOW() - INTERVAL '5 days', '{"order_id": "sample_order_2"}'),
    (gen_random_uuid()::text, 'sample_user_2', 'session_006', NULL, 'unisex-classic-3-stripes-backpack-backpack-b09n2pjxrz', 'view', NOW() - INTERVAL '4 days', '{}')
ON CONFLICT (id) DO NOTHING;

-- User 3: Interested in t-shirts and casual wear
INSERT INTO recommendation.rec_user_interactions (id, user_id, session_id, product_id, product_handle, interaction_type, timestamp, metadata)
VALUES 
    (gen_random_uuid()::text, 'sample_user_3', 'session_008', NULL, 'men-s-solid-regular-fit-sleeveless-sports-t-shirt-b093gz65k9', 'view', NOW() - INTERVAL '7 days', '{}'),
    (gen_random_uuid()::text, 'sample_user_3', 'session_008', NULL, 'men-s-solid-regular-fit-sleeveless-sports-t-shirt-b093gz65k9', 'purchase', NOW() - INTERVAL '7 days', '{"order_id": "sample_order_3"}'),
    (gen_random_uuid()::text, 'sample_user_3', 'session_009', NULL, 'men-solid-regular-fit-t-shirt-ss20symtee22-b09797wmz8', 'view', NOW() - INTERVAL '6 days', '{}'),
    (gen_random_uuid()::text, 'sample_user_3', 'session_009', NULL, 'men-solid-regular-fit-t-shirt-ss20symtee22-b09797wmz8', 'add_to_cart', NOW() - INTERVAL '5 days', '{}'),
    (gen_random_uuid()::text, 'sample_user_3', 'session_010', NULL, 'men-s-regular-polo-shirt-aw17mpcp11-b073x2spfg', 'view', NOW() - INTERVAL '4 days', '{}'),
    (gen_random_uuid()::text, 'sample_user_3', 'session_010', NULL, 'men-s-regular-polo-shirt-aw17mpcp11-b073x2spfg', 'wishlist', NOW() - INTERVAL '3 days', '{}')
ON CONFLICT (id) DO NOTHING;

-- User 4: Similar to User 3 (casual wear lover)
INSERT INTO recommendation.rec_user_interactions (id, user_id, session_id, product_id, product_handle, interaction_type, timestamp, metadata)
VALUES 
    (gen_random_uuid()::text, 'sample_user_4', 'session_011', NULL, 'men-s-solid-regular-fit-sleeveless-sports-t-shirt-b093gz65k9', 'view', NOW() - INTERVAL '8 days', '{}'),
    (gen_random_uuid()::text, 'sample_user_4', 'session_011', NULL, 'men-s-solid-regular-fit-sleeveless-sports-t-shirt-b093gz65k9', 'add_to_cart', NOW() - INTERVAL '8 days', '{}'),
    (gen_random_uuid()::text, 'sample_user_4', 'session_012', NULL, 'men-s-regular-polo-shirt-aw17mpcp11-b073x2spfg', 'view', NOW() - INTERVAL '7 days', '{}'),
    (gen_random_uuid()::text, 'sample_user_4', 'session_012', NULL, 'men-s-regular-polo-shirt-aw17mpcp11-b073x2spfg', 'purchase', NOW() - INTERVAL '7 days', '{"order_id": "sample_order_4"}'),
    (gen_random_uuid()::text, 'sample_user_4', 'session_013', NULL, 'men-solid-regular-fit-t-shirt-ss20symtee22-b09797wmz8', 'view', NOW() - INTERVAL '5 days', '{}')
ON CONFLICT (id) DO NOTHING;

-- User 5: Interested in Tote Bags
INSERT INTO recommendation.rec_user_interactions (id, user_id, session_id, product_id, product_handle, interaction_type, timestamp, metadata)
VALUES 
    (gen_random_uuid()::text, 'sample_user_5', 'session_014', NULL, 'women-s-hana-medium-tote-bag-b0d7gt9ktn', 'view', NOW() - INTERVAL '3 days', '{}'),
    (gen_random_uuid()::text, 'sample_user_5', 'session_014', NULL, 'women-s-hana-medium-tote-bag-b0d7gt9ktn', 'wishlist', NOW() - INTERVAL '3 days', '{}'),
    (gen_random_uuid()::text, 'sample_user_5', 'session_014', NULL, 'women-s-hana-medium-tote-bag-b0d7gt9ktn', 'purchase', NOW() - INTERVAL '2 days', '{"order_id": "sample_order_5"}'),
    (gen_random_uuid()::text, 'sample_user_5', 'session_015', NULL, 'women-s-hana-mini-tote-bag-b0d46zdljb', 'view', NOW() - INTERVAL '1 days', '{}')
ON CONFLICT (id) DO NOTHING;
