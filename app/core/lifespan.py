import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import get_session
from app.core.elasticsearch import create_es_index, get_es_client
from app.core.kafka import LOGS_TOPIC, get_consumer, get_producer
from app.services.kafka_service import KafkaConsumerService
from app.services.log_entry_service import LogEntryService


@asynccontextmanager
async def lifespan(app: FastAPI):
    es = get_es_client()
    await create_es_index(es)
    producer = await get_producer()
    app.state.kafka_producer = producer
    consumer = await get_consumer(LOGS_TOPIC, group_id="log-analytics")
    consumer_task = None
    async for session in get_session():
        log_service = LogEntryService(es, session)
        consumer_service = KafkaConsumerService(consumer, log_service)
        consumer_task = asyncio.create_task(consumer_service.consume_logs())
        break
    yield
    if consumer_task:
        consumer_task.cancel()
    await producer.stop()
    await consumer.stop()
    await es.close()
    print("Shutting down...")
