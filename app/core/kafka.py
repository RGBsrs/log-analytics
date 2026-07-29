import json

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from app.core.config import get_settings

settings = get_settings()

LOGS_TOPIC = "logs.raw"

async def get_producer() -> AIOKafkaProducer:
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode()
    )
    await producer.start()
    return producer

async def get_consumer(topic: str, group_id: str) -> AIOKafkaConsumer:
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=group_id,
        value_deserializer=lambda v: json.loads(v.decode()),
        auto_offset_reset="earliest"
    )
    await consumer.start()
    return consumer
