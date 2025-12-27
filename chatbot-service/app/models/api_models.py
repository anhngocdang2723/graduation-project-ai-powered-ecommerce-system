from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from enum import Enum
from .medusa_models import MedusaProduct

class ChatActionType(str, Enum):
    NAVIGATE = "navigate"
    API_CALL = "api_call"
    FORM = "form"
    SHOW_PRODUCTS = "show_products"
    REQUEST_ORDER_INFO = "request_order_info"
    GUIDE_TO_CART = "guide_to_cart"
    NONE = "none"

class ChatAction(BaseModel):
    type: ChatActionType = ChatActionType.NONE
    payload: Dict[str, Any] = Field(default_factory=dict)

class QuickReply(BaseModel):
    label: str
    value: str
    metadata: Optional[Dict[str, Any]] = None

class ProductVariantInfo(BaseModel):
    id: str
    title: str
    price: Optional[str] = None
    currency_code: Optional[str] = None

class ProductInfo(BaseModel):
    id: str
    title: str
    handle: str
    thumbnail: Optional[str] = None
    price: Optional[str] = None
    currency_code: Optional[str] = None
    variants: List[ProductVariantInfo] = Field(default_factory=list)
    
class ChatRequest(BaseModel):
    message: str
    session_id: str
    customer_id: Optional[str] = None
    tag: Optional[str] = None
    language: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ChatResponse(BaseModel):
    response: str
    session_id: str
    products: List[ProductInfo] = Field(default_factory=list)
    quick_replies: List[QuickReply] = Field(default_factory=list)
    action: Optional[ChatAction] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ContextNodeDTO(BaseModel):
    id: str
    label: str
    tag: Optional[str] = None
    type: str = "group"
    value: Optional[str] = None
    children: Optional[List['ContextNodeDTO']] = Field(default_factory=list)

class ContextSuggestionRequest(BaseModel):
    user_type: str = "guest"
    tag: Optional[str] = None
    customer_id: Optional[str] = None
    intent: Optional[str] = None

class ContextSuggestionResponse(BaseModel):
    suggestions: List[ContextNodeDTO]

def product_to_info(product: MedusaProduct) -> ProductInfo:
    # Logic to convert MedusaProduct to ProductInfo
    price = None
    currency = None
    variants_info = []

    if product.variants:
        for v in product.variants:
            v_price = None
            v_currency = None
            if v.calculated_price:
                calc = v.calculated_price
                amount = calc.get("calculated_amount")
                v_currency = calc.get("currency_code", "vnd").upper()
                if amount is not None:
                    # Format VND currency without decimals
                    if v_currency.upper() == "VND":
                        v_price = f"{int(amount):,}₫"
                    else:
                        v_price = f"{amount:,.2f} {v_currency}"
            elif v.prices and len(v.prices) > 0:
                p = v.prices[0]
                amount = p.get("amount")
                v_currency = p.get("currency_code", "vnd").upper()
                if amount is not None:
                    # Format VND currency without decimals
                    if v_currency.upper() == "VND":
                        v_price = f"{int(amount):,}₫"
                    else:
                        v_price = f"{amount:,.2f} {v_currency}"
            
            variants_info.append(ProductVariantInfo(
                id=v.id,
                title=v.title,
                price=v_price,
                currency_code=v_currency
            ))

    # Use first variant for main price display
    if variants_info:
        price = variants_info[0].price
        currency = variants_info[0].currency_code

    return ProductInfo(
        id=product.id,
        title=product.title,
        handle=product.handle,
        thumbnail=product.thumbnail,
        price=price,
        currency_code=currency,
        variants=variants_info
    )

def create_quick_reply(label: str, value: str, metadata: Optional[Dict] = None) -> QuickReply:
    return QuickReply(label=label, value=value, metadata=metadata)

def create_action(type: ChatActionType, payload: Dict) -> ChatAction:
    return ChatAction(type=type, payload=payload)
