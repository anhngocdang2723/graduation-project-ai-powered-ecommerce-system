import asyncio
import asyncpg
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/medusa-store")

async def list_tables():
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        rows = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_name LIKE '%stock%'
        """)
        print("Tables with 'stock':")
        for r in rows:
            print(r['table_name'])
            
        rows = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_name LIKE '%sales_channel%'
        """)
        print("\nTables with 'sales_channel':")
        for r in rows:
            print(r['table_name'])
            
        await conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(list_tables())
