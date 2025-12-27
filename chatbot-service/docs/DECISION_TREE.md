# 🌳 DECISION TREE - Kịch bản phân nhánh

## Tổng quan

Decision Tree giúp chatbot xác định chính xác intent của user mà không cần LLM.
Sử dụng keyword matching + context để phân loại.

---

## 📋 Intent Tree Structure

```
ROOT (Điểm bắt đầu)
│
├── 👋 GREETING ─────────────────────────────────────────────────────────────
│   │  Keywords: xin chào, hello, hi, chào, hey, alo
│   │  
│   └── Response: Welcome message + Main menu
│       └── Quick Replies: 
│           [🔍 Tìm sản phẩm] 
│           [📦 Tra cứu đơn hàng] 
│           [🛒 Xem giỏ hàng]
│           [❓ Trợ giúp]
│
├── 🔍 PRODUCT ──────────────────────────────────────────────────────────────
│   │  Keywords: sản phẩm, product, mua, tìm, giá, price, còn, có
│   │
│   ├── PRODUCT.SEARCH
│   │   │  Keywords: tìm, search, có...không, còn...không, tìm kiếm
│   │   │  Extract: search_query (phần còn lại sau keyword)
│   │   │
│   │   └── Flow:
│   │       1. Extract search query
│   │       2. Call tool: search_products(query)
│   │       3. Response: Product list
│   │       └── Quick Replies:
│   │           [Xem chi tiết {product_1}]
│   │           [Thêm vào giỏ]
│   │           [Tìm tiếp]
│   │
│   ├── PRODUCT.DETAIL
│   │   │  Keywords: chi tiết, thông tin, xem, detail, about
│   │   │  Extract: product_id OR product_name
│   │   │
│   │   └── Flow:
│   │       1. Identify product (from context or extract)
│   │       2. Call tool: get_product(id)
│   │       3. Response: Full product info + images
│   │       └── Quick Replies:
│   │           [Thêm vào giỏ]
│   │           [Chọn size/màu]
│   │           [Sản phẩm tương tự]
│   │
│   ├── PRODUCT.COMPARE
│   │   │  Keywords: so sánh, compare, khác nhau, versus, vs
│   │   │  Extract: product_ids[] (2+ products)
│   │   │
│   │   └── Flow:
│   │       1. Get products from context or ask
│   │       2. Call tool: get_products(ids)
│   │       3. Response: Comparison table
│   │
│   └── PRODUCT.RECOMMEND
│       │  Keywords: gợi ý, đề xuất, recommend, suggest, nên mua gì
│       │
│       └── Flow:
│           1. Check user history (if customer)
│           2. Call tool: get_featured_products()
│           3. Response: Recommended products
│
├── 📦 ORDER ────────────────────────────────────────────────────────────────
│   │  Keywords: đơn hàng, order, giao hàng, shipping, vận chuyển
│   │
│   ├── ORDER.TRACK
│   │   │  Keywords: tra cứu, kiểm tra, ở đâu, track, tracking, tình trạng
│   │   │  Required: order_id OR email
│   │   │  Permission: Customer only (guest → prompt login)
│   │   │
│   │   └── Flow:
│   │       ┌─ IF user == guest:
│   │       │     Response: "Vui lòng đăng nhập để xem đơn hàng"
│   │       │     Action: show_login_prompt
│   │       │
│   │       └─ IF user == customer:
│   │             ├─ Has order_id in message?
│   │             │   ├─ YES → Call: get_order(order_id)
│   │             │   └─ NO  → Call: list_orders(customer_id) → Show list
│   │             │
│   │             └── Response: Order status with timeline
│   │                 └── Quick Replies:
│   │                     [Xem chi tiết]
│   │                     [Hủy đơn]
│   │                     [Liên hệ hỗ trợ]
│   │
│   ├── ORDER.CREATE
│   │   │  Keywords: đặt hàng, mua ngay, order, checkout, thanh toán
│   │   │
│   │   └── Flow:
│   │       1. Check cart exists and not empty
│   │       2. Guide to checkout page
│   │       3. Response: "Giỏ hàng có X sản phẩm. Bấm để thanh toán"
│   │       └── Action: redirect_to_checkout
│   │
│   ├── ORDER.CANCEL
│   │   │  Keywords: hủy, cancel, không muốn, bỏ đơn
│   │   │  Required: order_id
│   │   │  Permission: Customer only
│   │   │
│   │   └── Flow:
│   │       1. Verify order belongs to customer
│   │       2. Check if cancellable (status = pending)
│   │       3. Confirm with user
│   │       4. Call tool: cancel_order(order_id)
│   │
│   └── ORDER.HISTORY
│       │  Keywords: lịch sử, history, đã mua, previous orders
│       │  Permission: Customer only
│       │
│       └── Flow:
│           1. Call tool: list_orders(customer_id)
│           2. Response: Order history list
│
├── 🛒 CART ─────────────────────────────────────────────────────────────────
│   │  Keywords: giỏ hàng, cart, giỏ
│   │
│   ├── CART.VIEW
│   │   │  Keywords: xem giỏ, giỏ hàng, cart, trong giỏ
│   │   │
│   │   └── Flow:
│   │       1. Get cart_id from session
│   │       2. Call tool: get_cart(cart_id)
│   │       3. Response: Cart items + total
│   │       └── Quick Replies:
│   │           [Thanh toán]
│   │           [Tiếp tục mua]
│   │           [Xóa sản phẩm]
│   │
│   ├── CART.ADD
│   │   │  Keywords: thêm, add, bỏ vào giỏ, mua cái này
│   │   │  Required: product_id (from context), variant_id, quantity
│   │   │
│   │   └── Flow:
│   │       ┌─ Has product in context?
│   │       │   ├─ YES → Check variant selected?
│   │       │   │         ├─ YES → Add to cart
│   │       │   │         └─ NO  → Ask for variant (size/color)
│   │       │   └─ NO  → Ask "Bạn muốn thêm sản phẩm nào?"
│   │       │
│   │       └── After add:
│   │           Response: "Đã thêm {product} vào giỏ!"
│   │           └── Quick Replies:
│   │               [Xem giỏ hàng]
│   │               [Thanh toán ngay]
│   │               [Tiếp tục mua]
│   │
│   ├── CART.UPDATE
│   │   │  Keywords: sửa, thay đổi số lượng, update, cập nhật
│   │   │
│   │   └── Flow:
│   │       1. Identify item to update
│   │       2. Ask for new quantity
│   │       3. Call tool: update_line_item(item_id, quantity)
│   │
│   └── CART.REMOVE
│       │  Keywords: xóa, remove, bỏ ra, không mua nữa
│       │
│       └── Flow:
│           1. Identify item to remove
│           2. Confirm with user
│           3. Call tool: remove_from_cart(item_id)
│
├── 👤 ACCOUNT ──────────────────────────────────────────────────────────────
│   │  Keywords: tài khoản, account, đăng nhập, đăng ký
│   │
│   ├── ACCOUNT.LOGIN_HELP
│   │   │  Keywords: đăng nhập, login, không vào được
│   │   │
│   │   └── Response: Hướng dẫn đăng nhập + link
│   │       └── Action: show_login_modal
│   │
│   ├── ACCOUNT.REGISTER_HELP
│   │   │  Keywords: đăng ký, register, tạo tài khoản
│   │   │
│   │   └── Response: Hướng dẫn đăng ký + link
│   │       └── Action: show_register_modal
│   │
│   └── ACCOUNT.ADDRESS
│       │  Keywords: địa chỉ, address, giao đến đâu
│       │  Permission: Customer only
│       │
│       └── Flow:
│           1. Call tool: get_addresses(customer_id)
│           2. Response: Address list
│           └── Quick Replies:
│               [Thêm địa chỉ mới]
│               [Sửa địa chỉ]
│
├── ❓ FAQ ──────────────────────────────────────────────────────────────────
│   │  Keywords: hỏi, câu hỏi, faq, chính sách
│   │
│   ├── FAQ.SHIPPING
│   │   │  Keywords: vận chuyển, ship, giao hàng, phí ship, bao lâu
│   │   │
│   │   └── Response: Template về chính sách vận chuyển
│   │
│   ├── FAQ.PAYMENT
│   │   │  Keywords: thanh toán, payment, trả tiền, COD, chuyển khoản
│   │   │
│   │   └── Response: Template về phương thức thanh toán
│   │
│   ├── FAQ.RETURN
│   │   │  Keywords: đổi trả, return, hoàn tiền, refund, bảo hành
│   │   │
│   │   └── Response: Template về chính sách đổi trả
│   │
│   └── FAQ.CONTACT
│       │  Keywords: liên hệ, contact, hotline, email, địa chỉ cửa hàng
│       │
│       └── Response: Thông tin liên hệ
│
├── 🆘 SUPPORT ──────────────────────────────────────────────────────────────
│   │  Keywords: hỗ trợ, support, giúp đỡ, help
│   │
│   ├── SUPPORT.ESCALATE
│   │   │  Keywords: nhân viên, người thật, nói chuyện, staff, human
│   │   │
│   │   └── Flow:
│   │       1. Update session.status = 'escalated'
│   │       2. Notify admin via WebSocket
│   │       3. Response: "Đang kết nối với nhân viên hỗ trợ..."
│   │       └── Action: wait_for_staff
│   │
│   ├── SUPPORT.COMPLAINT
│   │   │  Keywords: khiếu nại, complaint, không hài lòng, tệ, dở
│   │   │
│   │   └── Flow:
│   │       1. Acknowledge complaint
│   │       2. Ask for details
│   │       3. Auto-escalate if serious
│   │
│   └── SUPPORT.FEEDBACK
│       │  Keywords: góp ý, feedback, đánh giá, review
│       │
│       └── Flow:
│           1. Thank user
│           2. Save feedback to DB
│           3. Response: "Cảm ơn góp ý của bạn!"
│
└── 🤷 UNKNOWN ──────────────────────────────────────────────────────────────
    │  Khi không match được intent nào
    │
    └── Flow:
        1. Try LLM to understand (fallback)
        2. If still unclear:
           Response: "Tôi chưa hiểu ý bạn. Bạn có thể chọn:"
           └── Quick Replies:
               [🔍 Tìm sản phẩm]
               [📦 Tra cứu đơn hàng]
               [🆘 Nói chuyện với nhân viên]
```

---

## 🔑 Keyword Dictionary

### Vietnamese Keywords

```python
INTENT_KEYWORDS = {
    "GREETING": {
        "vi": ["xin chào", "chào", "hello", "hi", "hey", "alo", "chào bạn"],
        "en": ["hello", "hi", "hey", "good morning", "good afternoon"]
    },
    
    "PRODUCT.SEARCH": {
        "vi": ["tìm", "tìm kiếm", "có không", "còn không", "có bán", "muốn mua"],
        "en": ["search", "find", "looking for", "do you have", "want to buy"]
    },
    
    "PRODUCT.DETAIL": {
        "vi": ["chi tiết", "thông tin", "xem", "về sản phẩm", "mô tả"],
        "en": ["detail", "info", "about", "describe", "tell me about"]
    },
    
    "ORDER.TRACK": {
        "vi": ["tra cứu", "kiểm tra", "đơn hàng", "ở đâu", "tình trạng", "tracking"],
        "en": ["track", "check order", "where is", "order status", "shipping"]
    },
    
    "ORDER.CANCEL": {
        "vi": ["hủy", "hủy đơn", "không mua nữa", "bỏ đơn"],
        "en": ["cancel", "cancel order", "don't want"]
    },
    
    "CART.ADD": {
        "vi": ["thêm vào giỏ", "bỏ vào giỏ", "mua cái này", "lấy cái này"],
        "en": ["add to cart", "buy this", "get this"]
    },
    
    "CART.VIEW": {
        "vi": ["xem giỏ", "giỏ hàng", "trong giỏ có gì"],
        "en": ["view cart", "my cart", "shopping cart"]
    },
    
    "SUPPORT.ESCALATE": {
        "vi": ["nhân viên", "người thật", "nói chuyện với người", "không phải bot"],
        "en": ["human", "staff", "real person", "talk to someone", "agent"]
    },
    
    "FAQ.SHIPPING": {
        "vi": ["vận chuyển", "ship", "giao hàng", "phí ship", "bao lâu", "mấy ngày"],
        "en": ["shipping", "delivery", "shipping fee", "how long", "delivery time"]
    },
    
    "FAQ.RETURN": {
        "vi": ["đổi trả", "hoàn tiền", "trả hàng", "bảo hành", "refund"],
        "en": ["return", "refund", "exchange", "warranty"]
    }
}
```

---

## 🔄 Context-Aware Intent Resolution

Một số intent cần context từ conversation trước:

```python
CONTEXT_DEPENDENCIES = {
    "CART.ADD": {
        "requires": ["current_product"],  # Cần biết đang xem product nào
        "fallback": "PRODUCT.SEARCH"      # Nếu không có, chuyển sang search
    },
    
    "PRODUCT.DETAIL": {
        "requires": ["product_id"],
        "fallback": "ASK_WHICH_PRODUCT"
    },
    
    "ORDER.TRACK": {
        "requires": ["order_id"],
        "fallback": "ORDER.HISTORY"  # Show list để user chọn
    }
}
```

---

## 📱 Quick Replies by Intent

```python
QUICK_REPLIES = {
    "GREETING": [
        {"label": "🔍 Tìm sản phẩm", "action": "PRODUCT.SEARCH"},
        {"label": "📦 Tra cứu đơn hàng", "action": "ORDER.TRACK"},
        {"label": "🛒 Xem giỏ hàng", "action": "CART.VIEW"},
        {"label": "❓ Trợ giúp", "action": "FAQ"}
    ],
    
    "PRODUCT.SEARCH_RESULT": [
        {"label": "Xem chi tiết", "action": "PRODUCT.DETAIL", "params": "{product_id}"},
        {"label": "Thêm vào giỏ", "action": "CART.ADD", "params": "{product_id}"},
        {"label": "Tìm tiếp", "action": "PRODUCT.SEARCH"}
    ],
    
    "CART.VIEW": [
        {"label": "💳 Thanh toán", "action": "CHECKOUT"},
        {"label": "🛍️ Tiếp tục mua", "action": "PRODUCT.SEARCH"},
        {"label": "🗑️ Xóa sản phẩm", "action": "CART.REMOVE"}
    ],
    
    "UNKNOWN": [
        {"label": "🔍 Tìm sản phẩm", "action": "PRODUCT.SEARCH"},
        {"label": "📦 Đơn hàng", "action": "ORDER.TRACK"},
        {"label": "🆘 Gặp nhân viên", "action": "SUPPORT.ESCALATE"}
    ]
}
```

---

*Last updated: 2025-11-30*
