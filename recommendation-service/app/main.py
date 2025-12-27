from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import asyncpg
import json
from datetime import datetime, timedelta
import uuid

from app.config import get_settings
from app.services.recommendation_engine import RecommendationEngine
from app.services.interaction_tracker import InteractionTracker
from app.logging_config import setup_logging, get_rec_logger, log_interaction, log_recommendation_request, log_recommendation_result

# Setup logging
setup_logging(log_level="INFO", enable_file_logging=True, enable_console_logging=True)
logger = get_rec_logger("main")

settings = get_settings()
app = FastAPI(title="Recommendation Service", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection pool
db_pool = None

@app.on_event("startup")
async def startup():
    global db_pool
    db_pool = await asyncpg.create_pool(
        settings.database_url, 
        min_size=2, 
        max_size=10,
        server_settings={'search_path': f'{settings.db_schema}, public'}
    )
    logger.info(f"Recommendation service started successfully - schema={settings.db_schema}")

@app.on_event("shutdown")
async def shutdown():
    global db_pool
    if db_pool:
        await db_pool.close()

# Pydantic models
class TrackInteractionRequest(BaseModel):
    user_id: str
    session_id: Optional[str] = None
    product_id: Optional[str] = None
    product_handle: Optional[str] = None
    interaction_type: str  # view, add_to_cart, purchase, wishlist, search
    metadata: Optional[dict] = None

class RecommendationRequest(BaseModel):
    user_id: str
    product_handle: Optional[str] = None
    context: str = "homepage"  # homepage, product_page, cart, checkout
    limit: int = 12

class RecommendationResponse(BaseModel):
    recommendations: List[dict]
    algorithm: str
    user_id: str
    cached: bool = False

# Routes
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "recommendation"}

@app.post("/track")
async def track_interaction(request: TrackInteractionRequest):
    """Track user interaction"""
    try:
        log_interaction(logger, request.user_id, request.interaction_type, request.product_id, request.metadata)
        tracker = InteractionTracker(db_pool)
        interaction_id = await tracker.track(
            user_id=request.user_id,
            session_id=request.session_id,
            product_id=request.product_id,
            product_handle=request.product_handle,
            interaction_type=request.interaction_type,
            metadata=request.metadata or {}
        )
        
        return {
            "success": True,
            "interaction_id": interaction_id
        }
    except Exception as e:
        logger.error(f"Error tracking interaction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recommendations", response_model=RecommendationResponse)
async def post_recommendations(request: RecommendationRequest):
    """Get personalized recommendations via POST request"""
    try:
        import time
        start_time = time.time()
        
        user_id = request.user_id
        product_handle = request.product_handle
        context = request.context
        limit = request.limit
        
        log_recommendation_request(logger, user_id, context, limit, {"product_handle": product_handle})
        engine = RecommendationEngine(db_pool)
        
        # Generate recommendations
        if context == "product_page" and product_handle:
            recommendations, algorithm = await engine.get_similar_products(
                product_handle,
                limit=limit
            )
        elif context == "cart":
            recommendations, algorithm = await engine.get_frequently_bought_together(
                user_id,
                limit=limit
            )
        elif context == "top_selling":
            recommendations = await engine.get_personalized_top_selling(user_id, limit=limit)
            algorithm = "top_selling_personalized"
        elif context == "most_viewed":
            recommendations = await engine.get_personalized_most_viewed(user_id, limit=limit)
            algorithm = "most_viewed_personalized"
        elif context == "most_wishlisted":
            recommendations = await engine.get_personalized_most_wishlisted(user_id, limit=limit)
            algorithm = "most_wishlisted_personalized"
        else:  # homepage or default
            recommendations, algorithm = await engine.get_personalized_recommendations(
                user_id,
                limit=limit
            )
        
        execution_time = (time.time() - start_time) * 1000
        log_recommendation_result(
            logger, user_id, algorithm, len(recommendations),
            execution_time, {"context": context, "product_handle": product_handle}
        )
        
        return RecommendationResponse(
            recommendations=recommendations,
            algorithm=algorithm,
            user_id=user_id,
            cached=False
        )
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(
    user_id: str,
    product_handle: Optional[str] = None,
    context: str = "homepage",
    limit: int = 12
):
    """Get personalized recommendations via GET request"""
    try:
        import time
        start_time = time.time()
        
        log_recommendation_request(logger, user_id, context, limit, {"product_handle": product_handle})
        engine = RecommendationEngine(db_pool)
        
        # Generate recommendations
        if context == "product_page" and product_handle:
            recommendations, algorithm = await engine.get_similar_products(
                product_handle,
                limit=limit
            )
        elif context == "cart":
            recommendations, algorithm = await engine.get_frequently_bought_together(
                user_id,
                limit=limit
            )
        elif context == "top_selling":
            recommendations = await engine.get_personalized_top_selling(user_id, limit=limit)
            algorithm = "top_selling_personalized"
        elif context == "most_viewed":
            recommendations = await engine.get_personalized_most_viewed(user_id, limit=limit)
            algorithm = "most_viewed_personalized"
        elif context == "most_wishlisted":
            recommendations = await engine.get_personalized_most_wishlisted(user_id, limit=limit)
            algorithm = "most_wishlisted_personalized"
        else:  # homepage or default
            recommendations, algorithm = await engine.get_personalized_recommendations(
                user_id,
                limit=limit
            )
        
        execution_time = (time.time() - start_time) * 1000
        log_recommendation_result(
            logger, user_id, algorithm, len(recommendations),
            execution_time, {"context": context, "product_handle": product_handle}
        )
        
        return RecommendationResponse(
            recommendations=recommendations,
            algorithm=algorithm,
            user_id=user_id,
            cached=False
        )
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/{user_id}/preferences")
async def get_user_preferences(user_id: str):
    """Get learned user preferences"""
    try:
        async with db_pool.acquire() as conn:
            prefs = await conn.fetchrow(
                "SELECT * FROM rec_user_preferences WHERE user_id = $1",
                user_id
            )
            
            if not prefs:
                return {"user_id": user_id, "preferences": None}
            
            return {
                "user_id": user_id,
                "category_scores": prefs['category_scores'],
                "price_range": {
                    "min": float(prefs['price_min']) if prefs['price_min'] else None,
                    "max": float(prefs['price_max']) if prefs['price_max'] else None
                },
                "preferred_brands": prefs['preferred_brands'],
                "last_updated": prefs['last_updated'].isoformat()
            }
    except Exception as e:
        logger.error(f"Error getting preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/recommendations/similar")
async def get_similar_products(product_id: str, limit: int = 5):
    """Get similar products for a given product ID"""
    try:
        engine = RecommendationEngine(db_pool)
        
        # First try to get product handle by ID
        query = """
        SELECT handle FROM product WHERE id = $1
        """
        result = await db_pool.fetchrow(query, product_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Product not found")
        
        product_handle = result['handle']
        
        # Get similar products
        recommendations, algorithm = await engine.get_similar_products(
            product_handle,
            limit=limit
        )
        
        return {
            "recommendations": recommendations,
            "algorithm": algorithm,
            "product_id": product_id,
            "product_handle": product_handle
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting similar products: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/compute/similarities")
async def compute_product_similarities():
    """Compute product similarities (run periodically)"""
    try:
        engine = RecommendationEngine(db_pool)
        count = await engine.compute_all_similarities()
        return {
            "success": True,
            "similarities_computed": count,
            "message": "Product similarities computed successfully"
        }
    except Exception as e:
        logger.error(f"Error computing similarities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/compute/user-preferences")
async def compute_user_preferences(user_id: Optional[str] = None):
    """Compute user preferences from interactions"""
    try:
        tracker = InteractionTracker(db_pool)
        
        if user_id:
            await tracker.update_user_preferences(user_id)
            return {"success": True, "user_id": user_id}
        else:
            # Update all active users
            count = await tracker.update_all_user_preferences()
            return {"success": True, "users_updated": count}
    except Exception as e:
        logger.error(f"Error computing preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
