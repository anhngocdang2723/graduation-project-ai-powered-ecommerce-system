from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.services.medusa_client import MedusaClient
from app.models.agent_types import ToolResults

class BaseTool(ABC):
    """
    Base class for all tools.
    """
    def __init__(self, client: Optional[MedusaClient] = None):
        self.client = client or MedusaClient()

    @abstractmethod
    async def run(self, **kwargs) -> ToolResults:
        """
        Execute the tool logic.
        """
        pass
