import logging
from typing import Optional, Dict, Any
from app.models.agent_types import ProcessedInput, IntentResult, ActionPlan, ToolResults
from app.tools import (
    cart_tools,
    product_tools,
    product_recommend_tool,
    order_tools,
    staff_tools,
    report_tools,
    system_tools,
    customer_tools
)
from app.logging_config import get_agent_logger

logger = get_agent_logger("Executor")


def _merge_tool_result(results: ToolResults, tool_result: Any):
    if tool_result is None:
        return
    if isinstance(tool_result, ToolResults):
        results.ok = results.ok and tool_result.ok
        if tool_result.errors:
            results.errors.extend(tool_result.errors)
        if tool_result.timings_ms:
            results.timings_ms.update(tool_result.timings_ms)
        results.data = tool_result.data
    else:
        results.data = tool_result

class Executor:
    async def run(
        self, 
        processed: ProcessedInput, 
        intent: IntentResult, 
        plan: ActionPlan
    ) -> Optional[ToolResults]:
        if not plan.tools:
            return None

        results = ToolResults(ok=True)
        
        for tool_name in plan.tools:
            try:
                logger.info(f"[Executor] Running tool: {tool_name}")
                
                # Cart Tools
                if tool_name == "cart.view":
                    if processed.session_ctx.cart_id:
                        res = await cart_tools.view_cart(processed.session_ctx.cart_id)
                        _merge_tool_result(results, res)
                    else:
                        results.ok = False
                        results.errors.append("Missing cart_id")
                elif tool_name == "cart.add":
                    # Extract product and quantity from entities
                    query = intent.entities.get("product_query", processed.cleaned_text)
                    qty = intent.entities.get("quantity", 1)
                    variant_id = intent.entities.get("variant_id")
                    
                    # Pass current cart_id (can be None) to tools
                    current_cart_id = processed.session_ctx.cart_id
                    
                    if variant_id:
                        # If we have explicit variant_id (e.g. from UI action), use it directly
                        res = await cart_tools.add_to_cart(current_cart_id, variant_id, qty)
                    else:
                        # Otherwise try smart add (search -> add)
                        res = await cart_tools.add_to_cart_smart(current_cart_id, query, qty)
                    
                    _merge_tool_result(results, res)
                    
                    # Check if a new cart was created (e.g. because old one was completed)
                    if res.ok and isinstance(res.data, dict) and res.data.get("new_cart_created"):
                        new_cart_id = res.data.get("cart_id")
                        if new_cart_id:
                            logger.info(f"[Executor] Updating session cart_id from {current_cart_id} to {new_cart_id}")
                            processed.session_ctx.cart_id = new_cart_id
                            # Add to entities so ResponseGenerator can see it
                            intent.entities["new_cart_id"] = new_cart_id
                
                # Product Tools
                elif tool_name == "product.search":
                    query = intent.entities.get("product_query", processed.cleaned_text)
                    price_condition = intent.entities.get("price_condition")
                    res = await product_tools.search_products(query, price_condition=price_condition)
                    _merge_tool_result(results, res)
                    
                    # Context Passing for Sequential Execution (e.g. Search -> Add)
                    if res.ok and res.data and isinstance(res.data, list) and len(res.data) > 0:
                        first_product = res.data[0]
                        # Try to find a variant ID to pass to subsequent tools (like cart.add)
                        variant_id = None
                        try:
                            if isinstance(first_product, dict):
                                if "variants" in first_product and first_product["variants"]:
                                    v = first_product["variants"][0]
                                    variant_id = v.get("id") if isinstance(v, dict) else getattr(v, "id", None)
                            else:
                                # Handle object model (Pydantic or class)
                                variants = getattr(first_product, "variants", [])
                                if variants:
                                    v = variants[0]
                                    variant_id = v.get("id") if isinstance(v, dict) else getattr(v, "id", None)
                        except Exception as e:
                            logger.warning(f"[Executor] Error extracting variant_id: {e}")

                        if variant_id:
                            product_title = first_product.get('title', 'unknown') if isinstance(first_product, dict) else getattr(first_product, 'title', 'unknown')
                            logger.info(f"[Executor] Context passing: Found product '{product_title}', using variant {variant_id} for next steps")
                            intent.entities["variant_id"] = variant_id
                            intent.entities["product_title"] = product_title

                elif tool_name == "product.recommend":
                    # The tool currently only accepts limit, not customer_id
                    res = await product_recommend_tool.recommend_products(limit=5)
                    _merge_tool_result(results, res)
                elif tool_name == "product.detail":
                    # Try to get product_id from entities first
                    product_id = intent.entities.get("product_id")
                    
                    # If no product_id in entities, try to get from context (last products shown)
                    if not product_id and processed.session_ctx.last_product_ids:
                        product_id = processed.session_ctx.last_product_ids[0]
                        logger.info(f"[Executor] Using context product_id: {product_id}")
                    
                    if product_id:
                        res = await product_tools.get_product_details(product_id)
                        _merge_tool_result(results, res)
                    else:
                        # Fallback: try to search if we have a query
                        # Extract product name from text (remove "chi tiết", "xem", etc)
                        import re
                        query = intent.entities.get("product_query")
                        if not query:
                            # Try to extract product name from cleaned text
                            text_lower = processed.cleaned_text.lower()
                            # Remove common phrases (order matters - remove longer phrases first)
                            for phrase in ["cho tôi xem chi tiết", "cho tôi xem", "xem chi tiết", "chi tiết của", "chi tiết", "xem", "tôi muốn", "muốn"]:
                                text_lower = text_lower.replace(phrase, "")
                            query = text_lower.strip()
                        
                        if query and len(query) >= 2:
                            logger.info(f"[Executor] Searching for product: '{query}'")
                            res = await product_tools.search_products(query, limit=1)
                            _merge_tool_result(results, res)
                            # Store search query in entities for response_generator
                            intent.entities["product_query"] = query
                        else:
                            results.ok = False
                            results.errors.append("Missing product_id or query")
                            # Still store a placeholder for template
                            intent.entities["product_query"] = "sản phẩm bạn cần"

                # Order Tools
                elif tool_name == "order.track":
                    order_id = intent.entities.get("order_id")
                    email = intent.entities.get("email") # Might need to ask user
                    if order_id:
                        res = await order_tools.lookup_order(order_id)
                        _merge_tool_result(results, res)
                    else:
                        # If no order_id, list orders so user can choose
                        logger.info("[Executor] No order_id provided for tracking, listing orders instead")
                        res = await order_tools.list_orders(processed.customer_id)
                        _merge_tool_result(results, res)
                elif tool_name == "order.list":
                    # Allow listing without customer_id (demo mode)
                    res = await order_tools.list_orders(processed.customer_id)
                    _merge_tool_result(results, res)
                elif tool_name == "order.reorder":
                    # Assuming we reorder the last order or specific order
                    order_id = intent.entities.get("order_id")
                    if order_id:
                        res = await order_tools.reorder(order_id)
                        _merge_tool_result(results, res)
                    else:
                        # Maybe list orders to pick?
                        results.ok = False
                        results.errors.append("Missing order_id")

                # Staff Tools
                elif tool_name == "staff.check_stock":
                    query = intent.entities.get("product_query", processed.cleaned_text)
                    res = await staff_tools.check_stock(query)
                    _merge_tool_result(results, res)
                elif tool_name == "staff.check_price":
                    query = intent.entities.get("product_query", processed.cleaned_text)
                    res = await staff_tools.check_price(query)
                    _merge_tool_result(results, res)
                elif tool_name == "staff.customer_lookup":
                    query = intent.entities.get("customer_query", processed.cleaned_text)
                    res = await staff_tools.lookup_customer(query)
                    _merge_tool_result(results, res)
                elif tool_name == "staff.order_history":
                    customer_id = intent.entities.get("customer_id")
                    if customer_id:
                        res = await staff_tools.get_customer_order_history(customer_id)
                        _merge_tool_result(results, res)
                    else:
                        results.ok = False
                        results.errors.append("Missing customer_id")
                elif tool_name == "staff.create_order":
                    if processed.customer_id:
                        res = await staff_tools.create_draft_order(processed.customer_id, [])
                        _merge_tool_result(results, res)
                    else:
                        results.ok = False
                        results.errors.append("Missing customer_id")
                elif tool_name == "staff.lookup_order":
                    order_id = intent.entities.get("order_id")
                    if order_id:
                        res = await staff_tools.lookup_order(order_id)
                        _merge_tool_result(results, res)
                    else:
                        results.ok = False
                        results.errors.append("Missing order_id")
                elif tool_name == "staff.update_order":
                    order_id = intent.entities.get("order_id")
                    status = intent.entities.get("status", "processing")
                    if order_id:
                        res = await staff_tools.update_order_status(order_id, status)
                        _merge_tool_result(results, res)
                    else:
                        results.ok = False
                        results.errors.append("Missing order_id")
                elif tool_name == "staff.print_label":
                    order_id = intent.entities.get("order_id")
                    if order_id:
                        res = await staff_tools.print_shipping_label(order_id)
                        _merge_tool_result(results, res)
                    else:
                        results.ok = False
                        results.errors.append("Missing order_id")
                
                # Manager Tools
                elif tool_name == "manager.report_sales":
                    res = await report_tools.get_sales_report()
                    _merge_tool_result(results, res)
                elif tool_name == "manager.top_products":
                    res = await report_tools.get_top_products()
                    _merge_tool_result(results, res)
                elif tool_name == "manager.customer_analytics":
                    res = await report_tools.get_customer_analytics()
                    _merge_tool_result(results, res)

                # System/Auth Tools
                elif tool_name == "system.escalate":
                    # Just a marker, maybe log it
                    results.data = {"status": "escalated", "message": "Connecting to human agent..."}
                elif tool_name == "auth.logout":
                    # In a real app, this might invalidate session
                    results.data = {"status": "logged_out", "message": "You have been logged out."}
                
                # Product Tools (Extra)
                elif tool_name == "product.reviews":
                    # Mock
                    results.data = {"reviews": []}

                else:
                    logger.warning(f"[Executor] Unknown tool: {tool_name}")
                    results.errors.append(f"Unknown tool: {tool_name}")

            except Exception as e:
                logger.error(f"[Executor] Error running {tool_name}: {e}")
                results.ok = False
                results.errors.append(str(e))
        
        return results
