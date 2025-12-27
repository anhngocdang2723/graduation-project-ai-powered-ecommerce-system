import asyncio
import pytest

from app import main as app_main
from app.models import ChatRequest, ProductInfo, ChatActionType
from app.models.agent_types import ToolResults


@pytest.fixture(autouse=True)
def _enable_agents(monkeypatch):
    """Ensure agent pipeline is enabled and DB access is bypassed."""
    monkeypatch.setattr(app_main, "AGENTS_ENABLED", True, raising=False)

    async def _fake_get_db_pool():
        return None

    monkeypatch.setattr(app_main, "get_db_pool", _fake_get_db_pool, raising=False)


def test_chat_agent_product_search_success(monkeypatch):
    """Pipeline returns enriched response when tool yields products."""

    async def _fake_search_products(query: str, limit: int = 10):
        products = [
            ProductInfo(
                id="prod_1",
                title="Áo thun basic đen",
                handle="ao-thun-basic-den",
                price=250000,
                currency_code="vnd",
                in_stock=True,
            ),
            ProductInfo(
                id="prod_2",
                title="Áo thun basic trắng",
                handle="ao-thun-basic-trang",
                price=255000,
                currency_code="vnd",
                in_stock=True,
            ),
        ]
        return ToolResults(ok=True, data=products, errors=[], timings_ms={"duration_ms": 5})

    monkeypatch.setattr("app.tools.product_tools.search_products", _fake_search_products)

    async def _run():
        req = ChatRequest(message="Tôi muốn tìm áo thun basic màu đen", session_id="sess_success", customer_id="cust_success", language="vi")
        return await app_main.chat_endpoint(req)

    resp = asyncio.run(_run())

    assert resp.intent == "product_inquiry"
    assert resp.products is not None and len(resp.products) == 2
    assert resp.actions and resp.actions[0].type == ChatActionType.SHOW_PRODUCTS.value
    assert "Tìm thấy" in resp.response


def test_chat_agent_product_search_no_results(monkeypatch):
    """Pipeline gracefully handles empty tool results."""

    async def _fake_search_products(query: str, limit: int = 10):
        return ToolResults(ok=True, data=[], errors=[], timings_ms={"duration_ms": 3})

    monkeypatch.setattr("app.tools.product_tools.search_products", _fake_search_products)

    async def _run():
        req = ChatRequest(message="Mình tìm áo khoác mùa đông", session_id="sess_empty", customer_id="cust_empty", language="vi")
        return await app_main.chat_endpoint(req)

    resp = asyncio.run(_run())

    assert resp.intent == "product_inquiry"
    assert resp.products is None
    assert resp.quick_replies and resp.quick_replies[0].label == "Tìm tiếp"
    assert "Không tìm thấy" in resp.response


def test_chat_agent_product_search_tool_error(monkeypatch):
    """Pipeline falls back to apology when tool fails."""

    async def _fake_search_products(query: str, limit: int = 10):
        return ToolResults(ok=False, data=None, errors=["timeout"], timings_ms={})

    monkeypatch.setattr("app.tools.product_tools.search_products", _fake_search_products)

    async def _run():
        req = ChatRequest(message="Tìm giày sneaker nam", session_id="sess_error", customer_id="cust_error", language="vi")
        return await app_main.chat_endpoint(req)

    resp = asyncio.run(_run())

    assert resp.intent == "product_inquiry"
    assert resp.products is None
    assert resp.quick_replies and resp.quick_replies[0].label == "Tìm tiếp"
    assert "Không tìm thấy" in resp.response
    assert resp.actions == []