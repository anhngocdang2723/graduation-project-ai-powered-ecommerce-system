import httpx
from typing import Optional, Dict, Any, List
from app.config import MEDUSA_BACKEND_URL, MEDUSA_PUBLISHABLE_KEY, MEDUSA_ADMIN_TOKEN

class MedusaClient:
    """
    Client for interacting with the Medusa Store API.
    """
    def __init__(self, base_url: str = MEDUSA_BACKEND_URL, api_key: Optional[str] = MEDUSA_PUBLISHABLE_KEY, admin_token: str = MEDUSA_ADMIN_TOKEN):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Content-Type": "application/json",
        }
        if api_key:
            self.headers["x-publishable-api-key"] = api_key
        self.admin_token = admin_token

    async def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Internal method to perform GET requests to Store API.
        """
        url = f"{self.base_url}{endpoint}"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers, params=params, timeout=10.0)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                print(f"HTTP error occurred: {e}")
                return {"error": str(e), "status_code": e.response.status_code}
            except httpx.RequestError as e:
                print(f"Request error occurred: {e}")
                return {"error": str(e)}

    async def _get_admin(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Internal method to perform GET requests to Admin API.
        """
        url = f"{self.base_url}/admin{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.admin_token}"
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers, params=params, timeout=10.0)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                print(f"Admin HTTP error: {e}")
                return {"error": str(e), "status_code": e.response.status_code}
            except httpx.RequestError as e:
                print(f"Admin Request error: {e}")
                return {"error": str(e)}

    async def _post(self, endpoint: str, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal method to perform POST requests.
        """
        url = f"{self.base_url}{endpoint}"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=self.headers, json=json_data, timeout=10.0)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                print(f"HTTP error occurred: {e}")
                try:
                    err_json = e.response.json()
                    msg = err_json.get("message", str(e))
                except:
                    msg = e.response.text or str(e)
                return {"error": msg, "status_code": e.response.status_code}
            except httpx.RequestError as e:
                print(f"Request error occurred: {e}")
                return {"error": str(e)}

    async def search_products(self, query: str, limit: int = 5, region_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for products using the Medusa Store API.
        """
        endpoint = "/store/products"
        params = {
            "q": query,
            "limit": limit,
            # "fields": "id,title,description,handle,thumbnail,variants" # Optional: limit fields
        }
        if region_id:
            params["region_id"] = region_id
            
        # Try to get prices by using cart_id if available, or region_id?
        # Medusa Store API usually returns prices if a region_id or currency_code is provided in context?
        # But we got 400 Bad Request when passing currency_code.
        
        data = await self._get(endpoint, params)
        if "products" in data:
            return data["products"]
        return []

    async def get_product(self, product_id: str, region_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get a single product by ID.
        """
        endpoint = f"/store/products/{product_id}"
        params = {}
        if region_id:
            params["region_id"] = region_id
        data = await self._get(endpoint, params)
        return data.get("product")

    async def get_collections(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get product collections.
        """
        endpoint = "/store/collections"
        params = {"limit": limit}
        data = await self._get(endpoint, params)
        return data.get("collections", [])

    async def get_regions(self) -> List[Dict[str, Any]]:
        """
        Get regions.
        """
        endpoint = "/store/regions"
        data = await self._get(endpoint)
        return data.get("regions", [])

    async def get_order(self, order_id: str) -> Dict[str, Any]:
        """
        Get an order by ID using Admin API to ensure we get details.
        """
        # Try Admin API first for full details
        endpoint = f"/orders/{order_id}"
        params = {"fields": "+items.*,+shipping_address.*,+currency_code"}
        data = await self._get_admin(endpoint, params)
        
        if "order" in data:
            return data["order"]
            
        # Fallback to Store API if Admin fails (though unlikely with correct token)
        endpoint = f"/store/orders/{order_id}"
        data = await self._get(endpoint)
        if "order" in data:
            return data["order"]
        return data

    async def list_orders(self, limit: int = 5, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List recent orders using Admin API.
        """
        endpoint = "/orders"
        params = {
            "limit": limit,
            "offset": offset,
            "fields": "id,display_id,status,total,currency_code,created_at,items.*"
        }
        data = await self._get_admin(endpoint, params)
        return data.get("orders", [])

    async def create_cart(self) -> Dict[str, Any]:
        """
        Create a new cart.
        """
        endpoint = "/store/carts"
        data = await self._post(endpoint, {})
        if "cart" in data:
            return data["cart"]
        return data

    async def get_cart(self, cart_id: str) -> Dict[str, Any]:
        """
        Get a cart by ID.
        """
        endpoint = f"/store/carts/{cart_id}"
        data = await self._get(endpoint)
        if "cart" in data:
            return data["cart"]
        return data

    async def add_line_item(self, cart_id: str, variant_id: str, quantity: int) -> Dict[str, Any]:
        """
        Add an item to the cart.
        """
        endpoint = f"/store/carts/{cart_id}/line-items"
        payload = {"variant_id": variant_id, "quantity": quantity}
        data = await self._post(endpoint, payload)
        if "cart" in data:
            return data["cart"]
        return data

    async def get_shipping_options(self, cart_id: str) -> List[Dict[str, Any]]:
        """
        Get shipping options for a cart.
        """
        endpoint = f"/store/shipping-options/{cart_id}"
        data = await self._get(endpoint)
        return data.get("shipping_options", [])

    async def add_shipping_method(self, cart_id: str, option_id: str) -> Dict[str, Any]:
        """
        Add a shipping method to the cart.
        """
        endpoint = f"/store/carts/{cart_id}/shipping-methods"
        payload = {"option_id": option_id}
        data = await self._post(endpoint, payload)
        if "cart" in data:
            return data["cart"]
        return data
