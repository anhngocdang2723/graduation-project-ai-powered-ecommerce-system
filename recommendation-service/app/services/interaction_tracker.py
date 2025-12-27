import asyncpg
import uuid
from datetime import datetime
import json

class InteractionTracker:
    def __init__(self, db_pool):
        self.db_pool = db_pool
    
    async def track(self, user_id: str, session_id: str, product_id: str, 
                   product_handle: str, interaction_type: str, metadata: dict):
        """Track a user interaction"""
        interaction_id = f"int_{uuid.uuid4().hex}"
        
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO rec_user_interactions 
                (id, user_id, session_id, product_id, product_handle, interaction_type, metadata, timestamp)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """, interaction_id, user_id, session_id, product_id, product_handle, 
                interaction_type, json.dumps(metadata), datetime.now())
        
        if interaction_type in ['view', 'add_to_cart', 'purchase', 'wishlist']:
            await self.update_user_preferences(user_id)
        
        return interaction_id
    
    async def update_user_preferences(self, user_id: str):
        """Learn user preferences from their interactions"""
        async with self.db_pool.acquire() as conn:
            interactions = await conn.fetch("""
                SELECT product_handle, interaction_type, metadata, timestamp
                FROM rec_user_interactions
                WHERE user_id = $1
                AND timestamp > NOW() - INTERVAL '30 days'
                ORDER BY timestamp DESC
                LIMIT 100
            """, user_id)
            
            if not interactions:
                return
            
            category_scores = {}
            prices = []
            
            for interaction in interactions:
                metadata = interaction['metadata']
                if not metadata:
                    continue
                
                if isinstance(metadata, str):
                    try:
                        metadata = json.loads(metadata)
                    except:
                        continue
                
                weight = {
                    'purchase': 5.0,
                    'add_to_cart': 3.0,
                    'wishlist': 2.0,
                    'view': 1.0
                }.get(interaction['interaction_type'], 1.0)
                
                if 'category' in metadata:
                    category = metadata['category']
                    category_scores[category] = category_scores.get(category, 0) + weight
                
                if 'price' in metadata:
                    try:
                        price = float(metadata['price'])
                        prices.append(price)
                    except:
                        pass
            
            if category_scores:
                max_score = max(category_scores.values())
                category_scores = {k: v/max_score for k, v in category_scores.items()}
            
            price_min = min(prices) if prices else None
            price_max = max(prices) if prices else None
            
            await conn.execute("""
                INSERT INTO rec_user_preferences 
                (user_id, category_scores, price_min, price_max, last_updated)
                VALUES ($1, $2, $3, $4, NOW())
                ON CONFLICT (user_id) 
                DO UPDATE SET 
                    category_scores = $2,
                    price_min = $3,
                    price_max = $4,
                    last_updated = NOW()
            """, user_id, json.dumps(category_scores), price_min, price_max)
    
    async def update_all_user_preferences(self):
        """Update preferences for all active users"""
        async with self.db_pool.acquire() as conn:
            # Get users with recent activity
            users = await conn.fetch("""
                SELECT DISTINCT user_id 
                FROM rec_user_interactions
                WHERE timestamp > NOW() - INTERVAL '7 days'
            """)
            
            count = 0
            for user in users:
                await self.update_user_preferences(user['user_id'])
                count += 1
            
            return count
