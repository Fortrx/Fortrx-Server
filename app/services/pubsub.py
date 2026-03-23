import json
import redis.asyncio as aioredis
from app.config import settings

def get_redis():
    return aioredis.from_url(settings.REDIS_URL,decode_responses=True)

async def publish_message(user_id:int,payload:dict):
    r = get_redis()
    channel = f"user:{user_id}"
    await r.publish(channel,json.dumps(payload))
    await r.aclose()
    
async def subscribe_to_user(user_id:int):
    r = get_redis()
    pubsub = r.pubsub()
    await pubsub.subscribe(f"user:{user_id}")
    return pubsub,r

async def unsubscribe_from_user(pubsub,r):
    await pubsub.unsubscribe()
    await pubsub.close()
    await r.close()