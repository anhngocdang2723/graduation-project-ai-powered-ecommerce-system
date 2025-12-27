import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.medusa_client import MedusaClient
from app.tools.cart_tools import view_cart, add_to_cart
from app.tools.product_tools import search_products

async def test_cart_flow():
    print("--- STARTING MANUAL SYSTEM TEST ---")
    
    # 1. Test Connection & Product Search (to get a variant)
    print("\n1. Searching for products to get a Variant ID...")
    search_res = await search_products(query="", limit=1)
    
    if not search_res.ok or not search_res.data:
        print("❌ Failed to find any products. Cannot test Add to Cart.")
        print(f"Error: {search_res.errors}")
        return

    product = search_res.data[0]
    print(f"✅ Found product: {product.title} (ID: {product.id})")
    
    # We need a variant ID. 
    # Note: product_to_info might have stripped variants. Let's check.
    # If product_to_info returns a Pydantic model or dict, we need to access it correctly.
    # In product_tools.py, it returns a list of ProductInfo objects (Pydantic models) or dicts?
    # Let's check product_tools.py again. It calls product_to_info.
    # Let's assume for this test we might need to fetch the raw product if variants are missing.
    
    # Actually, let's just use the client directly to get raw product data to be sure we have a variant.
    client = MedusaClient()
    raw_product = await client.get_product(product.id)
    if not raw_product or not raw_product.get("variants"):
        print("❌ Product has no variants.")
        return

    variant_id = raw_product["variants"][0]["id"]
    print(f"✅ Using Variant ID: {variant_id}")

    # 2. Test View Cart (No ID -> Create New)
    print("\n2. Testing View Cart (No ID)...")
    cart_res = await view_cart(cart_id=None)
    
    if not cart_res.ok:
        print(f"❌ Failed to create/view cart: {cart_res.errors}")
        return
    
    cart = cart_res.data
    cart_id = cart.get("id")
    print(f"✅ Cart Created/Retrieved. ID: {cart_id}")
    print(f"   Items: {len(cart.get('items', []))}")

    # 3. Test Add to Cart
    print(f"\n3. Testing Add to Cart (Variant: {variant_id})...")
    add_res = await add_to_cart(cart_id=cart_id, variant_id=variant_id, quantity=1)
    
    if not add_res.ok:
        print(f"❌ Failed to add to cart: {add_res.errors}")
    else:
        print("✅ Item added successfully.")
        updated_cart = add_res.data
        print(f"   Items in cart: {len(updated_cart.get('items', []))}")

    # 4. Test View Cart (With ID)
    print(f"\n4. Testing View Cart (ID: {cart_id})...")
    view_res = await view_cart(cart_id=cart_id)
    
    if not view_res.ok:
        print(f"❌ Failed to view cart: {view_res.errors}")
    else:
        final_cart = view_res.data
        items = final_cart.get("items", [])
        print(f"✅ Cart retrieved successfully.")
        print(f"   Total Items: {len(items)}")
        for item in items:
            print(f"   - {item.get('title')} (Qty: {item.get('quantity')})")

    print("\n--- TEST COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(test_cart_flow())
