import asyncio
import asyncpg
import pandas as pd
import os

# Database Configuration
DB_CONFIG = {
    "user": "postgres",
    "password": "postgres",
    "database": "medusa-store",
    "host": "localhost",
    "port": 5432
}

async def export_data():
    print(f"Connecting to database {DB_CONFIG['database']} at {DB_CONFIG['host']}...")
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
    except Exception as e:
        print(f"Error connecting to database: {e}")
        print("Please ensure your database is running and accessible.")
        return

    print("Connection successful.")

    # 1. Export Products with Categories and Collections
    print("Fetching products...")
    # Note: Medusa products can have multiple categories, we'll take the first one for simplicity in this evaluation
    products_query = """
        SELECT 
            p.id,
            p.handle,
            p.title,
            p.status,
            pc.name as category,
            pcol.title as collection
        FROM product p
        LEFT JOIN product_category_product pcp ON p.id = pcp.product_id
        LEFT JOIN product_category pc ON pcp.product_category_id = pc.id
        LEFT JOIN product_collection pcol ON p.collection_id = pcol.id
        WHERE p.status = 'published' AND p.deleted_at IS NULL
    """
    
    products_rows = await conn.fetch(products_query)
    products_data = [dict(row) for row in products_rows]
    products_df = pd.DataFrame(products_data)
    
    # Deduplicate by handle (in case of multiple categories, just take one)
    products_df = products_df.drop_duplicates(subset=['handle'])
    
    print(f"Found {len(products_df)} products.")
    products_df.to_csv('products.csv', index=False)
    print("Saved to products.csv")

    # 2. Export Interactions
    print("Fetching interactions...")
    try:
        interactions_query = """
            SELECT 
                user_id,
                session_id,
                product_handle,
                interaction_type,
                timestamp
            FROM recommendation.rec_user_interactions
            ORDER BY timestamp DESC
        """
        interactions_rows = await conn.fetch(interactions_query)
        interactions_data = [dict(row) for row in interactions_rows]
        interactions_df = pd.DataFrame(interactions_data)
        
        print(f"Found {len(interactions_df)} interactions.")
        interactions_df.to_csv('interactions.csv', index=False)
        print("Saved to interactions.csv")
        
    except asyncpg.UndefinedTableError:
        print("Warning: Table 'recommendation.rec_user_interactions' not found.")
        print("Creating empty interactions.csv")
        pd.DataFrame(columns=['user_id', 'session_id', 'product_handle', 'interaction_type', 'timestamp']).to_csv('interactions.csv', index=False)

    await conn.close()
    print("Done.")

if __name__ == "__main__":
    # Install dependencies if needed: pip install asyncpg pandas
    loop = asyncio.get_event_loop()
    loop.run_until_complete(export_data())
