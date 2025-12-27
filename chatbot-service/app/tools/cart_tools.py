import time
import logging
from typing import Any, Dict, Optional, List

from app.tools.base import BaseTool
from app.models.agent_types import ToolResults

logger = logging.getLogger(__name__)

class CartViewTool(BaseTool):
    async def run(self, cart_id: str) -> ToolResults:
        if not cart_id:
             return ToolResults(ok=False, errors=["No cart_id provided"])
        
        cart = await self.client.get_cart(cart_id)
        if "error" in cart:
             return ToolResults(ok=False, errors=[cart["error"]])
             
        return ToolResults(ok=True, data=cart, errors=[])

class CartAddTool(BaseTool):
    async def _ensure_shipping_method(self, cart_id: str, cart_data: Optional[Dict] = None):
        """
        Ensures the cart has a valid shipping method.
        Checks if the current shipping method is valid for the cart contents, 
        and updates it if necessary.
        """
        try:
            # 1. Get valid options for the CURRENT cart state (with new items)
            options = await self.client.get_shipping_options(cart_id)
            if not options:
                logger.warning(f"No shipping options available for cart {cart_id}")
                return

            valid_option_ids = [opt["id"] for opt in options]

            # 2. Check current shipping methods
            if not cart_data or "shipping_methods" not in cart_data:
                cart_data = await self.client.get_cart(cart_id)
            
            current_methods = cart_data.get("shipping_methods", [])
            
            needs_update = False
            if not current_methods:
                needs_update = True
                logger.info(f"Cart {cart_id} has no shipping methods.")
            else:
                # Check if current method is valid
                # Assuming single shipping method for simplicity (standard Medusa)
                current_method_id = current_methods[0].get("shipping_option_id")
                if current_method_id not in valid_option_ids:
                    needs_update = True
                    logger.info(f"Cart {cart_id} has invalid shipping method {current_method_id}. Valid options: {valid_option_ids}")
            
            if needs_update:
                # Select the first option (usually the cheapest or default)
                option_id = options[0]["id"]
                logger.info(f"Setting shipping method {option_id} for cart {cart_id}")
                await self.client.add_shipping_method(cart_id, option_id)
                
        except Exception as e:
            logger.error(f"Failed to ensure shipping method for cart {cart_id}: {e}")

    async def run(self, cart_id: str, variant_id: str, quantity: int = 1) -> ToolResults:
        if not cart_id:
            # Create new cart if none exists
            logger.info("No cart_id provided, creating new cart")
            new_cart = await self.client.create_cart()
            if "id" not in new_cart:
                return ToolResults(ok=False, errors=["Failed to create cart"])
            cart_id = new_cart["id"]
            # Do NOT add shipping yet. Add item first so we get valid options.

        # 1. Try to add to existing cart
        res = await self.client.add_line_item(cart_id, variant_id, quantity)
        
        # 2. Check for failure (specifically completed cart)
        if "error" in res:
            error_msg = str(res.get("error", "")).lower()
            status_code = res.get("status_code", 0)
            
            # Check if error is due to completed cart or other unrecoverable state
            # Medusa returns 400 or 422 for completed carts
            if "completed" in error_msg or "payment" in error_msg or status_code in [400, 422]:
                logger.info(f"Cart {cart_id} seems completed or invalid ({error_msg}), creating new cart...")
                
                # 3. Create new cart
                new_cart = await self.client.create_cart()
                if "id" in new_cart:
                    new_cart_id = new_cart["id"]
                    # Do NOT add shipping yet.
                    
                    # 4. Add to new cart
                    res_new = await self.client.add_line_item(new_cart_id, variant_id, quantity)
                    if "error" not in res_new:
                        # Success with new cart
                        # NOW ensure shipping method
                        await self._ensure_shipping_method(new_cart_id, res_new)

                        return ToolResults(
                            ok=True, 
                            data={
                                "message": "Created new cart and added item", 
                                "cart_id": new_cart_id, # Return NEW cart ID
                                "cart": res_new,
                                "new_cart_created": True
                            }, 
                            errors=[]
                        )
                    else:
                        return ToolResults(ok=False, errors=[f"Failed to add to new cart: {res_new.get('error')}"])
                else:
                    return ToolResults(ok=False, errors=["Failed to create new cart"])
            
            return ToolResults(ok=False, errors=[str(res.get("error", "Unknown error"))])
        
        # Success on first try
        # Ensure shipping method
        await self._ensure_shipping_method(cart_id, res)
            
        return ToolResults(ok=True, data={"message": "Item added", "cart": res, "cart_id": cart_id}, errors=[])

class CartRemoveTool(BaseTool):
    async def run(self, cart_id: str, line_item_id: str) -> ToolResults:
        # Mock implementation
        return ToolResults(ok=True, data={"message": "Item removed"}, errors=[])

class CartAddSmartTool(BaseTool):
    async def run(self, cart_id: str, query: str, quantity: int = 1) -> ToolResults:
        try:
            # 1. Search for product
            products = await self.client.search_products(query, limit=1)
            if not products:
                return ToolResults(ok=False, errors=[f"Product not found: {query}"])
            
            product = products[0]
            variants = product.get("variants", [])
            if not variants:
                return ToolResults(ok=False, errors=[f"Product has no variants: {product.get('title')}"])
            
            # 2. Pick first variant (simplification)
            variant_id = variants[0]["id"]
            variant_title = variants[0].get("title", "")
            product_title = product.get("title", "")
            
            # 3. Use CartAddTool logic
            add_tool = CartAddTool(self.client)
            res = await add_tool.run(cart_id, variant_id, quantity)
            
            if res.ok:
                # Enhance data with product info
                if isinstance(res.data, dict):
                    res.data["product_title"] = product_title
                    res.data["variant_title"] = variant_title
                    res.data["added_item"] = {"variant_id": variant_id, "quantity": quantity}
                
            return res
        except Exception as e:
            return ToolResults(ok=False, errors=[str(e)])

async def view_cart(cart_id: str) -> ToolResults:
    tool = CartViewTool()
    return await tool.run(cart_id=cart_id)

async def add_to_cart(cart_id: str, variant_id: str, quantity: int = 1) -> ToolResults:
    tool = CartAddTool()
    return await tool.run(cart_id=cart_id, variant_id=variant_id, quantity=quantity)

async def add_to_cart_smart(cart_id: str, query: str, quantity: int = 1) -> ToolResults:
    tool = CartAddSmartTool()
    return await tool.run(cart_id=cart_id, query=query, quantity=quantity)

async def remove_from_cart(cart_id: str, line_item_id: str) -> ToolResults:
    tool = CartRemoveTool()
    return await tool.run(cart_id=cart_id, line_item_id=line_item_id)
