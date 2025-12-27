from typing import Optional, Tuple, Dict, List
import re

from app.agents.specialized.base_agent import BaseAgent
from app.models.agent_types import ProcessedInput, IntentResult, ActionPlan, ToolResults
from app.agents.intent_classifier import _match_score, _extract_product_query

class SalesAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "sales"

    def can_handle(self, intent_name: str) -> bool:
        return intent_name in [
            "product_inquiry", "product_detail", "product_recommend",
            "cart_view", "cart_add", "cart_remove",
            "account_login", "account_register",
            "faq_shipping", "faq_payment",
            "general"
        ]

    async def process(self, processed: ProcessedInput, intent: Optional[IntentResult] = None) -> Tuple[ActionPlan, Optional[ToolResults]]:
        if not intent:
            intent = self._classify_intent(processed)

        if intent.intent == "product_inquiry":
            query = intent.entities.get("product_query")
            if not query:
                # If no query extracted, maybe ask user? Or just search everything?
                # For now, let's assume we need a query.
                # But if user just says "tìm sản phẩm", we might want to ask "Bạn tìm gì?"
                # Let's try to search with empty query (might return featured) or ask.
                return ActionPlan(tools=[], required_data=["product_query"], next_step="ask_product_query"), None
            return ActionPlan(tools=["product.search"], next_step="show_product_list"), None

        elif intent.intent == "product_detail":
            # Need product_id or handle. If not present, check context for last products
            product_id = intent.entities.get("product_id")
            
            # If no product_id but we have context from previous search, use first product
            if not product_id and processed.session_ctx.last_product_ids:
                product_id = processed.session_ctx.last_product_ids[0]
                intent.entities["product_id"] = product_id
                print(f"[SalesAgent] Using context product_id: {product_id}")
            
            # Always return product.detail tool - executor will handle fallback search if no product_id
            return ActionPlan(tools=["product.detail"], next_step="show_product_detail"), None

        elif intent.intent == "product_recommend":
            return ActionPlan(tools=["product.recommend"], next_step="show_recommendations"), None

        elif intent.intent == "cart_view":
            return ActionPlan(tools=["cart.view"], next_step="show_cart"), None

        elif intent.intent == "cart_add":
            # Need product_id and variant_id
            product_id = intent.entities.get("product_id")
            variant_id = intent.entities.get("variant_id")
            
            # Context-aware: if user says "thêm vào giỏ" right after seeing products
            if not product_id and processed.session_ctx.last_product_ids:
                # Use the first product from context
                product_id = processed.session_ctx.last_product_ids[0]
                intent.entities["product_id"] = product_id
                print(f"[SalesAgent] Context-aware cart_add: using product_id={product_id}")
            
            if not product_id or not variant_id:
                 return ActionPlan(tools=[], required_data=["product_id", "variant_id"], next_step="ask_product_to_add"), None
            return ActionPlan(tools=["cart.add"], next_step="confirm_add_to_cart"), None
            
        elif intent.intent == "cart_remove":
             return ActionPlan(tools=["cart.remove"], next_step="confirm_remove_from_cart"), None

        elif intent.intent == "account_login":
            return ActionPlan(tools=[], next_step="response.login_link"), None
            
        elif intent.intent == "account_register":
            return ActionPlan(tools=[], next_step="response.register_link"), None

        elif intent.intent == "faq_shipping":
            return ActionPlan(tools=[], next_step="response.faq_shipping"), None
            
        elif intent.intent == "faq_payment":
            return ActionPlan(tools=[], next_step="response.faq_payment"), None

        elif intent.intent == "general":
             return ActionPlan(tools=[], next_step="response.greet"), None

        return ActionPlan(tools=[], next_step=None), None

    def _classify_intent(self, processed: ProcessedInput) -> IntentResult:
        # Simple fallback classification if global NLU failed or wasn't used
        # This duplicates some logic from global classifier but scoped to sales
        text = processed.cleaned_text
        
        # ... (Simplified for brevity, relying on global intent mostly)
        return IntentResult(intent="general", confidence=0.5)
