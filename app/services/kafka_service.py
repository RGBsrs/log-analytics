from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from app.core.kafka import LOGS_TOPIC
from app.schemas.log_entry import LogEntryCreate
from app.services.log_entry_service import LogEntryService


class KafkaProducerService:
    def __init__(self, producer: AIOKafkaProducer):
        self.producer = producer

    async def send_log(self, log: LogEntryCreate) -> None:
        await self.producer.send(LOGS_TOPIC, value=log.model_dump(mode="json"))


class KafkaConsumerService:
    def __init__(self, consumer: AIOKafkaConsumer, log_entry_service: LogEntryService):
        self.consumer = consumer
        self.log_entry_service = log_entry_service

    async def consume_logs(self) -> None:
        async for message in self.consumer:
            try:
                log = LogEntryCreate(**message.value)  # pyright: ignore[reportCallIssue]
                await self.log_entry_service.index_log_entry(log)
            except Exception as e:  # noqa: BLE001
                print(f"Error processing log: {e}")
