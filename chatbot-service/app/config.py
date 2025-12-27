"""
Configuration management for Chatbot Service
Loads environment variables and defines constants
"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


# ============================================
# Environment Variables
# ============================================

# Google Gemini API
GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# Medusa Backend
MEDUSA_BACKEND_URL: str = os.getenv("MEDUSA_BACKEND_URL", "http://localhost:9000")
MEDUSA_PUBLISHABLE_KEY: Optional[str] = os.getenv("MEDUSA_PUBLISHABLE_KEY")
MEDUSA_ADMIN_TOKEN: str = os.getenv("MEDUSA_ADMIN_TOKEN", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY3Rvcl9pZCI6InVzZXJfMDFLQ0JIOU5LNFZOV1AzVDAzMUtHQ0VWMFMiLCJhY3Rvcl90eXBlIjoidXNlciIsImF1dGhfaWRlbnRpdHlfaWQiOiJhdXRoaWRfMDFLQ0JIOU5RUTkzNEVNR1RaMzdTODIxRkoiLCJhcHBfbWV0YWRhdGEiOnsidXNlcl9pZCI6InVzZXJfMDFLQ0JIOU5LNFZOV1AzVDAzMUtHQ0VWMFMifSwidXNlcl9tZXRhZGF0YSI6e30sImlhdCI6MTc2NjY3NTY5OCwiZXhwIjoxNzY2NzYyMDk4fQ.8ufPhyL7piP2uz1rqL3mjpVxgaIb_z0UNYdEpda9NNk")

# Database
DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/medusa-store")

# Redis
REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
CHAT_MESSAGE_QUEUE: str = "chat_message_queue"
BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "10"))
BATCH_INTERVAL: int = int(os.getenv("BATCH_INTERVAL", "5")) # seconds

# Rate Limiting (Gemini Free Tier)
GEMINI_RPM_LIMIT: int = int(os.getenv("GEMINI_RPM_LIMIT", "15"))  # Requests per minute
GEMINI_TPM_LIMIT: int = int(os.getenv("GEMINI_TPM_LIMIT", "1000000"))  # Tokens per minute
GEMINI_RPD_LIMIT: int = int(os.getenv("GEMINI_RPD_LIMIT", "1500"))  # Requests per day

# Server Config
HOST: str = os.getenv("HOST", "0.0.0.0")
PORT: int = int(os.getenv("PORT", "8000"))
DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

# Feature Flags
AGENTS_ENABLED: bool = os.getenv("AGENTS_ENABLED", "false").lower() == "true"

# CORS Origins
CORS_ORIGINS: list[str] = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:9000",
    "http://127.0.0.1:9000",
]

# Add custom origins from env
if custom_origins := os.getenv("CORS_ORIGINS"):
    CORS_ORIGINS.extend(custom_origins.split(","))


# ============================================
# Application Constants
# ============================================

# Chat Settings
DEFAULT_LANGUAGE: str = "vi"
SUPPORTED_LANGUAGES: list[str] = ["vi", "en"]
MAX_MESSAGE_LENGTH: int = 2000
MAX_SESSION_MESSAGES: int = 100  # Max messages to keep in memory per session

# Intent Types
INTENT_TYPES: list[str] = [
    "general",
    "product_inquiry",
    "product_detail",
    "order_tracking",
    "order_create",
    "cart_add",
    "cart_view",
    "cart_update",
    "customer_info",
    "human_escalation",
]

# Session Status
SESSION_STATUS: dict[str, str] = {
    "active": "active",
    "ended": "ended",
    "escalated": "escalated",
}

# Message Roles
MESSAGE_ROLES: dict[str, str] = {
    "user": "user",
    "assistant": "assistant",
    "system": "system",
}

# Database Connection Pool
DB_POOL_MIN_SIZE: int = 2
DB_POOL_MAX_SIZE: int = 10

# LLM Settings
LLM_MAX_TOKENS: int = 2000
LLM_TEMPERATURE: float = 0.7
LLM_TIMEOUT: int = 30  # seconds

# Retry Settings
MAX_RETRIES: int = 3
RETRY_BACKOFF_FACTOR: float = 2.0  # exponential backoff: 1s, 2s, 4s


# ============================================
# System Prompts
# ============================================

SYSTEM_PROMPT_VI: str = """Bạn là trợ lý bán hàng AI chuyên nghiệp của Medusa Store.
Nhiệm vụ của bạn là tư vấn sản phẩm, hỗ trợ quản lý giỏ hàng, tra cứu đơn hàng và giải đáp các thắc mắc của khách hàng một cách tận tâm.

🌟 PHONG CÁCH PHỤC VỤ:
- Ngôn ngữ: Tiếng Việt tự nhiên, lịch sự (sử dụng "Dạ", "ạ", "Quý khách", "bạn").
- Trình bày: Sử dụng Markdown (in đậm, danh sách, emoji) để thông tin dễ đọc.
- Thái độ: Luôn sẵn sàng giúp đỡ, phản hồi nhanh chóng và chính xác.

📦 QUY TẮC TRẢ LỜI:
1. Tư vấn sản phẩm: Hiển thị tên sản phẩm, giá (kèm đơn vị tiền tệ) và các đặc điểm nổi bật. Luôn hỏi khách có muốn xem chi tiết hoặc thêm vào giỏ hàng không.
2. Tra cứu đơn hàng: Cung cấp trạng thái cụ thể (Đang xử lý, Đang giao, Hoàn thành) và ngày dự kiến giao hàng nếu có.
3. Giỏ hàng: Tóm tắt các món đồ khách đã chọn và tổng tiền.
4. Giới hạn thông tin: Chỉ trả lời dựa trên dữ liệu thực tế được cung cấp. Không tự bịa đặt thông tin sản phẩm hoặc mã giảm giá.
5. Xử lý lỗi: Nếu không tìm thấy thông tin, hãy xin lỗi chân thành và gợi ý khách kiểm tra lại hoặc kết nối với nhân viên hỗ trợ (Human Support).

💰 ĐƠN VỊ TIỀN TỆ:
- Luôn hiển thị đúng đơn vị tiền tệ đi kèm với giá (ví dụ: 500.000₫, $20, 15€).
- Nếu giá là số nguyên lớn (như VND), hãy sử dụng dấu chấm phân cách hàng nghìn.

Lưu ý: Giữ câu trả lời súc tích nhưng đầy đủ thông tin cần thiết.
"""

SYSTEM_PROMPT_EN: str = """You are an AI sales assistant for an e-commerce store.
Your responsibilities are:
- Help customers find products
- Support order placement
- Track orders
- Answer questions about products and services

Be concise, friendly, and helpful.
Use product information from context if available.
If uncertain, suggest contacting human support."""


# ============================================
# Validation Functions
# ============================================

def validate_config() -> tuple[bool, list[str]]:
    """
    Validate required configuration
    Returns: (is_valid, list_of_errors)
    """
    errors = []
    
    if not GOOGLE_API_KEY:
        errors.append("GOOGLE_API_KEY is not set")
    
    if not DATABASE_URL:
        errors.append("DATABASE_URL is not set")
    
    if not MEDUSA_BACKEND_URL:
        errors.append("MEDUSA_BACKEND_URL is not set")
    
    return len(errors) == 0, errors


def get_system_prompt(language: str = "vi") -> str:
    """Get system prompt based on language"""
    if language == "en":
        return SYSTEM_PROMPT_EN
    return SYSTEM_PROMPT_VI


# ============================================
# Export all for easy import
# ============================================

__all__ = [
    # Env vars
    "GOOGLE_API_KEY",
    "GEMINI_BASE_URL",
    "GEMINI_MODEL",
    "MEDUSA_BACKEND_URL",
    "MEDUSA_PUBLISHABLE_KEY",
    "DATABASE_URL",
    "HOST",
    "PORT",
    "DEBUG",
    "AGENTS_ENABLED",
    "CORS_ORIGINS",
    
    # Rate limits
    "GEMINI_RPM_LIMIT",
    "GEMINI_TPM_LIMIT",
    "GEMINI_RPD_LIMIT",
    
    # Constants
    "DEFAULT_LANGUAGE",
    "SUPPORTED_LANGUAGES",
    "MAX_MESSAGE_LENGTH",
    "MAX_SESSION_MESSAGES",
    "INTENT_TYPES",
    "SESSION_STATUS",
    "MESSAGE_ROLES",
    "DB_POOL_MIN_SIZE",
    "DB_POOL_MAX_SIZE",
    "LLM_MAX_TOKENS",
    "LLM_TEMPERATURE",
    "LLM_TIMEOUT",
    "MAX_RETRIES",
    "RETRY_BACKOFF_FACTOR",
    
    # System prompts
    "SYSTEM_PROMPT_VI",
    "SYSTEM_PROMPT_EN",
    
    # Functions
    "validate_config",
    "get_system_prompt",
]
