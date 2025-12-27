import os
import yaml
import json
import logging
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam
from app.config import GOOGLE_API_KEY, GEMINI_BASE_URL, GEMINI_MODEL, SYSTEM_PROMPT_VI
from app.models.api_models import ChatResponse, QuickReply, ProductInfo
from app.models.agent_types import ProcessedInput, IntentResult, ActionPlan, ToolResults
from app.agents.response_templates import get_response_template
from app.logging_config import get_agent_logger

logger = get_agent_logger("ResponseGenerator")

class ResponseGenerator:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=GOOGLE_API_KEY,
            base_url=GEMINI_BASE_URL
        )
        self.context_config = self._load_context_config()

    def _load_context_config(self):
        try:
            path = os.path.join(os.path.dirname(__file__), "..", "context_config.yaml")
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading context_config: {e}")
            return {}

    async def run(
        self, 
        processed: ProcessedInput, 
        intent: IntentResult, 
        plan: ActionPlan, 
        tool_res: Optional[ToolResults]
    ) -> ChatResponse:
        
        logger.info(f"Generating response - intent={intent.intent} has_tool_result={tool_res is not None}")
        
        # 1. Generate Text Response
        response_text = await self._generate_llm_response(processed, intent, tool_res)
        
        # 2. Generate Quick Replies (Options)
        quick_replies = self._generate_quick_replies(processed)
        
        # 3. Format Products if available
        products = []
        if tool_res and tool_res.ok and isinstance(tool_res.data, list):
            for item in tool_res.data:
                # Try to map to ProductInfo
                try:
                    # If item is already ProductInfo, append directly
                    if isinstance(item, ProductInfo):
                        products.append(item)
                    # Handle if item is dict
                    elif isinstance(item, dict):
                        # Filter keys that match ProductInfo
                        valid_keys = ProductInfo.model_fields.keys()
                        filtered = {k: v for k, v in item.items() if k in valid_keys}
                        # Ensure required fields
                        if "id" in filtered and "title" in filtered and "handle" in filtered:
                            products.append(ProductInfo(**filtered))
                    # Handle if item is object
                    elif hasattr(item, "id") and hasattr(item, "title"):
                        # Manually map variants if they exist in the object but weren't automatically mapped
                        variants = getattr(item, "variants", [])
                        # If variants are already ProductVariantInfo objects, use them.
                        # If they are dicts, convert them.
                        mapped_variants = []
                        for v in variants:
                            if isinstance(v, dict):
                                mapped_variants.append(v) # Pydantic will handle dict -> model
                            else:
                                mapped_variants.append(v)

                        products.append(ProductInfo(
                            id=item.id,
                            title=item.title,
                            handle=item.handle,
                            thumbnail=getattr(item, "thumbnail", None),
                            price=getattr(item, "price", None),
                            currency_code=getattr(item, "currency_code", None),
                            variants=mapped_variants
                        ))
                except Exception as e:
                    logger.warning(f"Failed to map product item: {e}")
        
        # Add product-specific quick replies if products found
        if products:
            # Add "Buy Now" button first
            quick_replies.insert(0, QuickReply(label="Mua ngay", value=f"Đặt hàng {products[0].title}", metadata={"type": "action"}))
            # Add "View Details" button second
            quick_replies.insert(1, QuickReply(label="Xem chi tiết", value=f"Chi tiết {products[0].title}", metadata={"type": "action"}))

        # Add order-specific quick replies if orders found
        if intent.intent in ["order_track", "order_tracking", "order_list"] and tool_res and tool_res.ok and isinstance(tool_res.data, list):
             for order in tool_res.data[:3]: # Limit to 3
                 oid = order.get("id")
                 display_id = order.get("display_id", oid)
                 # Use full ID for value to ensure lookup works
                 quick_replies.append(QuickReply(label=f"Đơn #{display_id}", value=f"Tra cứu đơn hàng {oid}", metadata={"type": "action"}))

        # Check for new cart action
        action = None
        if intent.entities.get("new_cart_id"):
            # Create ChatAction for updating cart
            # We need to import ChatAction and ChatActionType if not already imported
            # But since we are returning ChatResponse which expects ChatAction, we should construct it properly
            # Assuming ChatAction is imported or available via api_models
            from app.models.api_models import ChatAction, ChatActionType
            action = ChatAction(
                type=ChatActionType.API_CALL,
                payload={"command": "update_cart", "cart_id": intent.entities['new_cart_id']}
            )

        logger.info(f"Response generated - text_length={len(response_text)} products={len(products)} quick_replies={len(quick_replies)}")
        return ChatResponse(
            response=response_text,
            session_id=processed.session_id,
            products=products,
            quick_replies=quick_replies,
            metadata={"intent": intent.intent},
            action=action
        )

    async def _generate_llm_response(self, processed, intent, tool_res) -> str:
        # Try template-based response first for common cases
        template_context = {}
        
        logger.debug(f"Template routing - intent={intent.intent} tool_ok={tool_res.ok if tool_res else 'N/A'} data_count={len(tool_res.data) if tool_res and tool_res.ok else 0}")
        
        # PRIORITY 1: Handle FAQ intents with templates (avoid LLM hallucination)
        if intent.intent in ["faq_shipping", "faq_payment", "faq_return", "faq_promo"]:
            logger.info(f"Using FAQ template - intent={intent.intent}")
            return get_response_template(intent.intent)
        
        # PRIORITY 2: Handle thank_you/goodbye
        if intent.intent == "thank_you":
            return get_response_template("thank_you")
        elif intent.intent == "goodbye":
            return get_response_template("goodbye")
        
        if tool_res:
            if tool_res.ok and isinstance(tool_res.data, list):
                template_context['count'] = len(tool_res.data)
                if len(tool_res.data) > 0:
                    first_item = tool_res.data[0]
                    if isinstance(first_item, dict):
                        template_context['product'] = first_item.get('title', '')
                        template_context['order_id'] = first_item.get('display_id') or first_item.get('id')
                        template_context['status'] = self._translate_status(first_item.get('status', 'pending'))
                        template_context['total'] = self._format_price(first_item.get('total'), first_item.get('currency_code'))
                        template_context['delivery_date'] = "Dự kiến 2-3 ngày tới"
                        
                        # Format items for order
                        items = first_item.get('items', [])
                        if items:
                            item_names = [i.get('title') for i in items if isinstance(i, dict)]
                            template_context['items'] = ", ".join(item_names[:3]) + ("..." if len(item_names) > 3 else "")
                        else:
                            template_context['items'] = "Đang cập nhật"
                    elif hasattr(first_item, 'title'):
                        template_context['product'] = first_item.title
            else:
                # tool_res.ok = False means tool failed/no results
                template_context['count'] = 0
        
        # PRIORITY 3: Handle specific intents with templates
        if intent.intent == "general" and (not tool_res or not tool_res.ok):
            logger.info("Using greeting template")
            return get_response_template("greeting")
            
        elif intent.intent in ["order_track", "order_tracking"]:
            if tool_res and tool_res.ok and template_context.get('count', 0) > 0:
                return get_response_template("order_found", template_context)
            else:
                template_context['order_id'] = intent.entities.get("order_id", "của bạn")
                return get_response_template("order_not_found", template_context)

        elif intent.intent in ["product_inquiry", "product_detail"]:
            # Get product query from entities (may be set by executor)
            query = intent.entities.get("product_query")
            if query:
                template_context['query'] = query
            else:
                # Fallback: extract from processed text
                template_context['query'] = "sản phẩm bạn cần"
            
            if template_context.get('count', 0) > 0:
                logger.info(f"Using product_found template - count={template_context['count']}")
                return get_response_template("product_found", template_context)
            else:
                # Product not found - use template to avoid LLM hallucination
                logger.info(f"Using product_not_found template - query={template_context.get('query')}")
                return get_response_template("product_not_found", template_context)
        elif intent.intent == "product_recommend":
            if tool_res and tool_res.ok and template_context.get('count', 0) > 0:
                return get_response_template("product_recommend")
            else:
                return "Xin lỗi, shop đang cập nhật sản phẩm. Bạn quay lại sau nhé!"
        elif intent.intent == "cart_add":
            if tool_res and tool_res.ok:
                # Try to get product title from entities if not in template_context
                if 'product' not in template_context and intent.entities.get("product_title"):
                    template_context['product'] = intent.entities.get("product_title")
                return get_response_template("cart_added", template_context)
            else:
                return "Xin lỗi, tôi cần biết sản phẩm nào bạn muốn thêm vào giỏ hàng."
        
        # PRIORITY 4: Fallback to LLM only for complex cases
        # But prevent hallucination by checking tool_res.ok
        if tool_res and not tool_res.ok:
            # Tool failed - don't let LLM make up data
            logger.warning(f"Tool execution failed - errors={tool_res.errors}")
            if intent.intent in ["product_inquiry", "product_detail"]:
                return get_response_template("product_not_found", template_context)
            return "Xin lỗi, tôi không tìm thấy thông tin bạn cần. Bạn có thể hỏi lại được không?"
        
        # Construct prompt for LLM (only when tool succeeded or no tool needed)
        logger.info("Using LLM for response generation")
        context_str = ""
        if tool_res:
            if tool_res.ok:
                # Truncate data if too large
                data_str = json.dumps(tool_res.data, ensure_ascii=False, default=str)
                if len(data_str) > 3000: # Increased limit for better context
                    data_str = data_str[:3000] + "...(truncated)"
                context_str = f"Tool Result: {data_str}"
            else:
                context_str = f"Tool Error: {tool_res.errors}"
        
        # Add currency hint if available in tool result (e.g. from product search)
        currency_hint = ""
        if tool_res and tool_res.ok and isinstance(tool_res.data, list) and len(tool_res.data) > 0:
            first_item = tool_res.data[0]
            if isinstance(first_item, dict) and "currency_code" in first_item:
                 currency_hint = f"\nLưu ý: Đơn vị tiền tệ đang sử dụng là {first_item.get('currency_code', 'N/A').upper()}."
            elif hasattr(first_item, "currency_code"):
                 currency_hint = f"\nLưu ý: Đơn vị tiền tệ đang sử dụng là {getattr(first_item, 'currency_code', 'N/A').upper()}."

        messages: List[ChatCompletionSystemMessageParam | ChatCompletionUserMessageParam] = [
            ChatCompletionSystemMessageParam(role="system", content=SYSTEM_PROMPT_VI + currency_hint),
            ChatCompletionUserMessageParam(role="user", content=f"User Input: {processed.text}\nIntent: {intent.intent}\nContext: {context_str}")
        ]
        
        try:
            completion = await self.client.chat.completions.create(
                model=GEMINI_MODEL,
                messages=messages,
                temperature=0.7
            )
            return completion.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"LLM Error: {e}")
            if "429" in str(e):
                return "Xin lỗi, hệ thống đang quá tải (Quota Exceeded). Vui lòng thử lại sau."
            return get_response_template("error_generic")

    def _translate_status(self, status: str) -> str:
        mapping = {
            "pending": "⏳ Đang chờ xử lý",
            "completed": "✅ Đã hoàn thành",
            "shipped": "🚚 Đang giao hàng",
            "canceled": "❌ Đã hủy",
            "archived": "📦 Đã lưu trữ",
            "requires_action": "⚠️ Cần xử lý",
            "processing": "⚙️ Đang xử lý"
        }
        return mapping.get(status.lower(), status)

    def _format_price(self, amount: Optional[float], currency: Optional[str]) -> str:
        if amount is None:
            return "Liên hệ"
        
        curr = (currency or "VND").upper()
        if curr == "VND":
            return f"{int(amount):,}₫".replace(",", ".")
        elif curr == "USD":
            return f"${amount:,.2f}"
        elif curr == "EUR":
            return f"{amount:,.2f}€"
        return f"{amount:,.2f} {curr}"

    def _generate_quick_replies(self, processed) -> List[QuickReply]:
        nodes = self.context_config.get("nodes", [])
        
        # Helper to find node by ID recursively
        def find_node(node_list, target_id):
            for node in node_list:
                if node.get("id") == target_id:
                    return node
                if "children" in node:
                    found = find_node(node["children"], target_id)
                    if found: return found
            return None

        # Determine current context node
        current_node = None
        if processed.tag:
            # If tag is like "action:view_cart", we might not find a node if it's a leaf.
            # But if tag is a group ID, we might.
            # Let's try to find by ID first (assuming tag might be ID)
            current_node = find_node(nodes, processed.tag)
        
        # If no specific node found, default to user root
        if not current_node:
            user_root_id = f"{processed.user_type}_root"
            current_node = find_node(nodes, user_root_id)

        if not current_node:
            return []

        options = []
        # Return children of the current node
        for child in current_node.get("children", []):
            # Determine value: prefer value, then tag, then id
            val = child.get("value") or child.get("tag") or child.get("id")
            options.append(QuickReply(
                label=child["label"],
                value=val,
                metadata={"type": child.get("type")}
            ))
            
        return options
