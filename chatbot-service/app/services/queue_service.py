import json
import redis.asyncio as redis
from app.config import REDIS_URL, CHAT_MESSAGE_QUEUE

class QueueService:
    def __init__(self):
        self.redis = redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)

    async def push_message(self, message_data: dict):
        """Push a message to the Redis queue"""
        try:
            await self.redis.rpush(CHAT_MESSAGE_QUEUE, json.dumps(message_data))
        except Exception as e:
            print(f"Error pushing to Redis: {e}")
            # Fallback or retry logic could go here

    async def close(self):
        await self.redis.close()

# Global instance
queue_service = QueueService()
