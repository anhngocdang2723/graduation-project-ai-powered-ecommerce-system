from typing import Optional, Dict, Any, List
import re
import asyncpg

from app.models import ChatRequest
from app.models.agent_types import ProcessedInput, SessionContext
from app.logging_config import get_agent_logger

logger = get_agent_logger("InputProcessor")


def _normalize_text(text: str) -> str:
    # Trim, collapse spaces; keep diacritics (for VI) and punctuation minimally
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


def _detect_language_heuristic(text: str) -> str:
    t = text.lower()
    # Very lightweight heuristic: VI keywords/diacritics vs common EN markers
    if any(ch in t for ch in "ăâêôơưđáàảãạấầẩẫậắằẳẵặéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ"):
        return "vi"
    if any(word in t for word in [" the ", " and ", " price ", " order ", " product ", " hello "]):
        return "en"
    # Fallback: prefer VI as primary market
    return "vi"


async def _fetch_session_context(pool: Optional[asyncpg.Pool], session_id: str) -> SessionContext:
    ctx = SessionContext()
    if not pool:
        return ctx
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT role, content, intent, response_time_ms, metadata, created_at
                FROM chatbot.messages
                WHERE session_id = $1
                ORDER BY created_at DESC
                LIMIT 10
                """,
                session_id,
            )
            msgs: List[Dict[str, Any]] = []
            prod_ids: List[str] = []
            for r in rows:
                meta = r["metadata"] if r["metadata"] else None
                msgs.append(
                    {
                        "role": r["role"],
                        "content": r["content"],
                        "intent": r["intent"],
                        "created_at": r["created_at"].isoformat() if r["created_at"] else None,
                    }
                )
                if meta and isinstance(meta, dict):
                    # Try to extract product ids if present
                    if "product_ids" in meta and isinstance(meta["product_ids"], list):
                        prod_ids.extend([str(x) for x in meta["product_ids"] if x])
            ctx.last_messages = list(reversed(msgs))  # oldest -> newest
            ctx.last_product_ids = list(dict.fromkeys(reversed(prod_ids)))  # preserve order, unique
            logger.debug(f"Context loaded - messages={len(ctx.last_messages)} product_ids={len(ctx.last_product_ids)}")
            # cart_id could be attached to session table later
    except Exception as e:
        logger.error(f"Session context fetch error: {e}")
    return ctx


class InputProcessor:
    async def run(self, req: ChatRequest, pool: Optional[asyncpg.Pool]) -> ProcessedInput:
        logger.info(f"Processing input - session={req.session_id} message_length={len(req.message)}")
        cleaned = _normalize_text(req.message)
        lang = req.language or _detect_language_heuristic(cleaned)
        
        # Determine user_type:
        # 1. Trust metadata if provided (useful for testing or specific FE logic)
        # 2. Infer from customer_id (customer vs guest)
        user_type = "guest"
        if req.metadata and "user_type" in req.metadata:
            user_type = req.metadata["user_type"]
        elif req.customer_id:
            user_type = "customer"
            
        session_ctx = await _fetch_session_context(pool, req.session_id)
        
        # Sync cart_id from metadata if provided (Frontend is source of truth for cart)
        if req.metadata and "cart_id" in req.metadata and req.metadata["cart_id"]:
            frontend_cart_id = req.metadata["cart_id"]
            logger.info(f"Received cart_id from frontend: {frontend_cart_id}")
            if frontend_cart_id != session_ctx.cart_id:
                logger.info(f"Syncing cart_id from frontend: {frontend_cart_id} (was {session_ctx.cart_id})")
                session_ctx.cart_id = frontend_cart_id
        else:
            logger.info("No cart_id received from frontend metadata")
        
        logger.debug(f"Context - last_intent={session_ctx.last_messages[0]['intent'] if session_ctx.last_messages else 'None'} history_count={len(session_ctx.last_messages)}")

        result = ProcessedInput(
            session_id=req.session_id,
            customer_id=req.customer_id,
            text=req.message,
            cleaned_text=cleaned,
            language=lang,
            user_type=user_type,
            tag=req.tag,
            session_ctx=session_ctx,
        )
        
        logger.info(f"Input processed - language={lang} user_type={user_type} tag={req.tag}")
        return result
