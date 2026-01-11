"""Dramatiq task queue worker configuration.

This module sets up the Dramatiq broker and worker for asynchronous
document processing tasks.
"""

import dramatiq
from dramatiq.brokers.redis import RedisBroker

import structlog

from src.shared.config import settings

logger = structlog.get_logger(__name__)

# Initialize Redis broker
redis_broker = RedisBroker(url=settings.dramatiq_broker_url)
dramatiq.set_broker(redis_broker)

logger.info(
    "Dramatiq broker initialized",
    broker_url=settings.dramatiq_broker_url,
    max_concurrent_jobs=settings.max_concurrent_parsing_jobs,
)


# Task decorators will be added here as we implement specific tasks
# Example:
# @dramatiq.actor(max_retries=3, time_limit=300000)  # 5 minutes
# def parse_document_task(document_id: int) -> None:
#     """Parse document asynchronously."""
#     pass
