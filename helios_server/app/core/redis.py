"""Redis connection management for Helios."""

import redis
from typing import Generator

from app.core.config import get_settings


def get_redis_client() -> redis.Redis:
    """Get Redis client instance."""
    settings = get_settings()
    return redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        password=settings.redis_password,
        decode_responses=True
    )


def get_redis_pubsub() -> Generator[redis.client.PubSub, None, None]:
    """Get Redis PubSub instance."""
    redis_client = get_redis_client()
    pubsub = redis_client.pubsub()
    try:
        yield pubsub
    finally:
        pubsub.close()