"""
Chatbot schema models - map to chatbot.sessions, chatbot.messages, chatbot.settings
"""
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from enum import Enum


class SessionStatus(str, Enum):
    """Session status enum"""
    ACTIVE = "active"
    ENDED = "ended"
    ESCALATED = "escalated"


class MessageRole(str, Enum):
    """Message role enum"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatSession(BaseModel):
    """
    Map to chatbot.sessions table
    """
    id: str = Field(..., description="Primary key, format: chat_xxx")
    session_id: str = Field(..., description="Unique session identifier")
    customer_id: Optional[str] = Field(None, description="FK to public.customer.id (nullable for guests)")
    customer_email: Optional[str] = None
    customer_name: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    status: SessionStatus = Field(default=SessionStatus.ACTIVE)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "id": "chat_abc123",
                "session_id": "sess_xyz789",
                "customer_id": "cus_01H1234567",
                "customer_email": "user@example.com",
                "status": "active",
                "metadata": {"source": "web", "language": "vi"}
            }
        }


class ChatMessage(BaseModel):
    """
    Map to chatbot.messages table
    """
    id: str = Field(..., description="Primary key, format: msg_xxx")
    session_id: str = Field(..., description="FK to chatbot.sessions.session_id")
    role: MessageRole
    content: str = Field(..., description="Message text content")
    intent: Optional[str] = Field(None, description="Detected intent: product_inquiry, order_tracking, etc.")
    tokens_used: int = Field(default=0, description="Tokens consumed by LLM")
    response_time_ms: Optional[int] = Field(None, description="Response time in milliseconds")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Extra data: products, actions, etc.")
    created_at: Optional[datetime] = None
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "id": "msg_def456",
                "session_id": "sess_xyz789",
                "role": "user",
                "content": "Tôi muốn tìm áo thun",
                "intent": "product_inquiry",
                "tokens_used": 0,
                "metadata": {}
            }
        }


class ChatSetting(BaseModel):
    """
    Map to chatbot.settings table
    """
    id: str = Field(..., description="Primary key, format: setting_xxx")
    key: str = Field(..., description="Unique setting key")
    value: Any = Field(..., description="Setting value (JSONB)")
    description: Optional[str] = None
    updated_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "setting_001",
                "key": "enabled",
                "value": True,
                "description": "Enable/disable chatbot",
                "updated_by": "admin@example.com"
            }
        }


# ============================================
# DB Row to Pydantic converters
# ============================================

def session_from_db(row: Any) -> ChatSession:
    """Convert asyncpg.Record to ChatSession"""
    return ChatSession(
        id=row["id"],
        session_id=row["session_id"],
        customer_id=row.get("customer_id"),
        customer_email=row.get("customer_email"),
        customer_name=row.get("customer_name"),
        started_at=row.get("started_at"),
        ended_at=row.get("ended_at"),
        status=row.get("status", "active"),
        metadata=row.get("metadata", {}),
        created_at=row.get("created_at"),
        updated_at=row.get("updated_at"),
    )


def message_from_db(row: Any) -> ChatMessage:
    """Convert asyncpg.Record to ChatMessage"""
    return ChatMessage(
        id=row["id"],
        session_id=row["session_id"],
        role=row["role"],
        content=row["content"],
        intent=row.get("intent"),
        tokens_used=row.get("tokens_used", 0),
        response_time_ms=row.get("response_time_ms"),
        metadata=row.get("metadata", {}),
        created_at=row.get("created_at"),
    )


def setting_from_db(row: Any) -> ChatSetting:
    """Convert asyncpg.Record to ChatSetting"""
    return ChatSetting(
        id=row["id"],
        key=row["key"],
        value=row["value"],
        description=row.get("description"),
        updated_by=row.get("updated_by"),
        updated_at=row.get("updated_at"),
    )
