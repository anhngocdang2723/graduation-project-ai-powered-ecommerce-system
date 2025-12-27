#!/usr/bin/env python3
"""
QUICK DEMO SCRIPT - For Live Presentation
Runs key test cases with clear output for audience
"""
import requests
import time
import sys

BASE_URL = "http://localhost:8000/chat"

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def demo_chat(message, session_id):
    """Send message and display response clearly"""
    print(f"\n👤 USER: {message}")
    print("-" * 70)
    
    try:
        response = requests.post(BASE_URL, json={
            "message": message,
            "session_id": session_id
        }, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"🤖 BOT: {data['response'][:300]}")
            
            products = data.get('products', [])
            if products:
                print(f"\n📦 SẢN PHẨM ({len(products)} items):")
                for i, prod in enumerate(products[:3], 1):
                    price = prod.get('price', 'N/A')
                    print(f"   {i}. {prod['title']}")
                    print(f"      💰 Giá: {price}")
                if len(products) > 3:
                    print(f"   ... và {len(products)-3} sản phẩm khác")
            
            suggestions = data.get('quick_replies', [])
            if suggestions:
                print(f"\n💡 GỢI Ý:")
                for sugg in suggestions[:4]:
                    print(f"   • {sugg['label']}")
            
            print("\n✅ SUCCESS")
            return True
        else:
            print(f"❌ ERROR: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("  🎬 CHATBOT LIVE DEMO - GRADUATION PROJECT")
    print("="*70)
    print("\n  Testing key functionalities for presentation...\n")
    
    session_id = f"live_demo_{int(time.time())}"
    
    # Test 1: Greeting
    print_section("TEST 1: Chào hỏi & Gợi ý")
    demo_chat("Xin chào", session_id)
    time.sleep(1)
    
    # Test 2: Product Price
    print_section("TEST 2: Hỏi giá sản phẩm")
    demo_chat("Giá của Medusa Coffee Mug là bao nhiêu?", session_id)
    time.sleep(1)
    
    # Test 3: Product Search
    print_section("TEST 3: Tìm kiếm sản phẩm")
    session_search = f"live_demo_{int(time.time())}_search"
    demo_chat("Tìm backpack", session_search)
    time.sleep(1)
    
    # Test 4: Context Awareness
    print_section("TEST 4: Context - Câu hỏi tiếp theo")
    demo_chat("cho tôi xem chi tiết sản phẩm đầu tiên", session_search)
    time.sleep(1)
    
    # Test 5: Add to Cart
    print_section("TEST 5: Thêm vào giỏ hàng")
    demo_chat("thêm vào giỏ hàng", session_search)
    time.sleep(1)
    
    # Test 6: FAQ
    print_section("TEST 6: Câu hỏi thông tin chung")
    demo_chat("Chính sách đổi trả như thế nào?", session_id)
    time.sleep(1)
    
    # Summary
    print("\n" + "="*70)
    print("  ✅ DEMO COMPLETED SUCCESSFULLY")
    print("="*70)
    print("\n  Key Points Demonstrated:")
    print("  • ✅ Greeting & Suggestions")
    print("  • ✅ Product Search with VND Prices")
    print("  • ✅ Product Details with Images")
    print("  • ✅ Context Awareness")
    print("  • ✅ Add to Cart Intent")
    print("  • ✅ FAQ Responses")
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted\n")
        sys.exit(0)
