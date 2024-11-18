# Redis cache
import json
from functools import wraps
from flask import Response, request, jsonify
import redis
from app.logger_config import setup_logger
from app.performance_monitor import log_duration

logger = setup_logger("Redis Cache")

# Radis connection string (we can use a password to improve security

cache = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)


@log_duration
def redis_cache(redis_key: str, ttl: int = 3600):
    """
    Redis cache decorator
    :param redis_key: key for Redis cache.
    :param ttl: time to live (in seconds). by default 3600 seconds (1 hour).
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 1. cache key generation
            final_key = redis_key
            if request.args:  # Add query-params to key (if needed)
                final_key += ":" + ":".join([f"{k}={v}" for k, v in request.args.items()])

            # 2. check data in cache
            cached_data = cache.get(final_key)
            if cached_data:
                logger.info(f"[Cache Hit] Key: {final_key}")
                # return data in Flask Response format
                return jsonify(json.loads(cached_data))

            logger.info(f"[Cache Miss] Key: {final_key}")
            # 3. Get data from sql database
            response = func(*args, **kwargs)
            # 4. Check response data type
            if isinstance(response, Response):
                # if data in Flask Response format, get data as a string
                response_data = response.get_data(as_text=True)
                cache.set(final_key, response_data, ex=ttl)
            else:
                # if data is a Python Object (list or dictionary)
                cache.set(final_key, json.dumps(response), ex=ttl)

            return response

        return wrapper

    return decorator
