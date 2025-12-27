from typing import List, Any, Dict
import time

from app.tools.base import BaseTool
from app.models.agent_types import ToolResults
from app.models import product_to_info, MedusaProduct

# Cache region_id to avoid repeated API calls
_cached_region_id = None

class ProductSearchTool(BaseTool):
    async def run(self, query: str, limit: int = 5, price_condition: Dict[str, Any] = None) -> ToolResults:
        start_time = time.time()
        try:
            # Get or use cached region to ensure prices are returned
            global _cached_region_id
            if _cached_region_id is None:
                regions = await self.client.get_regions()
                _cached_region_id = regions[0]['id'] if regions else None
            
            # If filtering by price, fetch more candidates
            fetch_limit = limit * 5 if price_condition else limit
            
            products_raw = await self.client.search_products(query, fetch_limit, region_id=_cached_region_id)
            
            filtered_products = []
            for p in products_raw:
                if price_condition:
                    # Check price
                    # Get lowest price from variants
                    variants = p.get("variants", [])
                    prices = []
                    for v in variants:
                        # Check calculated_price first
                        if "calculated_price" in v:
                            amount = v["calculated_price"].get("calculated_amount")
                            if amount is not None:
                                prices.append(amount)
                        # Fallback to prices array
                        elif "prices" in v:
                            for price_obj in v["prices"]:
                                amount = price_obj.get("amount")
                                if amount is not None:
                                    prices.append(amount)
                    
                    if not prices:
                        continue # Skip if no price found
                        
                    min_price = min(prices)
                    
                    op = price_condition.get("operator")
                    if op == "lt":
                        if min_price < price_condition["value"]:
                            filtered_products.append(p)
                    elif op == "gt":
                        if min_price > price_condition["value"]:
                            filtered_products.append(p)
                    elif op == "range":
                        if price_condition["min"] <= min_price <= price_condition["max"]:
                            filtered_products.append(p)
                else:
                    filtered_products.append(p)
            
            # Slice to limit
            filtered_products = filtered_products[:limit]

            # Convert raw dicts to MedusaProduct objects to ensure attribute access works
            products = [product_to_info(MedusaProduct(**p)) for p in filtered_products]
            
            duration = int((time.time() - start_time) * 1000)
            return ToolResults(
                ok=True, 
                data=products, 
                errors=[], 
                timings_ms={"search_products": duration}
            )
        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            return ToolResults(
                ok=False, 
                data=None, 
                errors=[str(e)], 
                timings_ms={"search_products": duration}
            )

class ProductDetailTool(BaseTool):
    async def run(self, product_id: str) -> ToolResults:
        start_time = time.time()
        try:
            # Use cached region to ensure prices are returned
            global _cached_region_id
            if _cached_region_id is None:
                regions = await self.client.get_regions()
                _cached_region_id = regions[0]['id'] if regions else None

            product_raw = await self.client.get_product(product_id, region_id=_cached_region_id)
            if not product_raw:
                 return ToolResults(ok=False, data=None, errors=["product_not_found"], timings_ms={})
            
            product = product_to_info(MedusaProduct(**product_raw))
            duration = int((time.time() - start_time) * 1000)
            return ToolResults(
                ok=True, 
                data=product, 
                errors=[], 
                timings_ms={"get_product": duration}
            )
        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            return ToolResults(
                ok=False, 
                data=None, 
                errors=[str(e)], 
                timings_ms={"get_product": duration}
            )

async def get_product_details(product_id: str) -> ToolResults:
    tool = ProductDetailTool()
    return await tool.run(product_id=product_id)

# Backward compatibility wrapper
async def search_products(query: str, limit: int = 10, price_condition: Dict[str, Any] = None) -> ToolResults:
    tool = ProductSearchTool()
    return await tool.run(query=query, limit=limit, price_condition=price_condition)
