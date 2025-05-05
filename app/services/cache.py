import redis.asyncio as redis
import os, json, hashlib

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def generate_cache_key(params: dict):
    key_string = json.dumps(params, sort_keys=True)
    return hashlib.sha256(key_string.encode()).hexdigest()
