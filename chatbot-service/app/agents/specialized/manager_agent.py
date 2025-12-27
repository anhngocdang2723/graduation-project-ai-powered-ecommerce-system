from typing import Optional, Tuple, Dict, List

from app.agents.specialized.base_agent import BaseAgent
from app.models.agent_types import ProcessedInput, IntentResult, ActionPlan, ToolResults

class ManagerAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "manager"

    def can_handle(self, intent_name: str) -> bool:
        return intent_name in ["manager_report_sales", "manager_report_chatbot", "manager_config_update"]

    async def process(self, processed: ProcessedInput, intent: Optional[IntentResult] = None) -> Tuple[ActionPlan, Optional[ToolResults]]:
        # Permission Check
        allowed_roles = ["manager", "admin"]
        if processed.user_type not in allowed_roles:
             return ActionPlan(tools=[], required_data=[], next_step="deny_access"), None

        if intent.intent == "manager_report_sales":
            return ActionPlan(tools=["report.sales"], next_step="show_sales_report"), None
        
        elif intent.intent == "manager_report_chatbot":
            return ActionPlan(tools=["report.chatbot_stats"], next_step="show_chatbot_stats"), None

        elif intent.intent == "manager_config_update":
            return ActionPlan(tools=["system.update_config"], next_step="confirm_config_update"), None

        return ActionPlan(tools=[], next_step=None), None
