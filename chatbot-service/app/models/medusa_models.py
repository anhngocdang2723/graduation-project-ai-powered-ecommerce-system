"""
Medusa models - map to public.customer, product, order, cart, region
Simplified versions for chatbot use (not full Medusa objects)
"""
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class MedusaCustomer(BaseModel):
    """
    Simplified model for public.customer
    """
    id: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    has_account: bool = False
    metadata: Optional[dict[str, Any]] = None
    created_at: Optional[datetime] = None
    
    @property
    def full_name(self) -> str:
        """Get full name"""
        parts = [self.first_name, self.last_name]
        return " ".join(p for p in parts if p)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "cus_01H1234567",
                "email": "user@example.com",
                "first_name": "Nguyễn",
                "last_name": "Văn A",
                "has_account": True
            }
        }


class MedusaProductVariant(BaseModel):
    """
    Simplified model for public.product_variant
    """
    id: str
    title: str
    sku: Optional[str] = None
    allow_backorder: bool = False
    manage_inventory: bool = True
    product_id: Optional[str] = None
    calculated_price: Optional[dict[str, Any]] = None  # From Store API
    prices: Optional[list[dict[str, Any]]] = None # Raw prices
    inventory_quantity: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "variant_01H123",
                "title": "Size M",
                "sku": "TSHIRT-M",
                "calculated_price": {
                    "calculated_amount": 250000,
                    "currency_code": "vnd"
                },
                "inventory_quantity": 50
            }
        }


class MedusaProduct(BaseModel):
    """
    Simplified model for public.product
    """
    id: str
    title: str
    handle: str  # URL slug
    subtitle: Optional[str] = None
    description: Optional[str] = None
    thumbnail: Optional[str] = None
    status: str = "draft"  # draft | published
    variants: list[MedusaProductVariant] = Field(default_factory=list)
    metadata: Optional[dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "prod_01H123",
                "title": "Áo thun basic",
                "handle": "ao-thun-basic",
                "description": "Áo thun cotton 100%",
                "thumbnail": "https://example.com/img.jpg",
                "status": "published",
                "variants": []
            }
        }


class MedusaOrder(BaseModel):
    """
    Simplified model for public.order
    """
    id: str
    display_id: Optional[int] = None  # Human-readable order number
    customer_id: Optional[str] = None
    email: Optional[str] = None
    status: str  # pending | completed | canceled
    currency_code: str
    total: Optional[int] = None  # In cents
    region_id: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None
    created_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "order_01H123",
                "display_id": 1001,
                "email": "user@example.com",
                "status": "completed",
                "currency_code": "vnd",
                "total": 500000
            }
        }


class MedusaCart(BaseModel):
    """
    Simplified model for public.cart
    """
    id: str
    customer_id: Optional[str] = None
    email: Optional[str] = None
    region_id: Optional[str] = None
    currency_code: str
    total: Optional[int] = None  # In cents
    items: list[dict[str, Any]] = Field(default_factory=list)
    completed_at: Optional[datetime] = None
    metadata: Optional[dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "cart_01H123",
                "region_id": "reg_01H456",
                "currency_code": "vnd",
                "total": 250000,
                "items": []
            }
        }


class MedusaRegion(BaseModel):
    """
    Simplified model for public.region
    """
    id: str
    name: str
    currency_code: str
    automatic_taxes: bool = True
    metadata: Optional[dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "reg_01H123",
                "name": "Vietnam",
                "currency_code": "vnd",
                "automatic_taxes": True
            }
        }


# ============================================
# API Response to Pydantic converters
# ============================================

def product_from_api(data: dict[str, Any]) -> MedusaProduct:
    """Convert Medusa Store API product response to MedusaProduct"""
    variants = [
        MedusaProductVariant(
            id=v["id"],
            title=v.get("title", ""),
            sku=v.get("sku"),
            allow_backorder=v.get("allow_backorder", False),
            manage_inventory=v.get("manage_inventory", True),
            product_id=v.get("product_id"),
            calculated_price=v.get("calculated_price"),
            inventory_quantity=v.get("inventory_quantity"),
        )
        for v in data.get("variants", [])
    ]
    
    return MedusaProduct(
        id=data["id"],
        title=data["title"],
        handle=data["handle"],
        subtitle=data.get("subtitle"),
        description=data.get("description"),
        thumbnail=data.get("thumbnail"),
        status=data.get("status", "draft"),
        variants=variants,
        metadata=data.get("metadata"),
    )


def order_from_api(data: dict[str, Any]) -> MedusaOrder:
    """Convert Medusa Store API order response to MedusaOrder"""
    return MedusaOrder(
        id=data["id"],
        display_id=data.get("display_id"),
        customer_id=data.get("customer_id"),
        email=data.get("email"),
        status=data["status"],
        currency_code=data["currency_code"],
        total=data.get("total"),
        region_id=data.get("region_id"),
        metadata=data.get("metadata"),
        created_at=data.get("created_at"),
    )


def cart_from_api(data: dict[str, Any]) -> MedusaCart:
    """Convert Medusa Store API cart response to MedusaCart"""
    return MedusaCart(
        id=data["id"],
        customer_id=data.get("customer_id"),
        email=data.get("email"),
        region_id=data.get("region_id"),
        currency_code=data["currency_code"],
        total=data.get("total"),
        items=data.get("items", []),
        completed_at=data.get("completed_at"),
        metadata=data.get("metadata"),
    )


def region_from_api(data: dict[str, Any]) -> MedusaRegion:
    """Convert Medusa Store API region response to MedusaRegion"""
    return MedusaRegion(
        id=data["id"],
        name=data["name"],
        currency_code=data["currency_code"],
        automatic_taxes=data.get("automatic_taxes", True),
        metadata=data.get("metadata"),
    )
