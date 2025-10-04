"""Worker entry point for Helios."""

import logging
import os
import sys
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent.parent / "app"
sys.path.insert(0, str(app_dir))

from rq import Worker
from redis import Redis

from app.core.config import get_settings
from app.core.constants import QueueNames


def main():
    """Main worker entry point."""
    settings = get_settings()
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format=settings.log_format
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Helios Worker...")
    
    # Create Redis connection
    redis_conn = Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        password=settings.redis_password
    )
    
    # Create worker with queues
    worker = Worker([QueueNames.HIGH, QueueNames.DEFAULT], connection=redis_conn)
    logger.info(f"Worker started, listening to queues: {QueueNames.HIGH}, {QueueNames.DEFAULT}")
    worker.work()


if __name__ == "__main__":
    main()