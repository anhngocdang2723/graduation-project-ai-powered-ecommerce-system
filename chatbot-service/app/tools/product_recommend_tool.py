import time
from typing import Any, Dict, Optional, List

from app.tools.base import BaseTool
from app.models.agent_types import ToolResults
from app.models.api_models import ProductInfo

class ProductRecommendTool(BaseTool):
    async def run(self, limit: int = 5) -> ToolResults:
        start_time = time.time()
        try:
            # For recommendations, return featured/popular products
            # Use empty search to get all products, then take first N
            products_raw = await self.client.search_products("", limit)
            
            # Convert to ProductInfo format (same as product_tools)
            results = []
            for p in products_raw:
                results.append(p)  # p is already ProductInfo from client

            duration = int((time.time() - start_time) * 1000)
            return ToolResults(
                ok=True, 
                data=results, 
                errors=[], 
                timings_ms={"recommend_products": duration}
            )
        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            return ToolResults(
                ok=False, 
                data=None, 
                errors=[str(e)], 
                timings_ms={"recommend_products": duration}
            )

async def recommend_products(limit: int = 5) -> ToolResults:
    tool = ProductRecommendTool()
    return await tool.run(limit=limit)
