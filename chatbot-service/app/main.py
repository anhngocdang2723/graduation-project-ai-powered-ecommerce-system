from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from openai import OpenAI
import asyncpg
from datetime import datetime
import time
import re
import httpx

# Import config and models
from app.config import (
    GOOGLE_API_KEY,
    GEMINI_BASE_URL,
    GEMINI_MODEL,
    MEDUSA_BACKEND_URL,
    DATABASE_URL,
    AGENTS_ENABLED,
    CORS_ORIGINS,
    DB_POOL_MIN_SIZE,
    DB_POOL_MAX_SIZE,
    LLM_MAX_TOKENS,
    LLM_TEMPERATURE,
    LLM_TIMEOUT,
    get_system_prompt,
    validate_config,
)
from app.models import (
    ChatRequest,
    ChatResponse,
    ChatSession,
    ChatMessage,
    MessageRole,
    SessionStatus,
    ChatAction,
    ChatActionType,
    MedusaProduct,
    product_to_info,
    ContextSuggestionRequest,
    ContextSuggestionResponse,
    ContextNodeDTO,
)
from app.services.context_manager import ContextManager, ContextState, ContextNode
from app.services.queue_service import queue_service
from app.services.medusa_client import MedusaClient
from app.logging_config import setup_logging, get_agent_logger, log_agent_execution

# Setup logging
setup_logging(log_level="INFO", enable_file_logging=True, enable_console_logging=True)
logger = get_agent_logger("main")

# Validate configuration on startup
is_valid, errors = validate_config()
if not is_valid:
    raise RuntimeError(f"Configuration errors: {', '.join(errors)}")

app = FastAPI(title="Medusa Chatbot Agent - Gemini")

# CORS for Frontend & Admin
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Google Gemini Client (OpenAI compatible)
gemini_client = OpenAI(
    api_key=GOOGLE_API_KEY,
    base_url=GEMINI_BASE_URL,
    timeout=LLM_TIMEOUT,
)

MEDUSA_URL = MEDUSA_BACKEND_URL

# Database connection pool
db_pool: Optional[asyncpg.Pool] = None


async def get_db_pool():
    global db_pool
    if db_pool is None:
        try:
            db_pool = await asyncpg.create_pool(
                DATABASE_URL, 
                min_size=DB_POOL_MIN_SIZE, 
                max_size=DB_POOL_MAX_SIZE
            )
        except Exception as e:
            logger.error(f"Database connection error: {e}")
    return db_pool


@app.on_event("startup")
async def startup():
    await get_db_pool()


@app.on_event("shutdown")
async def shutdown():
    global db_pool
    if db_pool:
        await db_pool.close()
    await queue_service.close()


# --- Helper Functions ---
async def search_products(query: str, limit: int = 5) -> List[MedusaProduct]:
    """Search products from Medusa API through MedusaClient"""
    client = MedusaClient()
    try:
        raw_products = await client.search_products(query, limit=limit)
        if not isinstance(raw_products, list):
            return []
        # Convert to MedusaProduct so product_to_info can read attributes
        products = []
        for raw in raw_products:
            if not isinstance(raw, dict):
                continue
            try:
                products.append(MedusaProduct(**raw))
            except Exception as e:
                print(f"Failed to parse product data: {e}")
        return products
    except Exception as e:
        print(f"Error fetching products: {e}")
    return []

SEARCH_STOP_WORDS = {
    "thông", "tin", "sản", "phẩm", "giá", "có", "không", "mua", "đặt", "hàng",
    "thêm", "vào", "với", "cho", "mình", "tôi", "bạn", "xem", "chi", "tiết",
    "cần", "giúp", "tìm", "tư", "vấn", "ngay", "khi", "nào", "còn"
}

def extract_search_keywords(message: str) -> Optional[str]:
    if not message:
        return None
    tokens = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+", message)
    filtered = [token for token in tokens if token.lower() not in SEARCH_STOP_WORDS]
    if not filtered:
        return None
    preferred = [token for token in filtered if any(char.isupper() for char in token)]
    if preferred:
        filtered = preferred
    max_tokens = 2
    if len(filtered) > max_tokens:
        filtered = filtered[-max_tokens:]
    return " ".join(filtered)


async def get_order_status(order_id: str, email: str) -> dict:
    """Get order status from Medusa API"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{MEDUSA_URL}/store/orders",
                params={"display_id": order_id, "email": email}
            )
            if response.status_code == 200:
                data = response.json()
                orders = data.get("orders", [])
                if orders:
                    return orders[0]
        except Exception as e:
            print(f"Error fetching order: {e}")
    return {}


def detect_intent(message: str) -> str:
    """Simple intent detection based on keywords"""
    message_lower = message.lower()
    
    if any(kw in message_lower for kw in ["đơn hàng", "order", "giao hàng", "shipping", "tracking"]):
        return "order_tracking"
    elif any(kw in message_lower for kw in ["mua", "đặt", "thêm vào giỏ", "add to cart", "order"]):
        return "create_order"
    elif any(kw in message_lower for kw in ["sản phẩm", "product", "có", "còn", "giá", "price", "tìm", "search"]):
        return "product_inquiry"
    else:
        return "general"


async def generate_response(message: str, context: str = "", language: str = "vi") -> str:
    """Generate response using Google Gemini"""
    system_prompt = get_system_prompt(language)

    try:
        completion = gemini_client.chat.completions.create(
            model=GEMINI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context: {context}\n\nUser: {message}"},
            ],
            max_tokens=LLM_MAX_TOKENS,
            temperature=LLM_TEMPERATURE,
        )
        content = completion.choices[0].message.content
        return content or "Xin lỗi, không thể tạo phản hồi. Vui lòng thử lại sau."
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return f"Xin lỗi, tôi gặp lỗi khi xử lý. Vui lòng thử lại sau. (Error: {str(e)})"

# --- API Endpoints ---
@app.get("/")
def health_check():
    return {
        "status": "Chatbot Service is running",
        "model": GEMINI_MODEL,
        "medusa_url": MEDUSA_URL,
        "agents_enabled": AGENTS_ENABLED,
        "config_valid": True
    }


async def _legacy_chat_flow(request: ChatRequest) -> ChatResponse:
    """Current chat flow kept intact to avoid behavior change."""
    start_time = time.time()
    message = request.message
    language = request.language or "vi"
    intent = detect_intent(message)
    context = ""
    products = None
    actions = []

    # Handle different intents
    if intent == "product_inquiry":
        search_terms = message.replace("có", "").replace("không", "").replace("?", "").strip()
        products_raw = await search_products(search_terms)
        if not products_raw:
            fallback_query = extract_search_keywords(message)
            if fallback_query and fallback_query != search_terms:
                print(f"[Legacy Chat] Falling back to '{fallback_query}' for search")
                products_raw = await search_products(fallback_query)
        
        if products_raw:
            # Convert to ProductInfo
            products = [product_to_info(p) for p in products_raw[:5]]
            context = f"Tìm thấy {len(products)} sản phẩm: " + ", ".join(
                [f"{p.title} - {p.price or 'N/A'}" for p in products[:3]]
            )
            actions = [ChatAction(type=ChatActionType.SHOW_PRODUCTS, payload={"count": len(products)})]
        else:
            context = "Không tìm thấy sản phẩm phù hợp."

    elif intent == "order_tracking":
        context = "Để tra cứu đơn hàng, khách hàng cần cung cấp mã đơn hàng và email."
        actions = [ChatAction(type=ChatActionType.REQUEST_ORDER_INFO, payload={})]

    elif intent == "create_order":
        context = "Khách hàng muốn đặt hàng. Hướng dẫn họ thêm sản phẩm vào giỏ hàng."
        actions = [ChatAction(type=ChatActionType.GUIDE_TO_CART, payload={})]

    # Generate AI response
    response_text = await generate_response(message, context, language)
    response_time = int((time.time() - start_time) * 1000)

    # Save messages to Queue
    try:
        import json
        
        # Prepare product metadata for context restoration
        product_ids = []
        products_for_metadata = []
        if products:
            for p in products:
                if hasattr(p, "id"):
                    product_ids.append(p.id)
                if hasattr(p, "dict"):
                    products_for_metadata.append(p.dict())
        
        # User message
        await queue_service.push_message({
            "type": "message",
            "session_id": request.session_id,
            "role": MessageRole.USER.value,
            "content": message,
            "metadata": json.dumps({"intent": intent})
        })
        
        # Assistant response with full context data
        assistant_metadata = {
            "intent": intent,
            "products": products_for_metadata,  # Full product data for UI restoration
            "product_ids": product_ids  # IDs for backend context
        }
        
        await queue_service.push_message({
            "type": "message",
            "session_id": request.session_id,
            "role": MessageRole.ASSISTANT.value,
            "content": response_text,
            "response_time_ms": response_time,
            "metadata": json.dumps(assistant_metadata)
        })
    except Exception as e:
        print(f"Queue error saving messages: {e}")

    # Convert actions (ChatAction objects) to JSON-friendly quick_replies for compatibility
    quick_replies_out = []
    for a in actions:
        # Support enum types and plain values
        action_type = getattr(getattr(a, "type", None), "value", getattr(a, "type", None))
        quick_replies_out.append({
            "type": action_type,
            "payload": getattr(a, "payload", None)
        })

    return ChatResponse(
        response=response_text,
        session_id=request.session_id,
        products=products or [],
        quick_replies=quick_replies_out
    )


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint with feature-flagged agent pipeline."""
    # Ensure session exists in DB FIRST (both agent and legacy flow need this)
    pool = await get_db_pool()
    if pool:
        try:
            async with pool.acquire() as conn:
                # Check if session exists
                session = await conn.fetchrow(
                    "SELECT id FROM chatbot.sessions WHERE session_id = $1",
                    request.session_id
                )
                if not session:
                    # Create new session
                    await conn.execute(
                        """INSERT INTO chatbot.sessions (session_id, customer_id, customer_email, status)
                           VALUES ($1, $2, $3, $4)""",
                        request.session_id, request.customer_id, None, SessionStatus.ACTIVE.value
                    )
                    logger.info(f"Created new chat session: {request.session_id}")
        except Exception as e:
            logger.error(f"DB error creating session: {e}")
    
    if AGENTS_ENABLED:
        start_time = time.time()
        products = None
        actions: List[ChatAction] = []
        try:
            # Step 1: Input Processor
            from app.agents.input_processor import InputProcessor
            processed = await InputProcessor().run(request, pool)
            logger.info(f"[AGENT-1:InputProcessor] session={processed.session_id} language={processed.language} user_type={processed.user_type} cleaned_text='{processed.cleaned_text[:50]}...'")

            # Step 2: Intent Classifier
            from app.agents.intent_classifier import IntentClassifier
            intent_res = await IntentClassifier().run(processed)
            logger.info(f"[AGENT-2:IntentClassifier] intent={intent_res.intent} confidence={intent_res.confidence:.2f} entities={intent_res.entities}")

            # Step 3: Orchestrator (plan only)
            from app.agents.orchestrator import Orchestrator
            plan, _ = await Orchestrator().run(processed, intent_res)
            logger.info(f"[AGENT-3:Orchestrator] action_plan={plan.dict()}")

            # Step 4: Executor (run tools based on plan)
            from app.agents.executor import Executor
            tool_res = await Executor().run(processed, intent_res, plan)
            if tool_res is not None:
                if tool_res.ok:
                    data_summary = f"type={type(tool_res.data).__name__}, count={len(tool_res.data) if isinstance(tool_res.data, list) else 1}"
                    logger.info(f"[AGENT-4:Executor] Tool execution SUCCESS - {data_summary}")
                else:
                    logger.warning(f"[AGENT-4:Executor] Tool execution FAILED - errors={tool_res.errors}")

            # Step 5: Response Generator
            from app.agents.response_generator import ResponseGenerator
            agent_response: ChatResponse = await ResponseGenerator().run(
                processed, intent_res, plan, tool_res
            )
            logger.info(f"[AGENT-5:ResponseGenerator] Generated response - products_count={len(agent_response.products)} response_length={len(agent_response.response)}")

            # Persist messages (mirror legacy behavior)
            response_time = int((time.time() - start_time) * 1000)
            logger.info(f"[PIPELINE] Complete - session={request.session_id} total_time={response_time}ms intent={intent_res.intent}")
            
            # Extract products for metadata
            products_meta = []
            product_ids = []
            if tool_res and tool_res.ok and isinstance(tool_res.data, list) and intent_res.intent == "product_inquiry":
                products_meta = tool_res.data
            elif agent_response.products:
                products_meta = agent_response.products
            
            if products_meta:
                # Extract IDs for context
                for p in products_meta:
                    if isinstance(p, dict):
                        if "id" in p: product_ids.append(p["id"])
                    elif hasattr(p, "id"):
                        product_ids.append(p.id)
                
                # Convert ProductInfo to dict for JSON serialization
                products_for_json = []
                for p in products_meta:
                    if isinstance(p, dict):
                        products_for_json.append(p)
                    elif hasattr(p, "dict"):
                        products_for_json.append(p.dict())
                    else:
                        products_for_json.append({"id": getattr(p, "id", "unknown"), "title": getattr(p, "title", "")})
                products_meta = products_for_json

            try:
                import json
                # User message
                await queue_service.push_message({
                    "type": "message",
                    "session_id": request.session_id,
                    "role": MessageRole.USER.value,
                    "content": request.message,
                    "metadata": json.dumps({"intent": intent_res.intent})
                })
                
                # Save full product data in metadata for history restoration
                # AND product_ids for context context restoration
                meta_data = {"products": products_meta, "product_ids": product_ids}
                meta_json = json.dumps(meta_data)
                
                # Assistant response (include intent into metadata)
                meta_with_intent = {"intent": intent_res.intent, "products": products_meta, "product_ids": product_ids}
                meta_json_with_intent = json.dumps(meta_with_intent)
                await queue_service.push_message({
                    "type": "message",
                    "session_id": request.session_id,
                    "role": MessageRole.ASSISTANT.value,
                    "content": agent_response.response,
                    "response_time_ms": response_time,
                    "metadata": meta_json_with_intent
                })
            except Exception as e:
                logger.error(f"Queue error saving agent messages: {e}")

            return agent_response
        except Exception as e:
            logger.error(f"Agent pipeline error: {e}", exc_info=True)
            # Fallback to legacy flow to keep responses stable
            return await _legacy_chat_flow(request)
    else:
        return await _legacy_chat_flow(request)


# --- Context API ---
@app.post("/chat/suggestions", response_model=ContextSuggestionResponse)
async def get_context_suggestions(request: ContextSuggestionRequest):
    """Get context-aware suggestions for UI"""
    context_manager = ContextManager()
    
    state = ContextState(
        user_id=request.customer_id,
        user_type=request.user_type,
        current_tag=request.tag,
        current_intent=request.intent
    )
    
    nodes = context_manager.get_suggestions(state)
    
    def map_node(node: ContextNode) -> ContextNodeDTO:
        children_dtos = []
        # We only return children if they are visible? 
        # get_suggestions already filters top-level. 
        # But if the UI wants a tree, we might need to recurse.
        # For now, let's just map the top level returned by get_suggestions.
        # If the node has children, we map them too?
        # The current get_suggestions returns a flat list of "next available options".
        # But some might be groups.
        
        if node.children:
             # Filter visible children for the DTO
             visible = [c for c in node.children if c.is_visible(state)]
             if visible:
                 children_dtos = [map_node(c) for c in visible]

        return ContextNodeDTO(
            id=node.id,
            label=node.label,
            tag=node.tag,
            type=node.type,
            value=node.value,
            children=children_dtos
        )

    dtos = [map_node(n) for n in nodes]
    return ContextSuggestionResponse(suggestions=dtos)


@app.get("/chat/history/{session_id}")
async def get_public_chat_history(session_id: str):
    """Get chat history for a session (public/user facing)"""
    pool = await get_db_pool()
    if not pool:
        return {"messages": []}
    
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """SELECT id, role, content, created_at, metadata 
                   FROM chatbot.messages
                   WHERE session_id = $1
                   ORDER BY created_at ASC""",
                session_id
            )
            
            messages = []
            for row in rows:
                products = []
                if row["metadata"]:
                    try:
                        import json
                        # metadata is already a dict if using asyncpg with jsonb, or str?
                        # asyncpg usually decodes jsonb automatically to dict
                        meta = row["metadata"]
                        if isinstance(meta, str):
                            meta = json.loads(meta)
                        
                        if isinstance(meta, dict) and "products" in meta:
                            products = meta["products"]
                    except Exception:
                        pass

                messages.append({
                    "id": str(row["id"]),
                    "role": row["role"],
                    "content": row["content"],
                    "timestamp": row["created_at"].isoformat() if row["created_at"] else None,
                    "products": products
                })
            return {"messages": messages}
    except Exception as e:
        print(f"Error fetching history: {e}")
        return {"messages": []}


@app.get("/chat/session/active/{customer_id}")
async def get_active_session(customer_id: str):
    """Get active session for a customer"""
    pool = await get_db_pool()
    if not pool:
        return {"session_id": None}
    
    try:
        async with pool.acquire() as conn:
            # Find the most recent active session
            row = await conn.fetchrow(
                """SELECT session_id FROM chatbot.sessions 
                   WHERE customer_id = $1 AND status = 'active'
                   ORDER BY updated_at DESC LIMIT 1""",
                customer_id
            )
            if row:
                print(f"[SessionAPI] Found active session for customer {customer_id}: {row['session_id']}")
                return {"session_id": row["session_id"]}
            print(f"[SessionAPI] No active session found for customer {customer_id}")
            return {"session_id": None}
    except Exception as e:
        print(f"Error fetching active session: {e}")
        return {"session_id": None}


@app.post("/chat/session/clear/{session_id}")
async def clear_session_history(session_id: str):
    """Clear chat history for a session (for testing/demo purposes)"""
    pool = await get_db_pool()
    if not pool:
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        async with pool.acquire() as conn:
            # Delete all messages for this session
            deleted = await conn.execute(
                "DELETE FROM chatbot.messages WHERE session_id = $1",
                session_id
            )
            print(f"[SessionAPI] Cleared {deleted} messages from session {session_id}")
            return {"session_id": session_id, "cleared": True, "message": "History cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Admin Endpoints ---
@app.get("/admin/sessions")
async def get_sessions(limit: int = 50, offset: int = 0, status: Optional[str] = None):
    """Get chat sessions list for admin"""
    pool = await get_db_pool()
    if not pool:
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        async with pool.acquire() as conn:
            if status:
                rows = await conn.fetch(
                    """SELECT s.*, 
                              (SELECT COUNT(*) FROM chatbot.messages m WHERE m.session_id = s.session_id) as message_count,
                              (SELECT MAX(created_at) FROM chatbot.messages m WHERE m.session_id = s.session_id) as last_message,
                              (SELECT intent FROM chatbot.messages m WHERE m.session_id = s.session_id ORDER BY created_at DESC LIMIT 1) as last_intent
                       FROM chatbot.sessions s
                       WHERE s.status = $1
                       ORDER BY s.updated_at DESC
                       LIMIT $2 OFFSET $3""",
                    status, limit, offset
                )
            else:
                rows = await conn.fetch(
                    """SELECT s.*, 
                              (SELECT COUNT(*) FROM chatbot.messages m WHERE m.session_id = s.session_id) as message_count,
                              (SELECT MAX(created_at) FROM chatbot.messages m WHERE m.session_id = s.session_id) as last_message,
                              (SELECT intent FROM chatbot.messages m WHERE m.session_id = s.session_id ORDER BY created_at DESC LIMIT 1) as last_intent
                       FROM chatbot.sessions s
                       ORDER BY s.updated_at DESC
                       LIMIT $1 OFFSET $2""",
                    limit, offset
                )
            
            sessions = []
            for row in rows:
                sessions.append({
                    "id": row["id"],
                    "session_id": row["session_id"],
                    "customer_id": row["customer_id"],
                    "customer_email": row["customer_email"],
                    "status": row["status"],
                    "message_count": row["message_count"],
                    "last_message": row["last_message"].isoformat() if row["last_message"] else None,
                    "last_intent": row["last_intent"],
                    "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                    "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
                })
            return {"sessions": sessions, "total": len(sessions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin/sessions/{session_id}/messages")
async def get_session_messages(session_id: str):
    """Get messages for a specific session"""
    pool = await get_db_pool()
    if not pool:
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """SELECT * FROM chatbot.messages
                   WHERE session_id = $1
                   ORDER BY created_at ASC""",
                session_id
            )
            
            import json
            messages = []
            for row in rows:
                msg_data = {
                    "id": row["id"],
                    "session_id": row["session_id"],
                    "role": row["role"],
                    "content": row["content"],
                    "intent": row["intent"],
                    "response_time_ms": row["response_time_ms"],
                    "timestamp": row["created_at"].isoformat() if row["created_at"] else None,
                }
                
                # Parse metadata to extract products
                if row.get("metadata"):
                    try:
                        metadata = json.loads(row["metadata"]) if isinstance(row["metadata"], str) else row["metadata"]
                        if metadata and "products" in metadata:
                            msg_data["products"] = metadata["products"]
                    except:
                        pass
                
                messages.append(msg_data)
            return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin/stats")
async def get_stats():
    """Get chatbot statistics for admin dashboard"""
    pool = await get_db_pool()
    if not pool:
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        async with pool.acquire() as conn:
            total_sessions = await conn.fetchval("SELECT COUNT(*) FROM chatbot.sessions")
            active_sessions = await conn.fetchval("SELECT COUNT(*) FROM chatbot.sessions WHERE status = 'active'")
            escalated_sessions = await conn.fetchval("SELECT COUNT(*) FROM chatbot.sessions WHERE status = 'waiting_for_staff'")
            total_messages = await conn.fetchval("SELECT COUNT(*) FROM chatbot.messages")
            avg_response_time = await conn.fetchval(
                "SELECT AVG(response_time_ms) FROM chatbot.messages WHERE role = 'assistant'"
            )
            
            return {
                "total_sessions": total_sessions or 0,
                "active_sessions": active_sessions or 0,
                "escalated_sessions": escalated_sessions or 0,
                "total_messages": total_messages or 0,
                "avg_response_time_ms": round(avg_response_time or 0, 2)
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/admin/sessions/{session_id}/status")
async def update_session_status(session_id: str, status: str):
    """Update session status (active, closed, archived)"""
    pool = await get_db_pool()
    if not pool:
        raise HTTPException(status_code=500, detail="Database not available")
    
    if status not in ["active", "closed", "archived"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE chatbot.sessions SET status = $1, updated_at = NOW() WHERE session_id = $2",
                status, session_id
            )
            return {"session_id": session_id, "status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin/settings")
async def get_settings():
    """Get chatbot settings"""
    pool = await get_db_pool()
    if not pool:
        return {"model": "qwen-max", "auto_order": False, "enabled": True}
    
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT key, value FROM chatbot.settings")
            settings = {row["key"]: row["value"] for row in rows}
            return settings if settings else {"model": "qwen-max", "auto_order": "false", "enabled": "true"}
    except Exception as e:
        return {"model": "qwen-max", "auto_order": False, "enabled": True}


@app.patch("/admin/settings")
async def update_settings(settings: dict):
    """Update chatbot settings"""
    pool = await get_db_pool()
    if not pool:
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        async with pool.acquire() as conn:
            for key, value in settings.items():
                await conn.execute(
                    """INSERT INTO chatbot.settings (key, value)
                       VALUES ($1, $2)
                       ON CONFLICT (key) DO UPDATE SET value = $2, updated_at = NOW()""",
                    key, str(value)
                )
            return {"status": "updated", "settings": settings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/escalate")
async def escalate_to_staff(request: dict):
    """Handle staff escalation request"""
    session_id = request.get("session_id")
    reason = request.get("reason", "User requested staff support")
    
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id required")
    
    pool = await get_db_pool()
    if not pool:
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        async with pool.acquire() as conn:
            # Update session status to waiting_for_staff
            await conn.execute(
                """UPDATE chatbot.sessions 
                   SET status = $1, metadata = jsonb_set(COALESCE(metadata, '{}'), '{escalation_reason}', $2::jsonb)
                   WHERE session_id = $3""",
                "waiting_for_staff",
                f'"{reason}"',
                session_id
            )
            
            # Log escalation message
            await queue_service.push_message({
                "type": "message",
                "session_id": session_id,
                "role": MessageRole.SYSTEM.value,
                "content": f"User requested staff support: {reason}",
                "metadata": '{"intent": "staff_escalation"}'
            })
        
        return {
            "status": "escalated",
            "message": "Yêu cầu của bạn đã được chuyển đến nhân viên hỗ trợ. Vui lòng chờ trong giây lát, nhân viên sẽ liên hệ với bạn sớm nhất có thể. 🧑‍💼",
            "session_id": session_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))