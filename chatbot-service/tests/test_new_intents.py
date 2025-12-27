import asyncio
import pytest
from unittest.mock import AsyncMock

from app import main as app_main
from app.models import ChatRequest
from app.models.agent_types import ToolResults

@pytest.fixture(autouse=True)
def _enable_agents(monkeypatch):
    """Ensure agent pipeline is enabled and DB access is bypassed."""
    monkeypatch.setattr(app_main, "AGENTS_ENABLED", True, raising=False)

    async def _fake_get_db_pool():
        return None

    monkeypatch.setattr(app_main, "get_db_pool", _fake_get_db_pool, raising=False)

def test_order_tracking_success(monkeypatch):
    """Test order tracking flow."""
    
    async def _fake_lookup_order(order_id: str):
        return ToolResults(
            ok=True, 
            data={"id": order_id, "display_id": 1001, "status": "shipped", "total": 500000}, 
            errors=[], 
            timings_ms={}
        )

    monkeypatch.setattr("app.tools.order_tools.lookup_order", _fake_lookup_order)

    async def _run():
        req = ChatRequest(message="Kiểm tra đơn hàng #1001", session_id="sess_order", customer_id="cust_1", language="vi")
        return await app_main.chat_endpoint(req)

    resp = asyncio.run(_run())
    
    assert resp.intent == "order_tracking"
    assert "1001" in resp.response
    assert "shipped" in resp.response

def test_cart_view_success(monkeypatch):
    """Test cart view flow."""
    
    async def _fake_view_cart(cart_id: str = None):
        return ToolResults(
            ok=True, 
            data={"id": "cart_1", "items": [{"id": "item_1"}, {"id": "item_2"}]}, 
            errors=[], 
            timings_ms={}
        )

    monkeypatch.setattr("app.tools.cart_tools.view_cart", _fake_view_cart)

    async def _run():
        req = ChatRequest(message="Xem giỏ hàng", session_id="sess_cart", customer_id="cust_1", language="vi")
        return await app_main.chat_endpoint(req)

    resp = asyncio.run(_run())
    
    assert resp.intent == "cart_view"
    assert "2 sản phẩm" in resp.response
