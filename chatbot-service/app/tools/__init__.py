"""Tools package for Medusa API wrappers."""

from .product_tools import search_products, get_product_details
from .order_tools import lookup_order, cancel_order
from .staff_tools import check_stock, lookup_customer, get_customer_order_history, create_draft_order
from .report_tools import get_sales_report, get_chatbot_stats
from .product_recommend_tool import recommend_products
from .cart_tools import view_cart, add_to_cart, remove_from_cart
from .system_tools import update_config

__all__ = [
    "search_products",
    "get_product_details",
    "lookup_order",
    "cancel_order",
    "check_stock",
    "lookup_customer",
    "get_customer_order_history",
    "create_draft_order",
    "get_sales_report",
    "get_chatbot_stats",
    "recommend_products",
    "view_cart",
    "add_to_cart",
    "remove_from_cart",
    "update_config",
]
