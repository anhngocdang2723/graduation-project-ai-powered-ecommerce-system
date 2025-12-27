import asyncio
import json
import time
import asyncpg
from redis.asyncio import Redis
from app.config import (
    DATABASE_URL, 
    REDIS_URL, 
    CHAT_MESSAGE_QUEUE, 
    BATCH_SIZE, 
    BATCH_INTERVAL,
    DB_POOL_MIN_SIZE,
    DB_POOL_MAX_SIZE
)
from app.logging_config import setup_logging, get_agent_logger

# Setup logging for worker
setup_logging(log_level="INFO")
logger = get_agent_logger("worker")

async def run_worker():
    logger.info("Starting Chatbot Message Worker...")
    
    # Connect to Redis
    redis_client = Redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
    
    # Connect to DB
    try:
        db_pool = await asyncpg.create_pool(
            DATABASE_URL, 
            min_size=DB_POOL_MIN_SIZE, 
            max_size=DB_POOL_MAX_SIZE
        )
    except Exception as e:
        logger.error(f"Failed to connect to DB: {e}")
        return

    logger.info("Worker connected to Redis and DB successfully")

    while True:
        try:
            # Fetch a batch of messages
            # lpop count is supported in newer redis, but for compatibility we can loop or use pipeline
            # Or just pop one by one up to BATCH_SIZE
            
            messages = []
            
            # Try to get up to BATCH_SIZE messages
            # We use a pipeline to get them atomically-ish, but lpop is atomic per item
            # To avoid blocking, we can check llen or just loop
            
            # Simple approach: pop until empty or batch full
            for _ in range(BATCH_SIZE):
                try:
                    # Explicitly cast to awaitable if linter is confused, but runtime should be fine.
                    # Using Redis.from_url with redis.asyncio returns an async client.
                    msg_json = await redis_client.lpop(CHAT_MESSAGE_QUEUE)  # type: ignore
                    if not msg_json:
                        break
                    if isinstance(msg_json, str):
                        messages.append(json.loads(msg_json))
                except json.JSONDecodeError:
                    logger.warning("Skipping invalid JSON message")
                    continue
                except Exception as e:
                    logger.error(f"Error fetching from Redis: {e}")
                    break
            
            if messages:
                logger.debug(f"Processing batch - count={len(messages)}")
                async with db_pool.acquire() as conn:
                    async with conn.transaction():
                        for msg in messages:
                            # Handle Session Creation if needed (though usually handled by API)
                            # But here we are just inserting messages.
                            # The API should ensure session exists or we can do upsert here.
                            
                            # We assume session exists or we ignore FK error? 
                            # Ideally API creates session synchronously, messages are async.
                            
                            if msg.get("type") == "message":
                                await conn.execute(
                                    """INSERT INTO chatbot.messages 
                                       (session_id, role, content, intent, response_time_ms, metadata)
                                       VALUES ($1, $2, $3, $4, $5, $6)""",
                                    msg["session_id"],
                                    msg["role"],
                                    msg["content"],
                                    msg.get("intent"),
                                    msg.get("response_time_ms"),
                                    msg.get("metadata")
                                )
            else:
                # No messages, sleep for a bit
                await asyncio.sleep(BATCH_INTERVAL)
                
        except Exception as e:
            logger.error(f"Worker error: {e}", exc_info=True)
            await asyncio.sleep(5) # Backoff on error

if __name__ == "__main__":
    asyncio.run(run_worker())
