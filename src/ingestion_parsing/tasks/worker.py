"""Dramatiq task queue worker configuration.

This module sets up the Dramatiq broker and worker for asynchronous
document processing tasks.
"""

import dramatiq
from dramatiq.brokers.redis import RedisBroker

import structlog

from config.settings import settings

logger = structlog.get_logger(__name__)

# Initialize Redis broker
redis_broker = RedisBroker(url=settings.task_queue.DRAMATIQ_BROKER_URL)
dramatiq.set_broker(redis_broker)

logger.info(
    "Dramatiq broker initialized",
    broker_url=settings.task_queue.DRAMATIQ_BROKER_URL,
    max_concurrent_jobs=settings.task_queue.MAX_CONCURRENT_PARSING_JOBS,
)


# Task decorators will be added here as we implement specific tasks
# Example:
# @dramatiq.actor(max_retries=3, time_limit=300000)  # 5 minutes
# def parse_document_task(document_id: int) -> None:
#     """Parse document asynchronously."""
#     pass
