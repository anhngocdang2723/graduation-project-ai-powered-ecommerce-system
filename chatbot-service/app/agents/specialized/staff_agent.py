from typing import Optional, Tuple, Dict, List
import re

from app.agents.specialized.base_agent import BaseAgent
from app.models.agent_types import ProcessedInput, IntentResult, ActionPlan, ToolResults
from app.agents.intent_classifier import _match_score, _extract_product_query

class StaffAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "staff"

    def can_handle(self, intent_name: str) -> bool:
        return intent_name in ["staff_check_stock", "staff_customer_lookup", "staff_order_history", "staff_create_order"]

    async def process(self, processed: ProcessedInput, intent: Optional[IntentResult] = None) -> Tuple[ActionPlan, Optional[ToolResults]]:
        # Permission Check
        # In a real app, we'd check specific roles. Here we assume 'staff' or 'admin' or 'manager'
        # For test simplicity, let's assume user_type must contain 'staff' or 'manager' or 'admin'
        # But our InputProcessor defaults to 'customer' or 'guest'.
        # We will need to simulate this in tests by setting user_type manually.
        allowed_roles = ["staff", "manager", "admin"]
        if processed.user_type not in allowed_roles:
             return ActionPlan(tools=[], required_data=[], next_step="deny_access"), None

        if not intent:
            intent = self._classify_intent(processed)

        if intent.intent == "staff_check_stock":
            query = intent.entities.get("product_query")
            if not query:
                return ActionPlan(tools=[], required_data=["product_query"], next_step="ask_product_for_stock"), None
            return ActionPlan(tools=["staff.check_stock"], next_step="show_stock_level"), None

        elif intent.intent == "staff_customer_lookup":
            query = intent.entities.get("customer_query")
            if not query:
                return ActionPlan(tools=[], required_data=["customer_query"], next_step="ask_customer_info"), None
            return ActionPlan(tools=["staff.customer_lookup"], next_step="show_customer_info"), None

        elif intent.intent == "staff_order_history":
            customer_id = intent.entities.get("customer_id")
            if not customer_id:
                 return ActionPlan(tools=[], required_data=["customer_id"], next_step="ask_customer_id_history"), None
            return ActionPlan(tools=["staff.order_history"], next_step="show_customer_order_history"), None

        elif intent.intent == "staff_create_order":
             return ActionPlan(tools=["staff.create_order"], next_step="start_create_order_flow"), None
            
        return ActionPlan(tools=[], next_step=None), None

    def _classify_intent(self, processed: ProcessedInput) -> IntentResult:
        text = processed.cleaned_text
        keywords = {
            "STAFF.CHECK_STOCK": ["check kho", "tồn kho", "kiểm kho", "số lượng tồn", "check stock", "inventory"],
            "STAFF.CUSTOMER_LOOKUP": ["tìm khách", "check info khách", "thông tin khách", "lookup customer", "find customer"]
        }
        
        scores = {k: _match_score(text, v) for k, v in keywords.items()}
        top_key = max(scores.items(), key=lambda kv: kv[1])[0] if scores else "STAFF.CHECK_STOCK"
        
        intent_map = {
            "STAFF.CHECK_STOCK": "staff_check_stock",
            "STAFF.CUSTOMER_LOOKUP": "staff_customer_lookup"
        }
        mapped = intent_map.get(top_key, "staff_check_stock")
        
        entities = {}
        q = _extract_product_query(text)
        if q:
            if mapped == "staff_check_stock":
                entities["product_query"] = q
            else:
                entities["customer_query"] = q
                
        return IntentResult(intent=mapped, confidence=1.0, entities=entities)
