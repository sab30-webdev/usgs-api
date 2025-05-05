import json
import httpx
from fastapi import HTTPException
from app.logging_config import logger
from app.services.cache import redis_client, generate_cache_key
from app.logging_config import logger
from app.config import USGS_API_URL


async def get_earthquake_data(params: dict):

    cache_key=generate_cache_key(params)
    cached_response=await redis_client.get(cache_key)

    if cached_response:
        logger.info("✅ Cache hit")
        return json.loads(cached_response)


    logger.info("❌ Cache miss")
    logger.info("Fetching from USGS API...")
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(USGS_API_URL, params=params)
            response.raise_for_status()
            data=response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"External API error: {e.response.text}"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Error contacting USGS API: {str(e)}"
        )  

    await redis_client.setex(cache_key,30,json.dumps(data))
    return data