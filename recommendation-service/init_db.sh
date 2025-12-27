#!/bin/bash

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h postgres -U postgres -d medusa-store -c '\q'; do
  >&2 echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is up - executing schema initialization"

# Drop old tables from public schema (migration from old structure)
echo "Cleaning up old tables from public schema..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h postgres -U postgres -d medusa-store <<EOF
DROP TABLE IF EXISTS public.rec_analytics CASCADE;
DROP TABLE IF EXISTS public.rec_frequently_together CASCADE;
DROP TABLE IF EXISTS public.rec_product_similarities CASCADE;
DROP TABLE IF EXISTS public.rec_recommendations_cache CASCADE;
DROP TABLE IF EXISTS public.rec_user_interactions CASCADE;
DROP TABLE IF EXISTS public.rec_user_preferences CASCADE;
DROP TABLE IF EXISTS public.rec_user_segments CASCADE;
EOF

# Execute schema initialization (creates recommendation schema and tables)
echo "Creating recommendation schema and tables..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h postgres -U postgres -d medusa-store -f /app/database/init_schema.sql

echo "Schema initialization completed"
