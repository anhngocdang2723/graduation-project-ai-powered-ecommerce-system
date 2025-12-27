# Response Templates for Chatbot
# Provides context-aware, natural Vietnamese responses

RESPONSE_TEMPLATES = {
    # Greetings
    "greeting": [
        "👋 **Xin chào!** Tôi là trợ lý ảo của shop. Tôi có thể giúp gì cho bạn hôm nay? 😊",
        "Chào bạn! Rất vui được hỗ trợ bạn. Bạn đang quan tâm đến dòng sản phẩm nào của shop ạ? 🛍️",
        "Chào mừng bạn đến với shop! 🌟 Tôi có thể tư vấn sản phẩm hoặc hỗ trợ kiểm tra đơn hàng cho bạn nhé."
    ],
    
    # Product Search Success
    "product_found": [
        "✨ Shop tìm thấy **{count}** sản phẩm phù hợp với yêu cầu của bạn:",
        "Dưới đây là **{count}** sản phẩm tốt nhất dành cho bạn:",
        "Shop có **{count}** sản phẩm như bạn đang tìm kiếm ạ:"
    ],
    
    # Product Not Found
    "product_not_found": [
        "😔 Rất tiếc, shop hiện chưa tìm thấy sản phẩm **'{query}'** như bạn mong muốn.\n\n💡 **Gợi ý:** Bạn có thể thử tìm kiếm với từ khóa khác hoặc xem các sản phẩm tương tự bên dưới nhé!",
        "Hiện tại shop chưa có sản phẩm **'{query}'** ạ. Bạn có muốn tham khảo các mẫu bán chạy khác của shop không? 🌟",
        "Mình chưa tìm thấy **'{query}'** trong kho. Bạn có thể mô tả chi tiết hơn (màu sắc, chất liệu...) để mình hỗ trợ tốt hơn nhé!"
    ],
    
    # Product Recommend
    "product_recommend": [
        "🌟 **Gợi ý dành riêng cho bạn:** Đây là những sản phẩm đang được yêu thích nhất tại shop:",
        "🔥 **Hot Trend:** Đừng bỏ lỡ những sản phẩm đang 'làm mưa làm gió' này nhé:",
        "✨ Shop gợi ý cho bạn một vài sản phẩm nổi bật, hy vọng bạn sẽ thích:"
    ],
    
    # Cart Actions
    "cart_added": [
        "✅ Tuyệt vời! Đã thêm **{product}** vào giỏ hàng của bạn.\n\n🛒 Bạn muốn tiếp tục chọn thêm đồ hay thanh toán luôn ạ?",
        "OK! **{product}** đã nằm gọn trong giỏ hàng rồi nhé. 😉\n\nBạn có muốn xem thêm sản phẩm nào khác không?",
        "Đã thêm thành công! Giỏ hàng của bạn đã sẵn sàng. Bạn cần hỗ trợ gì thêm trước khi thanh toán không?"
    ],
    
    "cart_view_empty": [
        "🛒 Giỏ hàng của bạn đang trống.\n\n✨ Hãy khám phá ngay những bộ sưu tập mới nhất của shop nhé! 🛍️",
        "Bạn chưa có sản phẩm nào trong giỏ. Cùng dạo quanh shop một vòng nhé! 😊"
    ],
    
    "cart_view_has_items": [
        "🛒 Giỏ hàng của bạn hiện có **{count}** sản phẩm:",
        "📦 Bạn đang có **{count}** món đồ trong giỏ hàng. Đây là chi tiết:",
        "Đây là danh sách sản phẩm trong giỏ hàng của bạn (**{count}** món):"
    ],
    
    # Order Tracking
    "order_found": [
        "### 📦 Thông tin đơn hàng #{order_id}\n\n- **Trạng thái:** {status}\n- **Tổng tiền:** {total}\n- **Sản phẩm:** {items}\n- **Dự kiến giao:** {delivery_date}\n\nBạn cần hỗ trợ gì thêm về đơn hàng này không ạ?",
        "🔍 **Kết quả tra cứu đơn hàng #{order_id}:**\n\n📌 **Trạng thái:** {status}\n💰 **Tổng thanh toán:** {total}\n📅 **Ngày giao dự kiến:** {delivery_date}\n\nĐơn hàng của bạn đang được xử lý tích cực nhé! 🚚"
    ],
    
    "order_not_found": [
        "❌ Rất tiếc, mình không tìm thấy đơn hàng **#{order_id}** trên hệ thống.\n\n💡 Bạn vui lòng kiểm tra lại mã đơn hàng hoặc liên hệ nhân viên hỗ trợ nhé!",
        "Mã đơn hàng **#{order_id}** có vẻ không chính xác. Bạn kiểm tra lại giúp mình nha! 🙏"
    ],
    
    # FAQ
    "faq_shipping": [
        "🚚 **Thông tin vận chuyển:**\n\n📍 **Nội thành (HN/HCM):** 2-3 ngày, phí 30.000₫\n📍 **Ngoại thành:** 3-5 ngày, phí 50.000₫\n\n🎁 **Ưu đãi:** Miễn phí vận chuyển cho đơn hàng từ **500.000₫**.\n✅ Hỗ trợ thanh toán khi nhận hàng (COD) toàn quốc.",
        "Shop giao hàng toàn quốc với thời gian từ 2-5 ngày tùy khu vực ạ. Đặc biệt, đơn hàng trên **500k** sẽ được **FREE SHIP** hoàn toàn nhé! 🚚💨"
    ],
    
    "faq_return": [
        "🔄 **Chính sách đổi trả chuyên nghiệp:**\n\n1️⃣ Đổi trả miễn phí trong vòng **7 ngày**.\n2️⃣ Sản phẩm còn nguyên tem mác, chưa qua sử dụng.\n3️⃣ Hỗ trợ đổi size/màu tận nơi (nếu còn hàng).\n4️⃣ Hoàn tiền nhanh chóng trong 3-5 ngày làm việc.",
        "Bạn hoàn toàn yên tâm mua sắm nhé! Shop hỗ trợ đổi trả trong **7 ngày** nếu có lỗi từ nhà sản xuất hoặc không vừa size ạ. ✨"
    ],
    
    "faq_payment": [
        "💳 **Phương thức thanh toán linh hoạt:**\n\n✅ **COD:** Thanh toán tiền mặt khi nhận hàng.\n✅ **Chuyển khoản:** Qua ngân hàng (Vietcombank, Techcombank...).\n✅ **Thẻ:** Visa, Mastercard, JCB.\n✅ **Ví điện tử:** Momo, ZaloPay, ShopeePay.",
        "Shop hỗ trợ nhiều hình thức thanh toán như COD, chuyển khoản và các loại ví điện tử để bạn thuận tiện nhất nhé! 💳✨"
    ],
    
    "faq_promo": [
        "🎁 **Chương trình ưu đãi hiện tại:**\n\n🔥 Giảm ngay **10%** cho đơn hàng đầu tiên.\n🚚 **Free ship** cho mọi đơn hàng từ 500.000₫.\n💎 Tích điểm thành viên để nhận quà tặng hấp dẫn.",
        "Đừng bỏ lỡ ưu đãi giảm **10%** cho khách hàng mới và chính sách **Free ship** đơn từ 500k của shop nhé! 🎉"
    ],
    
    # Thank you & Goodbye
    "thank_you": [
        "Rất vui được hỗ trợ bạn! 😊 Chúc bạn có những trải nghiệm mua sắm tuyệt vời tại shop.",
        "Không có gì ạ! Cần hỗ trợ thêm bất cứ điều gì, bạn cứ nhắn mình nhé! ✨",
        "Luôn sẵn sàng giúp đỡ bạn! Chúc bạn một ngày tốt lành và mua sắm vui vẻ! 🛍️"
    ],
    
    "goodbye": [
        "Tạm biệt bạn! Hẹn gặp lại bạn sớm nhé. 👋",
        "Chào tạm biệt! Đừng quên ghé shop thường xuyên để cập nhật mẫu mới nha! 😊",
        "Hẹn gặp lại bạn! Chúc bạn một ngày thật nhiều niềm vui! 🌟"
    ],
    
    # Errors
    "error_generic": [
        "😔 Xin lỗi, hệ thống đang gặp một chút trục trặc nhỏ. Bạn vui lòng thử lại sau giây lát nhé!",
        "Rất tiếc, mình chưa xử lý được yêu cầu này ngay lúc này. Bạn thử lại hoặc nhắn tin cho nhân viên hỗ trợ nhé! 🙏"
    ],
    
    "error_no_products": [
        "Shop đang cập nhật thêm nhiều mẫu mới. Bạn vui lòng quay lại sau hoặc xem các sản phẩm hiện có nhé! ✨",
        "Hiện tại các sản phẩm này đang tạm hết hàng. Shop sẽ sớm bổ sung thêm ạ! 📦"
    ],
    
    # Staff/Manager
    "staff_success": [
        "✅ **Đã xử lý thành công!** Chi tiết kết quả:",
        "Hoàn tất! Đây là thông tin bạn yêu cầu:"
    ],
    
    "manager_report": [
        "📊 **Báo cáo {report_type}:**\n\n{data}",
        "Đây là thống kê chi tiết về **{report_type}** bạn yêu cầu:\n\n{data}"
    ],
    
    # Clarification needed
    "need_clarification": [
        "Xin lỗi, mình chưa hiểu rõ ý bạn lắm. Bạn có thể mô tả chi tiết hơn được không ạ? 🤔",
        "Hmm, bạn đang quan tâm đến vấn đề gì nhỉ? Hãy cho mình biết thêm thông tin nhé!",
        "Bạn cần tìm sản phẩm hay hỗ trợ về đơn hàng? Nhắn chi tiết để mình giúp bạn nhanh nhất nha! ✨"
    ],
    
    "ask_product_details": [
        "Để tìm được sản phẩm ưng ý nhất, bạn cho mình biết thêm về: **màu sắc, kích thước hoặc khoảng giá** mong muốn nhé? 🎨",
        "Bạn đang tìm sản phẩm theo tiêu chí nào ạ? (Ví dụ: màu đen, size L, giá dưới 500k...)"
    ],
    
    "ask_order_id": [
        "Bạn vui lòng cung cấp **Mã đơn hàng** (Ví dụ: #1234) để mình kiểm tra trạng thái giúp bạn nhé! 🔍",
        "Cho mình xin mã đơn hàng của bạn để mình check thông tin ngay ạ!"
    ]
}

# Context-aware response selection
from typing import Optional
def get_response_template(intent: str, context: Optional[dict] = None) -> str:
    """Get appropriate response template based on intent and context"""
    import random
    
    context = context or {}
    templates = RESPONSE_TEMPLATES.get(intent, RESPONSE_TEMPLATES["need_clarification"])
    
    # Select random template for variety
    template = random.choice(templates)
    
    # Format with context if available
    try:
        if context:
            template = template.format(**context)
    except KeyError:
        pass  # Use template as-is if formatting fails
    
    return template
