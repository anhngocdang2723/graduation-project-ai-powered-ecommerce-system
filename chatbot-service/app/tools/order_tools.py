import time
from typing import Any, Dict

from app.tools.base import BaseTool
from app.models.agent_types import ToolResults

class OrderLookupTool(BaseTool):
    async def run(self, order_id: str) -> ToolResults:
        start_time = time.time()
        try:
            order = await self.client.get_order(order_id)
            duration = int((time.time() - start_time) * 1000)
            
            if order and "id" in order:
                return ToolResults(
                    ok=True, 
                    data=order, 
                    errors=[], 
                    timings_ms={"get_order": duration}
                )
            else:
                err = order.get("error", "order_not_found") if order else "order_not_found"
                return ToolResults(
                    ok=False, 
                    data=None, 
                    errors=[err], 
                    timings_ms={"get_order": duration}
                )
        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            return ToolResults(
                ok=False, 
                data=None, 
                errors=[str(e)], 
                timings_ms={"get_order": duration}
            )

async def lookup_order(order_id: str) -> ToolResults:
    tool = OrderLookupTool()
    return await tool.run(order_id=order_id)

class OrderCancelTool(BaseTool):
    async def run(self, order_id: str) -> ToolResults:
        # Mock implementation
        return ToolResults(ok=True, data={"message": f"Order {order_id} cancellation request received."}, errors=[])

async def cancel_order(order_id: str) -> ToolResults:
    tool = OrderCancelTool()
    return await tool.run(order_id=order_id)

class OrderListTool(BaseTool):
    async def run(self, customer_id: str = None) -> ToolResults:
        start_time = time.time()
        try:
            # For demo purposes, we list recent orders from the system
            # In a real scenario, we would filter by customer_id if provided
            orders = await self.client.list_orders(limit=5)
            duration = int((time.time() - start_time) * 1000)
            
            return ToolResults(
                ok=True, 
                data=orders, 
                errors=[],
                timings_ms={"list_orders": duration}
            )
        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            return ToolResults(
                ok=False, 
                data=None, 
                errors=[str(e)], 
                timings_ms={"list_orders": duration}
            )

async def list_orders(customer_id: str = None) -> ToolResults:
    tool = OrderListTool()
    return await tool.run(customer_id=customer_id)

class ReorderTool(BaseTool):
    async def run(self, order_id: str) -> ToolResults:
        # Mock implementation
        return ToolResults(ok=True, data={"cart_id": "cart_new_from_order", "message": "Items added to cart"}, errors=[])

async def reorder(order_id: str) -> ToolResults:
    tool = ReorderTool()
    return await tool.run(order_id=order_id)
