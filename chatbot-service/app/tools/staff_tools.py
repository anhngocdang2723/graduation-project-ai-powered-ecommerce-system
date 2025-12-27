import time
from typing import Any, Dict, Optional, List

from app.tools.base import BaseTool
from app.models.agent_types import ToolResults

class StockCheckTool(BaseTool):
    async def run(self, query: str) -> ToolResults:
        start_time = time.time()
        try:
            # Search for the product first
            products = await self.client.search_products(query, limit=5)
            
            results = []
            for p in products:
                # Extract variant inventory
                variants_info = []
                variants = p.get("variants", [])
                total_stock = 0
                
                for v in variants:
                    # Medusa API usually returns 'inventory_quantity' in variant
                    qty = v.get("inventory_quantity", 0)
                    title = v.get("title", "Default")
                    sku = v.get("sku", "N/A")
                    variants_info.append({
                        "title": title,
                        "sku": sku,
                        "quantity": qty
                    })
                    total_stock += qty
                
                results.append({
                    "id": p.get("id"),
                    "title": p.get("title"),
                    "total_stock": total_stock,
                    "variants": variants_info
                })
            
            duration = int((time.time() - start_time) * 1000)
            return ToolResults(
                ok=True, 
                data=results, 
                errors=[], 
                timings_ms={"check_stock": duration}
            )
        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            return ToolResults(
                ok=False, 
                data=None, 
                errors=[str(e)], 
                timings_ms={"check_stock": duration}
            )

async def check_stock(query: str) -> ToolResults:
    tool = StockCheckTool()
    return await tool.run(query=query)

class CustomerLookupTool(BaseTool):
    async def run(self, query: str) -> ToolResults:
        # Mock implementation
        return ToolResults(ok=True, data=[{"id": "cus_123", "email": "test@example.com", "name": "Test User"}], errors=[])

async def lookup_customer(query: str) -> ToolResults:
    tool = CustomerLookupTool()
    return await tool.run(query=query)

class OrderHistoryTool(BaseTool):
    async def run(self, customer_id: str) -> ToolResults:
        # Mock implementation
        return ToolResults(ok=True, data=[{"id": "order_1", "total": 100000, "status": "completed"}], errors=[])

async def get_customer_order_history(customer_id: str) -> ToolResults:
    tool = OrderHistoryTool()
    return await tool.run(customer_id=customer_id)

class CreateOrderTool(BaseTool):
    async def run(self, customer_id: str, items: List[Dict]) -> ToolResults:
        # Mock implementation
        return ToolResults(ok=True, data={"id": "order_new_123", "status": "draft"}, errors=[])

async def create_draft_order(customer_id: str, items: List[Dict]) -> ToolResults:
    tool = CreateOrderTool()
    return await tool.run(customer_id=customer_id, items=items)

class CheckPriceTool(BaseTool):
    async def run(self, query: str) -> ToolResults:
        # Mock
        return ToolResults(ok=True, data={"product": "Medusa T-Shirt", "price": "500,000 VND"}, errors=[])

async def check_price(query: str) -> ToolResults:
    tool = CheckPriceTool()
    return await tool.run(query=query)

class StaffOrderLookupTool(BaseTool):
    async def run(self, order_id: str) -> ToolResults:
        # Mock
        return ToolResults(ok=True, data={"id": order_id, "status": "processing", "customer": "John Doe"}, errors=[])

async def lookup_order(order_id: str) -> ToolResults:
    tool = StaffOrderLookupTool()
    return await tool.run(order_id=order_id)

class UpdateOrderStatusTool(BaseTool):
    async def run(self, order_id: str, status: str) -> ToolResults:
        # Mock
        return ToolResults(ok=True, data={"id": order_id, "new_status": status}, errors=[])

async def update_order_status(order_id: str, status: str) -> ToolResults:
    tool = UpdateOrderStatusTool()
    return await tool.run(order_id=order_id, status=status)

class PrintLabelTool(BaseTool):
    async def run(self, order_id: str) -> ToolResults:
        # Mock
        return ToolResults(ok=True, data={"label_url": "http://example.com/label.pdf"}, errors=[])

async def print_shipping_label(order_id: str) -> ToolResults:
    tool = PrintLabelTool()
    return await tool.run(order_id=order_id)
