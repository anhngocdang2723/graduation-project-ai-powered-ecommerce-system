import asyncpg
import json
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
import numpy as np
from collections import defaultdict, Counter
import random

from app.config import get_settings
from app.logging_config import get_rec_logger, log_algorithm_selection

settings = get_settings()
logger = get_rec_logger("engine")

def format_price(amount: float, currency_code: str) -> str:
    """Format price with proper currency symbol and formatting"""
    currency_upper = currency_code.upper()
    
    if currency_upper == "VND":
        return f"{int(amount):,}₫"
    elif currency_upper == "USD":
        return f"${amount:,.2f}"
    elif currency_upper == "EUR":
        return f"€{amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency_upper}"

class RecommendationEngine:
    def __init__(self, db_pool):
        self.db_pool = db_pool
    
    async def get_personalized_recommendations(self, user_id: str, limit: int = 12) -> Tuple[List[dict], str]:
        """Get personalized recommendations for user (hybrid approach)"""
        
        logger.info(f"Getting personalized recommendations - user={user_id} limit={limit}")
        
        user_stats = await self._get_user_interaction_stats(user_id)
        prefs = await self._get_user_preferences(user_id)
        recent_products = await self._get_user_recent_products(user_id, limit=10)
        
        if user_stats['total_interactions'] > 0:
            log_algorithm_selection(
                logger, user_id, "interaction_based",
                f"User has {user_stats['total_interactions']} interactions",
                user_stats
            )
            return await self._get_interaction_based_recommendations(user_id, user_stats, prefs, recent_products, limit)
        
        log_algorithm_selection(logger, user_id, "trending_fallback", "No user interactions found")
        trending = await self._get_trending_products(limit)
        if trending:
            return trending, "trending"
        return await self._get_random_products(limit), "random"
        
        # Hybrid recommendation
        recommendations = []
        
        # 1. Content-based: Based on user preferences
        if prefs and prefs.get('category_scores'):
            content_recs = await self._get_content_based_recommendations(prefs, limit=limit//2)
            recommendations.extend(content_recs)
        
        # 2. Collaborative: Similar users' purchases
        collab_recs = await self._get_collaborative_recommendations(user_id, limit=limit//2)
        recommendations.extend(collab_recs)
        
        # 3. Similar to recently viewed
        if recent_products:
            for product_handle in recent_products[:3]:
                similar = await self._get_similar_products_by_handle(product_handle, limit=2)
                recommendations.extend(similar)
        
        # Remove duplicates, keep order
        seen = set()
        unique_recs = []
        for rec in recommendations:
            if rec['handle'] not in seen:
                seen.add(rec['handle'])
                unique_recs.append(rec)
        
        # If still not enough, add random popular products
        if len(unique_recs) < limit:
            random_products = await self._get_random_products(limit - len(unique_recs))
            for product in random_products:
                if product['handle'] not in seen:
                    unique_recs.append(product)
                    seen.add(product['handle'])
        
        # DEMO MODE: Shuffle to show different products on each refresh
        random.shuffle(unique_recs)
        
        return unique_recs[:limit], "hybrid"
    
    async def _get_user_interaction_stats(self, user_id: str) -> dict:
        """Get user interaction statistics"""
        async with self.db_pool.acquire() as conn:
            stats = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_interactions,
                    COUNT(DISTINCT product_handle) as unique_products_viewed,
                    SUM(CASE WHEN interaction_type = 'view' THEN 1 ELSE 0 END) as views,
                    SUM(CASE WHEN interaction_type = 'add_to_cart' THEN 1 ELSE 0 END) as cart_adds,
                    SUM(CASE WHEN interaction_type = 'wishlist' THEN 1 ELSE 0 END) as wishlist_adds,
                    SUM(CASE WHEN interaction_type = 'purchase' THEN 1 ELSE 0 END) as purchases
                FROM recommendation.rec_user_interactions
                WHERE user_id = $1
            """, user_id)
            
            result = dict(stats) if stats else {
                'total_interactions': 0, 'unique_products_viewed': 0,
                'views': 0, 'cart_adds': 0, 'wishlist_adds': 0, 'purchases': 0
            }
            logger.debug(f"User interaction stats - user={user_id} stats={result}")
            return result
    
    async def _get_interaction_based_recommendations(self, user_id: str, stats: dict, prefs: dict, recent_products: List[str], limit: int) -> Tuple[List[dict], str]:
        """Generate recommendations based on user interactions"""
        recommendations = []
        
        # Strategy 1: Similar to products in cart/wishlist (highest priority)
        if stats['cart_adds'] > 0 or stats['wishlist_adds'] > 0:
            cart_wishlist_recs = await self._get_similar_to_cart_wishlist(user_id, limit=limit//3)
            recommendations.extend(cart_wishlist_recs)
            logger.info(f"Added similar to cart/wishlist - count={len(cart_wishlist_recs)}")
        
        # Strategy 2: Category-based on viewed products
        if stats['views'] > 0:
            category_recs = await self._get_category_based_on_views(user_id, limit=limit//3)
            recommendations.extend(category_recs)
            logger.info(f"Added category-based recommendations - count={len(category_recs)}")
        
        # Strategy 3: Collaborative filtering (users with similar interactions)
        if stats['unique_products_viewed'] >= 3:
            collab_recs = await self._get_collaborative_recommendations(user_id, limit=limit//3)
            recommendations.extend(collab_recs)
            logger.info(f"Added collaborative recommendations - count={len(collab_recs)}")
        
        # Strategy 4: Similar to most viewed products
        if recent_products and len(recent_products) > 0:
            for product_handle in recent_products[:3]:
                similar = await self._get_similar_products_by_handle(product_handle, limit=2)
                recommendations.extend(similar)
            logger.info(f"Added similar to recent products - count={len(recent_products)}")
        
        seen = set()
        unique_recs = []
        for rec in recommendations:
            if rec['handle'] not in seen:
                seen.add(rec['handle'])
                unique_recs.append(rec)
        
        if len(unique_recs) < limit:
            trending = await self._get_trending_products(limit - len(unique_recs))
            for product in trending:
                if product['handle'] not in seen:
                    unique_recs.append(product)
                    seen.add(product['handle'])
        
        random.shuffle(unique_recs)
        
        algorithm = f"personalized({stats['total_interactions']} interactions)"
        return unique_recs[:limit], algorithm
    
    async def get_similar_products(self, product_handle: str, limit: int = 12) -> Tuple[List[dict], str]:
        """Get products similar to given product"""
        
        similar = await self._get_precomputed_similar(product_handle, limit)
        
        if similar:
            return similar, "pre-computed"
        similar = await self._get_similar_by_category(product_handle, limit)
        return similar, "content-based"
    
    async def get_frequently_bought_together(self, user_id: str, limit: int = 6) -> Tuple[List[dict], str]:
        """Get products frequently bought together with cart items"""
        
        # Get user's cart items (from recent add_to_cart interactions)
        async with self.db_pool.acquire() as conn:
            cart_items = await conn.fetch("""
                SELECT DISTINCT product_handle
                FROM rec_user_interactions
                WHERE user_id = $1
                AND interaction_type = 'add_to_cart'
                AND timestamp > NOW() - INTERVAL '7 days'
                ORDER BY product_handle
                LIMIT 5
            """, user_id)
        
        if not cart_items:
            return [], "none"
        
        # Get frequently bought together items
        recommendations = []
        async with self.db_pool.acquire() as conn:
            for item in cart_items:
                fbt = await conn.fetch("""
                    SELECT product_id_2, confidence_score
                    FROM rec_frequently_together
                    WHERE product_id_1 = $1
                    ORDER BY confidence_score DESC
                    LIMIT 3
                """, item['product_handle'])
                
                for row in fbt:
                    recommendations.append({
                        'handle': row['product_id_2'],
                        'score': float(row['confidence_score'])
                    })
        
        # Get product details
        if recommendations:
            handles = [r['handle'] for r in recommendations[:limit]]
            products = await self._get_products_by_handles(handles)
            return products, "frequently_bought_together"
        
        return [], "none"
    
    async def compute_all_similarities(self) -> int:
        """Compute product similarities (run as batch job)"""
        
        # Get all products from Medusa using product_category and product_collection
        async with self.db_pool.acquire() as conn:
            products = await conn.fetch("""
                SELECT DISTINCT
                    p.id,
                    p.handle,
                    p.title,
                    p.description,
                    COALESCE(pc.name, pcol.title, 'uncategorized') as category,
                    pv.calculated_price_id
                FROM product p
                LEFT JOIN product_category_product pcp ON p.id = pcp.product_id
                LEFT JOIN product_category pc ON pcp.product_category_id = pc.id
                LEFT JOIN product_collection pcol ON p.collection_id = pcol.id
                LEFT JOIN product_variant pv ON p.id = pv.product_id
                WHERE p.status = 'published'
                AND p.deleted_at IS NULL
                LIMIT 1000
            """)
        
        count = 0
        
        for i, prod1 in enumerate(products):
            for prod2 in products[i+1:]:
                similarity = self._compute_content_similarity(prod1, prod2)
                
                if similarity > 0.3:
                    await self._store_similarity(
                        prod1['handle'],
                        prod2['handle'],
                        similarity,
                        'content'
                    )
                    count += 1
        
        return count
    
    def _compute_content_similarity(self, prod1: dict, prod2: dict) -> float:
        """Compute similarity between two products"""
        score = 0.0
        
        if prod1.get('category') == prod2.get('category') and prod1.get('category'):
            score += 0.6
        
        if prod1.get('title') and prod2.get('title'):
            words1 = set(prod1['title'].lower().split())
            words2 = set(prod2['title'].lower().split())
            overlap = len(words1 & words2) / max(len(words1 | words2), 1)
            score += overlap * 0.4
        
        return min(score, 1.0)
    
    async def _store_similarity(self, handle1: str, handle2: str, score: float, sim_type: str):
        """Store product similarity"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO rec_product_similarities 
                (product_id_1, product_id_2, similarity_score, similarity_type, updated_at)
                VALUES ($1, $2, $3, $4, NOW())
                ON CONFLICT (product_id_1, product_id_2, similarity_type)
                DO UPDATE SET similarity_score = $3, updated_at = NOW()
            """, handle1, handle2, score, sim_type)
    
    async def _get_user_preferences(self, user_id: str) -> dict:
        """Get user preferences"""
        async with self.db_pool.acquire() as conn:
            prefs = await conn.fetchrow(
                "SELECT * FROM rec_user_preferences WHERE user_id = $1",
                user_id
            )
            
            if not prefs:
                return {}
            
            return {
                'category_scores': prefs['category_scores'],
                'price_min': float(prefs['price_min']) if prefs['price_min'] else None,
                'price_max': float(prefs['price_max']) if prefs['price_max'] else None
            }
    
    async def _get_user_recent_products(self, user_id: str, limit: int = 10) -> List[str]:
        """Get user's recently viewed/interacted products"""
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT DISTINCT ON (product_handle) product_handle, timestamp
                FROM rec_user_interactions
                WHERE user_id = $1
                AND product_handle IS NOT NULL
                ORDER BY product_handle, timestamp DESC
                LIMIT $2
            """, user_id, limit)
            
            return [row['product_handle'] for row in rows]
    
    async def _get_content_based_recommendations(self, prefs: dict, limit: int) -> List[dict]:
        """Get recommendations based on user preferences using product_category and product_collection"""
        category_scores = prefs.get('category_scores', {})
        
        if isinstance(category_scores, str):
            try:
                category_scores = json.loads(category_scores)
            except:
                category_scores = {}
        
        if not category_scores:
            return []
        
        top_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        
        recommendations = []
        async with self.db_pool.acquire() as conn:
            for category_name, score in top_categories:
                # Try to find products by product_category first
                products = await conn.fetch("""
                    WITH product_vnd_price AS (
                        SELECT DISTINCT
                            p.id,
                            p.handle,
                            p.title,
                            p.thumbnail,
                            pc.name as category,
                            pr.amount,
                            pr.currency_code,
                            ROW_NUMBER() OVER (PARTITION BY p.id ORDER BY 
                                CASE WHEN pr.currency_code = 'vnd' THEN 1 
                                     WHEN pr.currency_code = 'usd' THEN 2 
                                     ELSE 3 END
                            ) as rn
                        FROM product p
                        LEFT JOIN product_category_product pcp ON p.id = pcp.product_id
                        LEFT JOIN product_category pc ON pcp.product_category_id = pc.id
                        LEFT JOIN product_variant pv ON p.id = pv.product_id
                        LEFT JOIN product_variant_price_set pvps ON pv.id = pvps.variant_id
                        LEFT JOIN price pr ON pvps.price_set_id = pr.price_set_id
                        WHERE pc.name ILIKE $1
                        AND p.status = 'published'
                        AND p.deleted_at IS NULL
                    )
                    SELECT id, handle, title, thumbnail, category, amount, currency_code
                    FROM product_vnd_price
                    WHERE rn = 1
                    ORDER BY RANDOM()
                    LIMIT 2
                """, f"%{category_name}%")
                
                # If no products found in categories, try collections
                if not products:
                    products = await conn.fetch("""
                        WITH product_vnd_price AS (
                            SELECT 
                                p.id,
                                p.handle,
                                p.title,
                                p.thumbnail,
                                pcol.title as category,
                                pr.amount,
                                pr.currency_code,
                                ROW_NUMBER() OVER (PARTITION BY p.id ORDER BY 
                                    CASE WHEN pr.currency_code = 'vnd' THEN 1 
                                         WHEN pr.currency_code = 'usd' THEN 2 
                                         ELSE 3 END
                                ) as rn
                            FROM product p
                            LEFT JOIN product_collection pcol ON p.collection_id = pcol.id
                            LEFT JOIN product_variant pv ON p.id = pv.product_id
                            LEFT JOIN product_variant_price_set pvps ON pv.id = pvps.variant_id
                            LEFT JOIN price pr ON pvps.price_set_id = pr.price_set_id
                            WHERE pcol.title ILIKE $1
                            AND p.status = 'published'
                            AND p.deleted_at IS NULL
                        )
                        SELECT id, handle, title, thumbnail, category, amount, currency_code
                        FROM product_vnd_price
                        WHERE rn = 1
                        ORDER BY RANDOM()
                        LIMIT 2
                    """, f"%{category_name}%")
                
                for p in products:
                    rec = {
                        'id': p['id'],
                        'handle': p['handle'],
                        'title': p['title'],
                        'thumbnail': p['thumbnail'],
                        'score': score
                    }
                    
                    if p['amount'] and p['currency_code']:
                        rec['price'] = {
                            'amount': format_price(p['amount'], p['currency_code']),
                            'currencyCode': p['currency_code'].upper()
                        }
                    
                    recommendations.append(rec)
        
        return recommendations[:limit]
    
    async def _get_collaborative_recommendations(self, user_id: str, limit: int) -> List[dict]:
        """Get recommendations based on similar users"""
        
        # Find similar users (users who interacted with same products)
        async with self.db_pool.acquire() as conn:
            similar_users = await conn.fetch("""
                WITH user_products AS (
                    SELECT DISTINCT product_handle
                    FROM rec_user_interactions
                    WHERE user_id = $1
                    AND product_handle IS NOT NULL
                    LIMIT 20
                ),
                similar_users AS (
                    SELECT ui.user_id, COUNT(*) as overlap
                    FROM rec_user_interactions ui
                    INNER JOIN user_products up ON ui.product_handle = up.product_handle
                    WHERE ui.user_id != $1
                    GROUP BY ui.user_id
                    HAVING COUNT(*) >= 2
                    ORDER BY overlap DESC
                    LIMIT 10
                )
                SELECT DISTINCT ui.product_handle
                FROM rec_user_interactions ui
                INNER JOIN similar_users su ON ui.user_id = su.user_id
                WHERE ui.interaction_type IN ('purchase', 'add_to_cart')
                AND ui.product_handle NOT IN (SELECT product_handle FROM user_products)
                AND ui.product_handle IS NOT NULL
                ORDER BY ui.product_handle
                LIMIT $2
            """, user_id, limit)
            
            handles = [row['product_handle'] for row in similar_users]
            
            if not handles:
                return []
            
            return await self._get_products_by_handles(handles)
    
    async def _get_trending_products(self, limit: int) -> List[dict]:
        """Get trending products (most viewed recently)"""
        return await self.get_most_viewed_products(limit)

    async def get_most_viewed_products(self, user_id: str, limit: int) -> List[dict]:
        """Get most viewed products from personalized recommendations"""
        # 1. Get a larger pool of personalized recommendations
        candidates, _ = await self.get_personalized_recommendations(user_id, limit=50)
        
        if not candidates:
            return []
            
        candidate_handles = [p['handle'] for p in candidates]
        
        # 2. Sort candidates by view count
        async with self.db_pool.acquire() as conn:
            # Get view counts for these candidates
            stats = await conn.fetch("""
                SELECT product_handle, COUNT(*) as views
                FROM rec_user_interactions
                WHERE interaction_type = 'view'
                AND product_handle = ANY($1::text[])
                GROUP BY product_handle
            """, candidate_handles)
            
            # Create a map of handle -> views
            view_map = {row['product_handle']: row['views'] for row in stats}
            
            # Sort candidates by views (descending)
            candidates.sort(key=lambda x: view_map.get(x['handle'], 0), reverse=True)
            
            return candidates[:limit]

    async def get_personalized_top_selling(self, user_id: str, limit: int) -> List[dict]:
        """Get top selling products from personalized recommendations"""
        # 1. Get a larger pool of personalized recommendations
        candidates, _ = await self.get_personalized_recommendations(user_id, limit=50)
        
        if not candidates:
            return []
            
        candidate_handles = [p['handle'] for p in candidates]
        
        # 2. Sort candidates by purchase count
        async with self.db_pool.acquire() as conn:
            # Get purchase counts for these candidates
            stats = await conn.fetch("""
                SELECT product_handle, COUNT(*) as purchases
                FROM rec_user_interactions
                WHERE interaction_type = 'purchase'
                AND product_handle = ANY($1::text[])
                GROUP BY product_handle
            """, candidate_handles)
            
            purchase_map = {row['product_handle']: row['purchases'] for row in stats}
            candidates.sort(key=lambda x: purchase_map.get(x['handle'], 0), reverse=True)
            
            return candidates[:limit]

    async def get_personalized_most_viewed(self, user_id: str, limit: int) -> List[dict]:
        """Get most viewed products from personalized recommendations"""
        # 1. Get a larger pool of personalized recommendations
        candidates, _ = await self.get_personalized_recommendations(user_id, limit=50)
        
        if not candidates:
            return []
            
        candidate_handles = [p['handle'] for p in candidates]
        
        # 2. Sort candidates by view count
        async with self.db_pool.acquire() as conn:
            # Get view counts for these candidates
            stats = await conn.fetch("""
                SELECT product_handle, COUNT(*) as views
                FROM rec_user_interactions
                WHERE interaction_type = 'view'
                AND product_handle = ANY($1::text[])
                GROUP BY product_handle
            """, candidate_handles)
            
            view_map = {row['product_handle']: row['views'] for row in stats}
            candidates.sort(key=lambda x: view_map.get(x['handle'], 0), reverse=True)
            
            return candidates[:limit]

    async def get_personalized_most_wishlisted(self, user_id: str, limit: int) -> List[dict]:
        """Get most wishlisted products from personalized recommendations"""
        # 1. Get a larger pool of personalized recommendations
        candidates, _ = await self.get_personalized_recommendations(user_id, limit=50)
        
        if not candidates:
            return []
            
        candidate_handles = [p['handle'] for p in candidates]
        
        # 2. Sort candidates by wishlist count
        async with self.db_pool.acquire() as conn:
            # Get wishlist counts for these candidates
            stats = await conn.fetch("""
                SELECT product_handle, COUNT(*) as wishes
                FROM rec_user_interactions
                WHERE interaction_type = 'wishlist'
                AND product_handle = ANY($1::text[])
                GROUP BY product_handle
            """, candidate_handles)
            
            wishlist_map = {row['product_handle']: row['wishes'] for row in stats}
            candidates.sort(key=lambda x: wishlist_map.get(x['handle'], 0), reverse=True)
            
            return candidates[:limit]

    async def get_top_selling_products(self, limit: int) -> List[dict]:
        """Get top selling products (global)"""
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT product_handle, COUNT(*) as count
                FROM rec_user_interactions
                WHERE interaction_type = 'purchase'
                GROUP BY product_handle
                ORDER BY count DESC
                LIMIT $1
            """, limit)
            
            handles = [row['product_handle'] for row in rows]
            if not handles:
                return []
            return await self._get_products_by_handles(handles)

    async def get_most_viewed_products(self, limit: int) -> List[dict]:
        """Get most viewed products (global)"""
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT product_handle, COUNT(*) as count
                FROM rec_user_interactions
                WHERE interaction_type = 'view'
                GROUP BY product_handle
                ORDER BY count DESC
                LIMIT $1
            """, limit)
            
            handles = [row['product_handle'] for row in rows]
            if not handles:
                return []
            return await self._get_products_by_handles(handles)

    async def get_most_wishlisted_products(self, limit: int) -> List[dict]:
        """Get most wishlisted products (global)"""
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT product_handle, COUNT(*) as count
                FROM rec_user_interactions
                WHERE interaction_type = 'wishlist'
                GROUP BY product_handle
                ORDER BY count DESC
                LIMIT $1
            """, limit)
            
            handles = [row['product_handle'] for row in rows]
            if not handles:
                return []
            return await self._get_products_by_handles(handles)
    
    async def _get_random_products(self, limit: int) -> List[dict]:
        """Get random popular products"""
        async with self.db_pool.acquire() as conn:
            products = await conn.fetch("""
                WITH product_first_price AS (
                    SELECT 
                        p.id,
                        p.handle,
                        p.title,
                        p.thumbnail,
                        p.description,
                        pr.amount,
                        pr.currency_code,
                        ROW_NUMBER() OVER (PARTITION BY p.id ORDER BY 
                            CASE WHEN pr.currency_code = 'vnd' THEN 1 
                                 WHEN pr.currency_code = 'usd' THEN 2 
                                 ELSE 3 END
                        ) as rn
                    FROM product p
                    LEFT JOIN product_variant pv ON p.id = pv.product_id
                    LEFT JOIN product_variant_price_set pvps ON pv.id = pvps.variant_id
                    LEFT JOIN price pr ON pvps.price_set_id = pr.price_set_id
                    WHERE p.status = 'published'
                    AND p.deleted_at IS NULL
                )
                SELECT id, handle, title, thumbnail, description, amount, currency_code
                FROM product_first_price
                WHERE rn = 1 AND amount IS NOT NULL
                ORDER BY RANDOM()
                LIMIT $1
            """, limit)
            
            result = []
            for row in products:
                product_dict = {
                    'id': row['id'],
                    'handle': row['handle'],
                    'title': row['title'],
                    'thumbnail': row['thumbnail'],
                    'description': row['description']
                }
                
                # Add price if available
                if row['amount'] and row['currency_code']:
                    product_dict['price'] = {
                        'amount': format_price(row['amount'], row['currency_code']),
                        'currencyCode': row['currency_code'].upper()
                    }
                
                result.append(product_dict)
            
            return result
    
    async def _get_precomputed_similar(self, product_handle: str, limit: int) -> List[dict]:
        """Get pre-computed similar products"""
        async with self.db_pool.acquire() as conn:
            similar = await conn.fetch("""
                SELECT product_id_2 as handle, similarity_score
                FROM rec_product_similarities
                WHERE product_id_1 = $1
                ORDER BY similarity_score DESC
                LIMIT $2
            """, product_handle, limit)
            
            if not similar:
                return []
            
            handles = [row['handle'] for row in similar]
            return await self._get_products_by_handles(handles)
    
    async def _get_similar_by_category(self, product_handle: str, limit: int) -> List[dict]:
        """Get similar products by product_category and product_collection"""
        async with self.db_pool.acquire() as conn:
            # Get product's categories and collection
            product_info = await conn.fetchrow("""
                SELECT 
                    pc.id as category_id, 
                    pc.name as category_name,
                    pcol.id as collection_id,
                    pcol.title as collection_title
                FROM product p
                LEFT JOIN product_category_product pcp ON p.id = pcp.product_id
                LEFT JOIN product_category pc ON pcp.product_category_id = pc.id
                LEFT JOIN product_collection pcol ON p.collection_id = pcol.id
                WHERE p.handle = $1
                LIMIT 1
            """, product_handle)
            
            if not product_info:
                return []
            
            similar = []
            
            # Get products from same category (if exists)
            if product_info['category_id']:
                category_products = await conn.fetch("""
                    SELECT p.id, p.handle, p.title, p.thumbnail
                    FROM (
                        SELECT DISTINCT p.id, p.handle, p.title, p.thumbnail
                        FROM product p
                        JOIN product_category_product pcp ON p.id = pcp.product_id
                        WHERE pcp.product_category_id = $1
                        AND p.handle != $2
                        AND p.status = 'published'
                        AND p.deleted_at IS NULL
                    ) p
                    ORDER BY RANDOM()
                    LIMIT $3
                """, product_info['category_id'], product_handle, limit//2 + 1)
                similar.extend([dict(row) for row in category_products])
            
            # Get products from same collection (if exists)
            if product_info['collection_id']:
                collection_products = await conn.fetch("""
                    SELECT p.id, p.handle, p.title, p.thumbnail
                    FROM product p
                    WHERE p.collection_id = $1
                    AND p.handle != $2
                    AND p.status = 'published'
                    AND p.deleted_at IS NULL
                    ORDER BY RANDOM()
                    LIMIT $3
                """, product_info['collection_id'], product_handle, limit//2 + 1)
                similar.extend([dict(row) for row in collection_products])
            
            # Remove duplicates and limit results
            seen_handles = set()
            unique_similar = []
            for item in similar:
                if item['handle'] not in seen_handles:
                    seen_handles.add(item['handle'])
                    unique_similar.append(item)
                    if len(unique_similar) >= limit:
                        break
            
            return unique_similar
    
    async def _get_similar_to_cart_wishlist(self, user_id: str, limit: int) -> List[dict]:
        """Get products similar to items in cart/wishlist"""
        async with self.db_pool.acquire() as conn:
            # Get cart/wishlist items
            items = await conn.fetch("""
                SELECT product_handle, MAX(timestamp) as latest
                FROM recommendation.rec_user_interactions
                WHERE user_id = $1
                AND interaction_type IN ('add_to_cart', 'wishlist')
                GROUP BY product_handle
                ORDER BY latest DESC
                LIMIT 5
            """, user_id)
            
            recommendations = []
            for item in items:
                similar = await self._get_similar_by_category(item['product_handle'], limit=2)
                recommendations.extend(similar)
            
            return recommendations[:limit]
    
    async def _get_category_based_on_views(self, user_id: str, limit: int) -> List[dict]:
        """Get recommendations based on product_category and product_collection of viewed products"""
        async with self.db_pool.acquire() as conn:
            # Get top product categories from viewed products
            categories = await conn.fetch("""
                SELECT pc.name as category_name, pc.id as category_id, COUNT(*) as view_count
                FROM recommendation.rec_user_interactions ui
                JOIN product p ON ui.product_handle = p.handle
                JOIN product_category_product pcp ON p.id = pcp.product_id
                JOIN product_category pc ON pcp.product_category_id = pc.id
                WHERE ui.user_id = $1
                AND ui.interaction_type = 'view'
                GROUP BY pc.name, pc.id
                ORDER BY view_count DESC
                LIMIT 2
            """, user_id)
            
            # Get top product collections from viewed products  
            collections = await conn.fetch("""
                SELECT pcol.title as collection_title, pcol.id as collection_id, COUNT(*) as view_count
                FROM recommendation.rec_user_interactions ui
                JOIN product p ON ui.product_handle = p.handle
                JOIN product_collection pcol ON p.collection_id = pcol.id
                WHERE ui.user_id = $1
                AND ui.interaction_type = 'view'
                GROUP BY pcol.title, pcol.id
                ORDER BY view_count DESC
                LIMIT 2
            """, user_id)
            
            recommendations = []
            
            # Get products from top viewed categories
            for cat in categories:
                products = await conn.fetch("""
                    SELECT p.id, p.handle, p.title, p.thumbnail
                    FROM (
                        SELECT DISTINCT p.id, p.handle, p.title, p.thumbnail
                        FROM product p
                        JOIN product_category_product pcp ON p.id = pcp.product_id
                        JOIN product_category pc ON pcp.product_category_id = pc.id
                        WHERE pc.id = $1
                        AND p.status = 'published'
                        AND p.deleted_at IS NULL
                        AND p.handle NOT IN (
                            SELECT DISTINCT product_handle 
                            FROM recommendation.rec_user_interactions 
                            WHERE user_id = $2 AND product_handle IS NOT NULL
                        )
                    ) p
                    ORDER BY RANDOM()
                    LIMIT 2
                """, cat['category_id'], user_id)
                
                recommendations.extend([dict(row) for row in products])
            
            # Get products from top viewed collections
            for col in collections:
                products = await conn.fetch("""
                    SELECT p.id, p.handle, p.title, p.thumbnail
                    FROM product p
                    JOIN product_collection pcol ON p.collection_id = pcol.id
                    WHERE pcol.id = $1
                    AND p.status = 'published'
                    AND p.deleted_at IS NULL
                    AND p.handle NOT IN (
                        SELECT DISTINCT product_handle 
                        FROM recommendation.rec_user_interactions 
                        WHERE user_id = $2 AND product_handle IS NOT NULL
                    )
                    ORDER BY RANDOM()
                    LIMIT 2
                """, col['collection_id'], user_id)
                
                recommendations.extend([dict(row) for row in products])
            
            return recommendations[:limit]
    
    async def _get_similar_products_by_handle(self, product_handle: str, limit: int) -> List[dict]:
        """Helper to get similar products"""
        similar, _ = await self.get_similar_products(product_handle, limit)
        return similar
    
    async def _get_products_by_handles(self, handles: List[str]) -> List[dict]:
        """Fetch full product details by handles"""
        if not handles:
            return []
        
        async with self.db_pool.acquire() as conn:
            products = await conn.fetch("""
                WITH product_first_price AS (
                    SELECT 
                        p.id,
                        p.handle,
                        p.title,
                        p.thumbnail,
                        p.description,
                        pr.amount,
                        pr.currency_code,
                        ROW_NUMBER() OVER (PARTITION BY p.id ORDER BY 
                            CASE WHEN pr.currency_code = 'vnd' THEN 1 
                                 WHEN pr.currency_code = 'usd' THEN 2 
                                 ELSE 3 END
                        ) as rn
                    FROM product p
                    LEFT JOIN product_variant pv ON p.id = pv.product_id
                    LEFT JOIN product_variant_price_set pvps ON pv.id = pvps.variant_id
                    LEFT JOIN price pr ON pvps.price_set_id = pr.price_set_id
                    WHERE p.handle = ANY($1::text[])
                    AND p.status = 'published'
                    AND p.deleted_at IS NULL
                )
                SELECT id, handle, title, thumbnail, description, amount, currency_code
                FROM product_first_price
                WHERE rn = 1 AND amount IS NOT NULL
            """, handles)
            
            result = []
            for row in products:
                product_dict = {
                    'id': row['id'],
                    'handle': row['handle'],
                    'title': row['title'],
                    'thumbnail': row['thumbnail'],
                    'description': row['description']
                }
                
                # Add price if available
                if row['amount'] and row['currency_code']:
                    product_dict['price'] = {
                        'amount': format_price(row['amount'], row['currency_code']),
                        'currencyCode': row['currency_code'].upper()
                    }
                
                result.append(product_dict)
            
            return result
    
    async def get_cached_recommendations(self, cache_key: str) -> Optional[dict]:
        """Get cached recommendations"""
        async with self.db_pool.acquire() as conn:
            cached = await conn.fetchrow("""
                SELECT recommendations, algorithm
                FROM rec_recommendations_cache
                WHERE cache_key = $1
                AND expires_at > NOW()
            """, cache_key)

            if cached:
                recommendations = cached['recommendations']
                # Parse JSON if it's a string
                if isinstance(recommendations, str):
                    try:
                        recommendations = json.loads(recommendations)
                    except:
                        recommendations = []
                
                return {
                    'recommendations': recommendations,
                    'algorithm': cached['algorithm']
                }

            return None
    
    async def cache_recommendations(self, cache_key: str, user_id: str, 
                                   recommendations: List[dict], algorithm: str):
        """Cache recommendations"""
        expires_at = datetime.now() + timedelta(seconds=settings.cache_ttl_seconds)
        
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO rec_recommendations_cache 
                (cache_key, user_id, recommendations, algorithm, created_at, expires_at)
                VALUES ($1, $2, $3, $4, NOW(), $5)
                ON CONFLICT (cache_key)
                DO UPDATE SET 
                    recommendations = $3,
                    algorithm = $4,
                    created_at = NOW(),
                    expires_at = $5
            """, cache_key, user_id, json.dumps(recommendations), algorithm, expires_at)
