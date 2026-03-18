import dramatiq
from dramatiq.brokers.redis import RedisBroker
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
broker = RedisBroker(url=REDIS_URL)
dramatiq.set_broker(broker)

@dramatiq.actor
def process_document(document_id):
	# Placeholder for document processing logic
	print(f"Processing document {document_id}")
