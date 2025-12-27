from typing import Any, Optional, Dict, List
from pydantic import BaseModel, Field


class SessionContext(BaseModel):
    last_messages: List[Dict[str, Any]] = Field(default_factory=list)
    cart_id: Optional[str] = None
    last_product_ids: List[str] = Field(default_factory=list)


class ProcessedInput(BaseModel):
    session_id: str
    customer_id: Optional[str] = None
    text: str
    cleaned_text: str
    language: str = "vi"  # "vi" | "en"
    user_type: str = "guest"  # "guest" | "customer"
    tag: Optional[str] = None
    session_ctx: SessionContext = Field(default_factory=SessionContext)


class IntentResult(BaseModel):
    intent: str
    sub_intent: Optional[str] = None
    confidence: float = 0.0
    entities: Dict[str, Any] = Field(default_factory=dict)


class ActionPlan(BaseModel):
    tools: List[str] = Field(default_factory=list)
    required_data: List[str] = Field(default_factory=list)
    next_step: Optional[str] = None
    escalate: bool = False


class ToolResults(BaseModel):
    ok: bool
    data: Any = None
    errors: List[str] = Field(default_factory=list)
    timings_ms: Dict[str, int] = Field(default_factory=dict)
