-- Add VND prices for all variants that don't have them
-- Exchange rate: 1 USD = 25,000 VND

-- Step 1: Find VND region
-- VietNam Region (reg_01KCC5AB82341JR41RZEE5F16Q)

-- Step 2: Insert VND prices for variants that have USD/EUR prices but no VND price
-- This uses the first available price (USD or EUR) and converts to VND

WITH base_prices AS (
  SELECT DISTINCT
    price_set_id,
    MIN(amount) as base_amount,
    MIN(currency_code) as base_currency
  FROM price
  WHERE currency_code IN ('usd', 'eur')
  GROUP BY price_set_id
),
price_sets_needing_vnd AS (
  SELECT bp.*
  FROM base_prices bp
  WHERE NOT EXISTS (
    SELECT 1 FROM price p
    WHERE p.price_set_id = bp.price_set_id
    AND p.currency_code = 'vnd'
  )
)
INSERT INTO price (
  price_set_id,
  currency_code,
  amount,
  min_quantity,
  max_quantity,
  created_at,
  updated_at
)
SELECT
  price_set_id,
  'vnd' as currency_code,
  -- Convert based on currency
  -- Assume USD cents → multiply by 25000 (USD to VND rate)
  -- For EUR, use similar rate (can adjust)
  CASE 
    WHEN base_currency = 'usd' THEN (base_amount::numeric / 100 * 25000 * 100)::bigint
    WHEN base_currency = 'eur' THEN (base_amount::numeric / 100 * 25000 * 100)::bigint
    ELSE base_amount
  END as amount,
  NULL as min_quantity,
  NULL as max_quantity,
  NOW() as created_at,
  NOW() as updated_at
FROM price_sets_needing_vnd;

-- Now link to region
WITH vnd_region AS (
  SELECT id FROM region WHERE currency_code = 'vnd' LIMIT 1
),
new_vnd_prices AS (
  SELECT id, price_set_id
  FROM price
  WHERE currency_code = 'vnd'
  AND created_at >= NOW() - INTERVAL '1 minute' -- Just created
)
INSERT INTO price_rule (
  price_id,
  attribute,
  value,
  priority,
  created_at,
  updated_at
)
SELECT
  np.id as price_id,
  'region_id' as attribute,
  vr.id as value,
  0 as priority,
  NOW() as created_at,
  NOW() as updated_at
FROM new_vnd_prices np
CROSS JOIN vnd_region vr
WHERE NOT EXISTS (
  SELECT 1 FROM price_rule pr
  WHERE pr.price_id = np.id
  AND pr.attribute = 'region_id'
);

-- Show result
SELECT 
  p.id,
  pv.title as variant_title,
  p.currency_code,
  p.amount,
  ROUND(p.amount::numeric / 100, 2) as display_price
FROM price p
JOIN price_set_variant_link pvl ON p.price_set_id = pvl.price_set_id
JOIN product_variant pv ON pvl.variant_id = pv.id
WHERE p.currency_code = 'vnd'
ORDER BY p.created_at DESC
LIMIT 20;
