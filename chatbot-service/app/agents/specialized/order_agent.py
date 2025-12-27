from typing import Optional, Tuple, Dict, List
import re

from app.agents.specialized.base_agent import BaseAgent
from app.models.agent_types import ProcessedInput, IntentResult, ActionPlan, ToolResults
from app.agents.intent_classifier import _match_score

class OrderAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "order"

    def can_handle(self, intent_name: str) -> bool:
        return intent_name in ["order_tracking", "order_cancel", "order_return"]

    async def process(self, processed: ProcessedInput, intent: Optional[IntentResult] = None) -> Tuple[ActionPlan, Optional[ToolResults]]:
        if not intent:
            intent = self._classify_intent(processed)

        if intent.intent == "order_tracking":
            order_id = intent.entities.get("order_id")
            if not order_id:
                # If no order_id, list orders so user can choose
                return ActionPlan(tools=["order.list"], next_step="show_order_list"), None
            return ActionPlan(tools=["order.track"], next_step="show_order_status"), None
        
        elif intent.intent == "order_cancel":
            order_id = intent.entities.get("order_id")
            if not order_id:
                return ActionPlan(tools=[], required_data=["order_id"], next_step="ask_order_id_cancel"), None
            return ActionPlan(tools=["order.cancel"], next_step="confirm_cancel"), None

        elif intent.intent == "order_return":
            return ActionPlan(tools=[], next_step="response.policy_return"), None
            
        return ActionPlan(tools=[], next_step=None), None

    def _classify_intent(self, processed: ProcessedInput) -> IntentResult:
        text = processed.cleaned_text
        # In Order scope, almost everything is order tracking unless specified otherwise
        entities = {}
        match = re.search(r"(order_[\w]+|#\d+|\d{4,})", text)
        if match:
            entities["order_id"] = match.group(0).replace("#", "")
            
        return IntentResult(intent="order_tracking", confidence=1.0, entities=entities)
