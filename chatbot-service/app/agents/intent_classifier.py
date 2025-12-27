from typing import Dict, List
import re

from app.models.agent_types import ProcessedInput, IntentResult
from app.logging_config import get_agent_logger

logger = get_agent_logger("IntentClassifier")


VI_KEYWORDS: Dict[str, List[str]] = {
    "GREETING": ["xin chào", "chào", "alo", "chào bạn", "hello", "hi", "hey", "chào buổi", "chào admin", "chào shop"],
    "PRODUCT.SEARCH": [
        "tìm", "tìm kiếm", "có không", "còn không", "có bán", "muốn mua", "giá", "sản phẩm", 
        "mua", "đặt", "kiếm", "tương tự", "giống", "cần", "shop có", "bên này có", "có hàng",
        "còn hàng", "hết hàng chưa", "còn size", "có màu", "loại", "dòng", "model"
    ],
    "PRODUCT.DETAIL": [
        "chi tiết", "thông số", "xem kỹ", "thông tin", "cụ thể", "mô tả", "spec", 
        "đặc điểm", "tính năng", "chất liệu", "kích thước", "size", "màu sắc", "xuất xứ"
    ],
    "PRODUCT.RECOMMEND": [
        "gợi ý cho tôi", "gợi ý cho mình", "gợi ý vài", "nên mua gì", "mua gì", 
        "hot trend", "bán chạy", "phổ biến", "đề xuất", "recommend me",
        "trending", "mới nhất", "best seller", "top sản phẩm", "sản phẩm tốt", "sản phẩm hay", "đáng mua nhất",
        "xem sản phẩm nào", "có sản phẩm nào", "sản phẩm nào tốt"
    ],
    "ORDER.TRACK": [
        "tra cứu", "kiểm tra", "đơn hàng", "ở đâu", "tình trạng", "tracking", "giao hàng",
        "ship", "vận chuyển", "đã giao chưa", "khi nào nhận", "bao giờ về", "đến chưa"
    ],
    "ORDER.CANCEL": ["hủy đơn", "không mua nữa", "huỷ đơn", "cancel", "không muốn", "đổi ý", "không lấy"],
    "ORDER.RETURN": [
        "đổi trả", "hoàn tiền", "bảo hành", "trả hàng", "return", "refund", "warranty",
        "đổi hàng", "lỗi", "hư", "không vừa", "sai", "không đúng"
    ],
    "CART.VIEW": ["xem giỏ", "giỏ hàng", "trong giỏ", "cart", "giỏ", "đã chọn", "đã thêm"],
    "CART.ADD": [
        "thêm vào giỏ", "bỏ vào giỏ", "mua cái này", "lấy cái này", "đặt cái này", 
        "lấy cho", "thêm 1", "đặt 1", "đặt hàng", "mua ngay", "chốt", "order",
        "cho vào giỏ", "bỏ giỏ", "add", "thêm", "bỏ", "cho tôi", "cho em",
        "mình lấy", "mình mua", "lấy luôn", "mua luôn"
    ],
    "CART.REMOVE": ["xóa khỏi giỏ", "bỏ ra", "xóa sản phẩm", "bỏ sản phẩm", "remove", "không lấy", "bỏ"],
    "CART.UPDATE": ["đổi số lượng", "thay đổi", "sửa giỏ", "update cart", "tăng", "giảm", "đổi size", "đổi màu"],
    "CHECKOUT": ["thanh toán", "checkout", "đặt luôn", "mua luôn", "pay", "trả tiền", "hoàn tất"],
    "ACCOUNT.LOGIN": ["đăng nhập", "login", "sign in", "vào tài khoản"],
    "ACCOUNT.REGISTER": ["đăng ký", "tạo tài khoản", "sign up", "register", "mở tài khoản"],
    "FAQ.SHIPPING": [
        "phí ship", "vận chuyển", "bao lâu", "giao hàng", "ship", "shipping",
        "delivery", "mất bao lâu", "khi nào nhận", "ship cod", "ship nhanh"
    ],
    "FAQ.PAYMENT": [
        "thanh toán", "chuyển khoản", "cod", "trả tiền", "payment", 
        "hình thức thanh toán", "trả góp", "ví", "momo", "zalopay", "banking"
    ],
    "FAQ.PROMO": ["khuyến mãi", "giảm giá", "sale", "voucher", "mã giảm", "coupon", "promotion", "ưu đãi"],
    "FAQ.RETURN": [
        "đổi trả", "chính sách đổi", "return policy", "hoàn tiền", "refund",
        "bảo hành", "warranty", "trả hàng", "đổi hàng", "chính sách hoàn"
    ],
    "SUPPORT.ESCALATE": [
        "nhân viên", "người thật", "không phải bot", "tư vấn", "hỗ trợ", 
        "admin", "staff", "human", "real person", "agent"
    ],
    "THANK": ["cảm ơn", "thanks", "thank you", "cám ơn", "ơn"],
    "GOODBYE": ["tạm biệt", "bye", "goodbye", "hẹn gặp lại", "đi đây"],
    # Staff / Manager Keywords
    "STAFF.CHECK_STOCK": ["check kho", "tồn kho", "kiểm kho", "số lượng tồn", "inventory", "stock"],
    "STAFF.CUSTOMER_LOOKUP": ["tìm khách", "check info khách", "thông tin khách", "lookup customer"],
    "STAFF.ORDER_HISTORY": ["lịch sử mua", "đơn cũ của khách", "khách mua gì", "order history"],
    "STAFF.CREATE_ORDER": ["tạo đơn giúp", "lên đơn", "tạo đơn", "create order", "draft order"],
    "MANAGER.REPORT_SALES": ["doanh thu", "báo cáo bán hàng", "doanh số", "sales report", "revenue"],
    "MANAGER.REPORT_CHATBOT": ["hiệu quả bot", "bot chat bao nhiêu", "thống kê bot", "chatbot stats"],
    "MANAGER.CONFIG_UPDATE": ["tắt bot", "bật bot", "chỉnh prompt", "cấu hình", "config"],
}

EN_KEYWORDS: Dict[str, List[str]] = {
    "GREETING": ["hello", "hi", "hey"],
    "PRODUCT.SEARCH": ["search", "find", "looking for", "do you have", "want to buy", "price", "product", "buy", "order"],
    "PRODUCT.DETAIL": ["detail", "specs", "info", "more info", "specification"],
    "PRODUCT.RECOMMEND": ["recommend", "suggest", "hot trend", "best seller", "popular"],
    "ORDER.TRACK": ["track", "check order", "order status", "where is", "shipping"],
    "ORDER.CANCEL": ["cancel order", "cancel"],
    "ORDER.RETURN": ["return", "refund", "warranty"],
    "CART.VIEW": ["view cart", "my cart", "shopping cart"],
    "CART.ADD": ["add to cart", "buy this", "get this", "order this"],
    "CART.REMOVE": ["remove", "delete item", "remove from cart"],
    "ACCOUNT.LOGIN": ["login", "sign in"],
    "ACCOUNT.REGISTER": ["register", "sign up"],
    "FAQ.SHIPPING": ["shipping cost", "delivery time", "shipping fee"],
    "FAQ.PAYMENT": ["payment", "cod", "bank transfer"],
    "SUPPORT.ESCALATE": ["human", "staff", "real person", "agent"],
    # Staff / Manager Keywords
    "STAFF.CHECK_STOCK": ["check stock", "inventory", "stock level"],
    "STAFF.CUSTOMER_LOOKUP": ["lookup customer", "find customer", "user info"],
    "STAFF.ORDER_HISTORY": ["customer order history", "order history"],
    "STAFF.CREATE_ORDER": ["create order", "draft order"],
    "MANAGER.REPORT_SALES": ["sales report", "revenue", "sales stats"],
    "MANAGER.REPORT_CHATBOT": ["chatbot stats", "bot performance"],
    "MANAGER.CONFIG_UPDATE": ["disable bot", "enable bot", "update config"],
}


def _match_score(text: str, phrases: List[str]) -> int:
    t = f" {text.lower()} "
    score = 0
    for p in phrases:
        if f" {p} " in t:
            score += 2 if len(p.split()) > 1 else 1
    return score


def _parse_price_value(val_str: str) -> int:
    val_str = val_str.lower().replace(",", "").replace(".", "")
    multiplier = 1
    if "k" in val_str or "nghìn" in val_str:
        multiplier = 1000
        val_str = re.sub(r"(k|nghìn)", "", val_str)
    elif "tr" in val_str or "triệu" in val_str or "m" in val_str:
        multiplier = 1000000
        val_str = re.sub(r"(tr|triệu|m)", "", val_str)
    
    try:
        # Extract number part only
        num_match = re.search(r"[\d]+", val_str)
        if num_match:
            return int(float(num_match.group(0)) * multiplier)
        return 0
    except:
        return 0

def _extract_price_condition(text: str) -> dict | None:
    text = text.lower()
    # Range: từ X đến Y
    range_match = re.search(r"từ\s+(\d+[.,\d]*\s*(?:k|tr|triệu|nghìn|m)?)\s+(đến|tới|-)\s+(\d+[.,\d]*\s*(?:k|tr|triệu|nghìn|m)?)", text)
    if range_match:
        min_val = _parse_price_value(range_match.group(1))
        max_val = _parse_price_value(range_match.group(3))
        return {"operator": "range", "min": min_val, "max": max_val}
    
    # Check for independent lower/upper bounds to support "trên X dưới Y"
    min_val = None
    max_val = None

    # Over: trên X, lớn hơn X, cao hơn X, > X
    over_match = re.search(r"(trên|lớn hơn|cao hơn|>)\s+(\d+[.,\d]*\s*(?:k|tr|triệu|nghìn|m)?)", text)
    if over_match:
        min_val = _parse_price_value(over_match.group(2))

    # Under: dưới X, nhỏ hơn X, thấp hơn X, < X
    under_match = re.search(r"(dưới|nhỏ hơn|thấp hơn|<)\s+(\d+[.,\d]*\s*(?:k|tr|triệu|nghìn|m)?)", text)
    if under_match:
        max_val = _parse_price_value(under_match.group(2))
        
    if min_val is not None and max_val is not None:
        return {"operator": "range", "min": min_val, "max": max_val}
    elif min_val is not None:
        return {"operator": "gt", "value": min_val}
    elif max_val is not None:
        return {"operator": "lt", "value": max_val}
        
    return None


def _extract_product_query(cleaned_text: str) -> str:
    s = cleaned_text
    
    # Check if this is a context reference (not a search query)
    context_patterns = [
        r"\b(cái|sản phẩm|sp)\s+(này|kia|đó|ấy|vừa|trước)",
        r"\b(đầu tiên|thứ nhất|thứ hai|cuối cùng)",
        r"\bnó\b",
        r"\bchi tiết\b.*(?!\w+)",  # "chi tiết" without specific product name
    ]
    for pattern in context_patterns:
        if re.search(pattern, s.lower()):
            return ""  # Return empty to signal this needs context
    
    s = re.sub(r"[?,.]", " ", s) # Remove punctuation
    
    # Clean up compound sentences (e.g. "tìm X và thêm vào giỏ")
    # Stop at "và", "rồi", "sau đó" if followed by action verbs
    compound_split = re.split(r'\b(và|rồi|sau đó)\b', s.lower())
    if len(compound_split) > 1:
        s = compound_split[0] # Take the first part as the query

    # Remove price conditions from query
    price_patterns = [
        r"từ\s+(\d+[.,\d]*\s*(?:k|tr|triệu|nghìn|m)?)\s+(đến|tới|-)\s+(\d+[.,\d]*\s*(?:k|tr|triệu|nghìn|m)?)",
        r"(dưới|nhỏ hơn|thấp hơn|<)\s+(\d+[.,\d]*\s*(?:k|tr|triệu|nghìn|m)?)",
        r"(trên|lớn hơn|cao hơn|>)\s+(\d+[.,\d]*\s*(?:k|tr|triệu|nghìn|m)?)"
    ]
    for p in price_patterns:
        s = re.sub(p, " ", s, flags=re.IGNORECASE)

    # remove common Vietnamese/English query anchors
    remove = [
        "tìm", "tìm kiếm", "có không", "còn không", "có bán", "muốn mua",
        "search", "find", "looking for", "do you have", "want to buy",
        "sản phẩm", "product", "mua", "đặt", "kiếm", "cho tôi", "cho anh", "cho em", "cho mình",
        "tương tự", "similar",
        "tôi", "anh", "em", "bạn", "mình", "cái", "chiếc", "là", "của",
        "giá", "bao nhiêu", "price", "cost", "how much", "tiền",
        "thông tin", "xem", "về", "info", "about", "có",
        # Staff keywords
        "check kho", "tồn kho", "kiểm kho", "số lượng tồn",
        "check stock", "inventory", "stock level",
        "tìm khách", "check info khách", "thông tin khách", "khách hàng", "khách",
        "lookup customer", "find customer", "user info",
        "nhân viên", "quản lý", "staff", "manager"
    ]
    low = s.lower()
    for r in remove:
        low = low.replace(r, " ")
    low = re.sub(r"\s+", " ", low).strip()
    return low


class IntentClassifier:
    async def run(self, processed: ProcessedInput) -> IntentResult:
        logger.info(f"Classifying intent - text='{processed.cleaned_text[:60]}...'") 
        text = processed.cleaned_text
        lang = processed.language or "vi"

        # Choose keyword table
        table = VI_KEYWORDS if lang == "vi" else EN_KEYWORDS

        # Compute scores
        scores: Dict[str, int] = {}
        for key, phrases in table.items():
            scores[key] = _match_score(text, phrases)
        
        # Boost PRODUCT.RECOMMEND score if recommend phrases are detected
        # This prevents "gợi ý sản phẩm" from being classified as product_inquiry
        recommend_boost_phrases = ["gợi ý cho", "đề xuất cho", "recommend me", "gợi ý vài", "gợi ý một", "nên mua gì"]
        if any(phrase in text.lower() for phrase in recommend_boost_phrases):
            if "PRODUCT.RECOMMEND" in scores:
                scores["PRODUCT.RECOMMEND"] += 5  # Strong boost to override PRODUCT.SEARCH
        
        # Boost PRODUCT.DETAIL for context reference patterns (e.g., "sản phẩm đầu tiên", "cái này")
        context_patterns = [
            r'\b(cái|sản phẩm|sp)\s+(này|kia|đó|ấy|vừa|trước)',
            r'\b(đầu tiên|thứ nhất|thứ hai|thứ ba|cuối cùng)',
            r'\bnó\b',
        ]
        for pattern in context_patterns:
            if re.search(pattern, text.lower()):
                if "PRODUCT.DETAIL" in scores:
                    scores["PRODUCT.DETAIL"] += 10  # Very strong boost to override PRODUCT.SEARCH
                break

        # Boost PRODUCT.SEARCH if "tìm" is explicitly used at start
        if text.lower().strip().startswith("tìm") or "tìm cho" in text.lower():
             if "PRODUCT.SEARCH" in scores:
                 scores["PRODUCT.SEARCH"] += 3

        # Boost CART.ADD if "thêm" or "mua" is present, to differentiate from CART.VIEW
        if "thêm" in text.lower() or "mua" in text.lower():
            if "CART.ADD" in scores:
                scores["CART.ADD"] += 2

        # Get top 3 intents for multi-intent detection
        sorted_scores = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
        top_key = sorted_scores[0][0] if sorted_scores else "UNKNOWN"
        top_score = sorted_scores[0][1] if sorted_scores else 0
        
        # Detect secondary intent (e.g., "tìm balo giá rẻ" = PRODUCT.SEARCH + PRODUCT.PRICE)
        secondary_intent = None
        if len(sorted_scores) > 1 and sorted_scores[1][1] >= 2:
            secondary_intent = sorted_scores[1][0]
        
        logger.debug(f"Intent scores - top={top_key}({top_score}) secondary={secondary_intent} all_scores={dict(list(sorted_scores)[:5])}")

        # Map to system intents used by backend
        intent_map = {
            "GREETING": "general",
            "PRODUCT.SEARCH": "product_inquiry",
            "PRODUCT.DETAIL": "product_detail",
            "PRODUCT.RECOMMEND": "product_recommend",
            "ORDER.TRACK": "order_tracking",
            "ORDER.CANCEL": "order_cancel",
            "ORDER.RETURN": "order_return",
            "CART.VIEW": "cart_view",
            "CART.ADD": "cart_add",
            "CART.REMOVE": "cart_remove",
            "CART.UPDATE": "cart_update",
            "CHECKOUT": "checkout",
            "ACCOUNT.LOGIN": "account_login",
            "ACCOUNT.REGISTER": "account_register",
            "FAQ.SHIPPING": "faq_shipping",
            "FAQ.PAYMENT": "faq_payment",
            "FAQ.PROMO": "faq_promo",
            "FAQ.RETURN": "faq_return",
            "SUPPORT.ESCALATE": "human_escalation",
            "THANK": "thank_you",
            "GOODBYE": "goodbye",
            "STAFF.CHECK_STOCK": "staff_check_stock",
            "STAFF.CUSTOMER_LOOKUP": "staff_customer_lookup",
            "STAFF.ORDER_HISTORY": "staff_order_history",
            "STAFF.CREATE_ORDER": "staff_create_order",
            "MANAGER.REPORT_SALES": "manager_report_sales",
            "MANAGER.REPORT_CHATBOT": "manager_report_chatbot",
            "MANAGER.CONFIG_UPDATE": "manager_config_update",
        }

        mapped = intent_map.get(top_key, "general")
        sub_intent = intent_map.get(secondary_intent) if secondary_intent else None

        # Enhanced confidence scoring
        if top_score >= 4:
            conf = 0.95
        elif top_score >= 3:
            conf = 0.85
        elif top_score >= 2:
            conf = 0.70
        elif top_score >= 1:
            conf = 0.50
        else:
            conf = 0.30

        entities = {}
        
        # Enhanced entity extraction
        if mapped == "product_inquiry" or mapped == "cart_add" or mapped == "product_detail":
            q = _extract_product_query(text)
            # For product_detail, empty query means context reference
            if mapped == "product_detail" and q == "":
                entities["product_query"] = ""  # Signal to use context
            elif q and len(q) >= 2:
                entities["product_query"] = q
            
            # Extract quantity
            qty_match = re.search(r'(\d+)\s*(cái|chiếc|con|bộ|món|sản phẩm|sp)', text.lower())
            if qty_match:
                entities["quantity"] = int(qty_match.group(1))
            else:
                entities["quantity"] = 1
            
            # Extract price condition
            price_cond = _extract_price_condition(text)
            if price_cond:
                entities["price_condition"] = price_cond
                
        elif mapped == "order_tracking":
            # Enhanced order ID extraction
            # Priority 1: Full Medusa ID (case-sensitive)
            medusa_id_match = re.search(r'\b(order_[0-9A-Za-z]+)\b', text)
            if medusa_id_match:
                entities["order_id"] = medusa_id_match.group(1)
            else:
                # Priority 2: Short ID / Display ID
                # Patterns: #1234, order 1234, ORD-1234, đơn 1234
                match = re.search(r'(order[_\s-]?[\w\d]+|#\d+|ord[_\s-]?\d+|đơn[\s]?\d+|\d{4,})', text.lower())
                if match:
                    # Clean up to get the core ID/Number
                    val = match.group(0)
                    # If it looks like a Medusa ID but wasn't caught by Priority 1 (maybe mixed case or spacing)
                    if "order" in val and "_" in val:
                         entities["order_id"] = val.replace(" ", "") # Try to preserve it
                    else:
                         # It's likely a display ID or short code
                         order_id = val.replace("#", "").replace("đơn", "").replace("order", "").replace("_", "").replace("-", "").strip()
                         entities["order_id"] = order_id
                
        elif mapped == "staff_check_stock":
            q = _extract_product_query(text)
            if q:
                entities["product_query"] = q
                
        elif mapped == "staff_customer_lookup":
            # Extract customer info (email, phone, name)
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
            phone_match = re.search(r'(\+?84|0)\d{9,10}', text)
            
            if email_match:
                entities["customer_email"] = email_match.group(0)
            elif phone_match:
                entities["customer_phone"] = phone_match.group(0)
            else:
                # Fallback to query extraction
                q = _extract_product_query(text)
                if q:
                    entities["customer_query"] = q
        
        logger.info(f"Intent classified - intent={mapped} confidence={conf:.2f} sub_intent={sub_intent} entities={entities}")
        return IntentResult(
            intent=mapped,
            sub_intent=sub_intent,
            confidence=conf,
            entities=entities,
        )
