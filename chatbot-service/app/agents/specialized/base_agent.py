from abc import ABC, abstractmethod
from typing import Optional, Tuple

from app.models.agent_types import ProcessedInput, IntentResult, ActionPlan, ToolResults

class BaseAgent(ABC):
    """
    Abstract base class for specialized agents.
    Each agent is responsible for a specific domain (Sales, Order, Staff, etc.)
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the agent (e.g., 'sales', 'staff')"""
        pass

    @abstractmethod
    async def process(self, processed: ProcessedInput, intent: Optional[IntentResult] = None) -> Tuple[ActionPlan, Optional[ToolResults]]:
        """
        Process the input within the agent's scope.
        If intent is provided (from global NLU), use it.
        Otherwise, perform scoped NLU.
        """
        pass
    
    @abstractmethod
    def can_handle(self, intent_name: str) -> bool:
        """Check if this agent can handle a specific global intent"""
        pass
