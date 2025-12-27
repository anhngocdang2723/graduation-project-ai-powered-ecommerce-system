"""
Pydantic models for chatbot service
"""

from .chatbot_models import (
    ChatSession,
    ChatMessage,
    ChatSetting,
    SessionStatus,
    MessageRole,
)

from .medusa_models import (
    MedusaCustomer,
    MedusaProduct,
    MedusaProductVariant,
    MedusaOrder,
    MedusaCart,
    MedusaRegion,
)

from .api_models import (
    ChatRequest,
    ChatResponse,
    ProductInfo,
    QuickReply,
    ChatAction,
    ChatActionType,
    ContextSuggestionRequest,
    ContextSuggestionResponse,
    ContextNodeDTO,
    product_to_info,
    create_quick_reply,
    create_action,
)

__all__ = [
    # Chatbot models
    "ChatSession",
    "ChatMessage",
    "ChatSetting",
    "SessionStatus",
    "MessageRole",
    
    # Medusa models
    "MedusaCustomer",
    "MedusaProduct",
    "MedusaProductVariant",
    "MedusaOrder",
    "MedusaCart",
    "MedusaRegion",
    
    # API models
    "ChatRequest",
    "ChatResponse",
    "ProductInfo",
    "QuickReply",
    "ChatAction",
    "ChatActionType",
    "ContextSuggestionRequest",
    "ContextSuggestionResponse",
    "ContextNodeDTO",
    
    # Helpers
    "product_to_info",
    "create_quick_reply",
    "create_action",
]
