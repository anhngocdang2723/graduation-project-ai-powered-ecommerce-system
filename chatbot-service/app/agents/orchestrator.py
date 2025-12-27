from typing import Optional, Tuple, Dict

from app.models.agent_types import ActionPlan, ToolResults, ProcessedInput, IntentResult
from app.agents.specialized.sales_agent import SalesAgent
from app.agents.specialized.order_agent import OrderAgent
from app.agents.specialized.staff_agent import StaffAgent
from app.agents.specialized.manager_agent import ManagerAgent
from app.logging_config import get_agent_logger

logger = get_agent_logger("Orchestrator")

class Orchestrator:
    def __init__(self):
        self.agents = {
            "sales": SalesAgent(),
            "order": OrderAgent(),
            "staff": StaffAgent(),
            "manager": ManagerAgent()
        }

    async def run(
        self,
        processed: ProcessedInput,
        intent: IntentResult,
    ) -> Tuple[ActionPlan, Optional[ToolResults]]:
        """
        Hybrid Orchestrator:
        1. Executable Tag -> Execute Tool directly
        2. Scope Tag -> Route to Specialized Agent (Scoped NLU)
        3. No Tag -> Global NLU -> Route to Agent
        """
        logger.info(f"Routing request - tag={processed.tag} intent={intent.intent}")
        
        # 1. Executable Tag (e.g., "action:view_cart")
        if processed.tag and processed.tag.startswith("action:"):
            action = processed.tag.split(":", 1)[1]
            logger.info(f"Direct action routing - action={action}")
            
            if action == "view_cart":
                return ActionPlan(tools=["cart.view"], next_step="show_cart"), None
            elif action == "order_list":
                return ActionPlan(tools=["order.list"], next_step="show_orders"), None
            elif action == "order_track":
                # If we have order_id in context/entities, we can call tool directly.
                # But usually tracking needs input. 
                # If this is a button click, maybe we just prompt?
                # Or if it's "Tra cứu vận chuyển" button, we might want to ask for ID.
                # But if we want to execute a tool, we return it.
                return ActionPlan(tools=[], next_step="ask_order_id"), None
            elif action == "reorder":
                return ActionPlan(tools=["order.reorder"], next_step="confirm_reorder"), None
            elif action == "logout":
                return ActionPlan(tools=["auth.logout"], next_step="confirm_logout"), None
            elif action == "chat_human":
                return ActionPlan(tools=["system.escalate"], next_step="escalate_chat"), None
            elif action == "my_reviews":
                return ActionPlan(tools=["product.reviews"], next_step="show_reviews"), None
            elif action == "check_stock":
                return ActionPlan(tools=[], next_step="ask_product_name"), None # Need product name
            elif action == "check_price":
                return ActionPlan(tools=[], next_step="ask_product_name"), None # Need product name
            elif action == "staff_lookup_order":
                return ActionPlan(tools=[], next_step="ask_order_id"), None
            elif action == "staff_customer_lookup":
                return ActionPlan(tools=[], next_step="ask_customer_info"), None
            elif action == "update_order_status":
                return ActionPlan(tools=[], next_step="ask_order_id_status"), None
            elif action == "print_shipping_label":
                return ActionPlan(tools=[], next_step="ask_order_id"), None
            elif action == "sales_report":
                return ActionPlan(tools=["manager.report_sales"], next_step="show_report"), None
            elif action == "top_products":
                return ActionPlan(tools=["manager.top_products"], next_step="show_top_products"), None
            elif action == "customer_analytics":
                return ActionPlan(tools=["manager.customer_analytics"], next_step="show_analytics"), None
            elif action.startswith("cart.add_item"):
                try:
                    params = {}
                    if "?" in action:
                        query = action.split("?", 1)[1]
                        for pair in query.split("&"):
                            if "=" in pair:
                                k, v = pair.split("=", 1)
                                params[k] = v
                    
                    intent.entities["product_id"] = params.get("product_id")
                    intent.entities["variant_id"] = params.get("variant_id")
                    intent.entities["quantity"] = 1
                    
                    return ActionPlan(tools=["cart.add"], next_step="confirm_add_to_cart"), None
                except Exception as e:
                    logger.error(f"Error parsing cart.add_item tag: {e}")
                    return ActionPlan(tools=[], next_step="error"), None
            
            # Add more direct actions here
        
        # 2.5 Multi-Intent Orchestration (Sequential Planning)
        # Handle "Find X and add to cart" scenario
        if (intent.intent == "cart_add" and intent.sub_intent == "product_inquiry") or \
           (intent.intent == "product_inquiry" and intent.sub_intent == "cart_add"):
            
            logger.info(f"Multi-intent detected: {intent.intent} + {intent.sub_intent} -> Sequential Plan")
            
            # If we have a product query, we plan: Search -> Add
            if intent.entities.get("product_query"):
                return ActionPlan(
                    tools=["product.search", "cart.add"], 
                    next_step="confirm_add_to_cart"
                ), None

        # 2. Scope Tag (e.g., "scope:order")
        if processed.tag and processed.tag.startswith("scope:"):
            scope = processed.tag.split(":", 1)[1]
            agent = self.agents.get(scope)
            if agent:
                logger.info(f"Scoped routing - scope={scope} agent={agent.__class__.__name__}")
                # Agent performs its own scoped NLU if intent is generic/unknown or we want to re-evaluate
                # For now, we pass None as intent to force agent to re-classify within scope
                return await agent.process(processed, intent=None)
        
        # 3. Implicit Routing (Global NLU)
        # We use the intent passed from the global classifier to decide which agent to call
        target_agent = self._route_by_intent(intent.intent)
        if target_agent:
            logger.info(f"Implicit routing - intent={intent.intent} agent={target_agent.__class__.__name__}")
            action_plan, tool_results = await target_agent.process(processed, intent)
            
            # Only fallback if agent returns empty plan AND we haven't tried the default sales agent
            if not action_plan.tools and not action_plan.next_step and target_agent != self.agents["sales"]:
                logger.warning(f"Agent {target_agent.__class__.__name__} returned empty plan, trying sales fallback")
                return await self.agents["sales"].process(processed, intent)
                
            return action_plan, tool_results
            
        # Default fallback to sales agent
        logger.warning(f"No agent found for intent={intent.intent}, using sales agent as fallback")
        return await self.agents["sales"].process(processed, intent)

    def _route_by_intent(self, intent_name: str):
        """Route intent to appropriate specialized agent"""
        for agent in self.agents.values():
            if agent.can_handle(intent_name):
                return agent
        # Always return sales agent as default fallback (never return None)
        return self.agents["sales"]
    
    def get_agent_suggestions(self, intent: str) -> list:
        """Get suggested actions based on intent - for better UX"""
        suggestions = {
            "product_inquiry": [
                {"label": "Xem giỏ hàng", "action": "action:view_cart"},
                {"label": "Sản phẩm gợi ý", "action": "action:my_recommendations"},
            ],
            "cart_view": [
                {"label": "Thanh toán ngay", "action": "action:checkout"},
                {"label": "Tiếp tục mua sắm", "action": "action:continue_shopping"},
            ],
            "order_tracking": [
                {"label": "Đơn hàng của tôi", "action": "action:order_list"},
                {"label": "Liên hệ hỗ trợ", "action": "action:chat_human"},
            ],
            "general": [
                {"label": "Tìm sản phẩm", "action": "action:product_search"},
                {"label": "Xem giỏ hàng", "action": "action:view_cart"},
                {"label": "Kiểm tra đơn hàng", "action": "action:order_list"},
            ],
        }
        return suggestions.get(intent, suggestions["general"])