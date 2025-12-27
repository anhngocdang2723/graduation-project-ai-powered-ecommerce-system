from typing import Protocol, runtime_checkable, Any, Dict


class AgentError(Exception):
    """Base exception for agent errors"""


@runtime_checkable
class Agent(Protocol):
    async def run(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent logic with provided context and return a dict payload.
        Implementations should avoid side effects and raise AgentError on failure.
        """
        ...
