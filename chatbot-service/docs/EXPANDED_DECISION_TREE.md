# 🌳 EXPANDED DECISION TREE & NLP SCENARIOS

## 🎭 User Roles & Permissions
1.  **Customer (Guest/Logged-in)**: Shopping, Order Tracking, Support.
2.  **Staff (Consultant)**: Customer Lookup, Stock Check, Order Assistance.
3.  **Manager (Admin)**: Reports, System Config, Override.

---

## 📋 Intent Structure

### 1. 🛍️ CUSTOMER INTENTS (Shopping & Service)

| Intent Group | Intent | Keywords (VI) | Keywords (EN) | Action/Tool |
| :--- | :--- | :--- | :--- | :--- |
| **GREETING** | `GREETING` | xin chào, hello, hi, alo | hello, hi, hey | `response.greet` |
| **PRODUCT** | `PRODUCT.SEARCH` | tìm, mua, giá, có bán, còn hàng | search, find, price, buy | `product.search` |
| | `PRODUCT.DETAIL` | chi tiết, thông số, xem kỹ | detail, specs, info | `product.get_details` |
| | `PRODUCT.RECOMMEND`| gợi ý, nên mua gì, hot trend | recommend, suggest | `product.recommend` |
| **ORDER** | `ORDER.TRACK` | tra cứu, đơn hàng, ở đâu | track, status, where is | `order.lookup` |
| | `ORDER.CANCEL` | hủy đơn, không mua nữa | cancel order | `order.cancel` |
| | `ORDER.RETURN` | đổi trả, hoàn tiền, bảo hành | return, refund | `response.policy_return` |
| **CART** | `CART.VIEW` | xem giỏ, giỏ hàng | view cart, my cart | `cart.view` |
| | `CART.ADD` | thêm vào giỏ, lấy cái này | add to cart, buy this | `cart.add` |
| | `CART.REMOVE` | xóa khỏi giỏ, bỏ ra | remove, delete item | `cart.remove` |
| **ACCOUNT** | `ACCOUNT.LOGIN` | đăng nhập, login | login, sign in | `response.login_link` |
| | `ACCOUNT.REGISTER` | đăng ký, tạo tài khoản | register, sign up | `response.register_link` |
| **FAQ** | `FAQ.SHIPPING` | phí ship, vận chuyển, bao lâu | shipping cost, delivery time | `response.faq_shipping` |
| | `FAQ.PAYMENT` | thanh toán, chuyển khoản | payment, cod | `response.faq_payment` |

---

### 2. 🧑‍💼 STAFF / CONSULTANT INTENTS (Internal Tools)
*Requires `user_type=staff` or `user_type=admin`*

| Intent Group | Intent | Keywords (VI) | Keywords (EN) | Action/Tool |
| :--- | :--- | :--- | :--- | :--- |
| **CUSTOMER** | `STAFF.CUSTOMER_LOOKUP` | tìm khách, check info khách | lookup customer, find user | `customer.lookup` |
| | `STAFF.ORDER_HISTORY` | lịch sử mua của khách | customer order history | `customer.order_history` |
| **STOCK** | `STAFF.CHECK_STOCK` | check kho, tồn kho thực tế | check stock, inventory | `inventory.check_stock` |
| **ORDER** | `STAFF.CREATE_ORDER` | tạo đơn giúp, lên đơn cho khách | create order for, draft order | `order.create_draft` |

---

### 3. 👨‍💼 MANAGER / ADMIN INTENTS (Management)
*Requires `user_type=admin`*

| Intent Group | Intent | Keywords (VI) | Keywords (EN) | Action/Tool |
| :--- | :--- | :--- | :--- | :--- |
| **REPORT** | `MANAGER.REPORT_SALES` | doanh thu hôm nay, báo cáo bán hàng | sales report, revenue | `report.sales` |
| | `MANAGER.REPORT_CHATBOT`| hiệu quả bot, bot chat bao nhiêu | chatbot stats, bot performance | `report.chatbot_stats` |
| **CONFIG** | `MANAGER.CONFIG_UPDATE` | tắt bot, bật bot, chỉnh prompt | disable bot, update config | `system.update_config` |

---

## 🔄 Decision Flow (Orchestrator Logic)

### Scenario A: Customer wants to cancel order
1. **Input**: "Tôi muốn hủy đơn hàng #123"
2. **Intent**: `ORDER.CANCEL` (Entity: `order_id=123`)
3. **Orchestrator**:
   - Check: Is user logged in?
     - No -> Response: "Vui lòng đăng nhập để hủy đơn."
     - Yes -> Check: Does order #123 belong to user?
       - Yes -> Check: Is status 'pending'?
         - Yes -> **Tool**: `order.cancel(#123)`
         - No -> Response: "Đơn hàng đã giao, không thể hủy."

### Scenario B: Staff checks stock for customer
1. **Input**: "Check tồn kho áo Hoodie size L"
2. **Intent**: `STAFF.CHECK_STOCK` (Entity: `product=Hoodie`, `variant=L`)
3. **Orchestrator**:
   - Check: Is user Staff?
     - No -> Fallback to `PRODUCT.SEARCH` (Customer view)
     - Yes -> **Tool**: `inventory.get_stock_level(sku)` -> Returns exact quantity across warehouses.

### Scenario C: Manager asks for revenue
1. **Input**: "Doanh thu hôm nay thế nào?"
2. **Intent**: `MANAGER.REPORT_SALES` (Entity: `period=today`)
3. **Orchestrator**:
   - Check: Is user Admin?
     - No -> Response: "Bạn không có quyền truy cập."
     - Yes -> **Tool**: `report.get_sales_stats(start, end)`

