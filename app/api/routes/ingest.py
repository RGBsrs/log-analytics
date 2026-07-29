
from webbrowser import get

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from pydantic import BaseModel, Field

from app.schemas.log_entry import LogEntryCreate
from app.services.kafka_service import KafkaProducerService
from app.services.log_entry_service import LogEntryService, get_log_entry_service
from app.services.mock_generator import generate_log_entries

router = APIRouter(prefix="/ingest", tags=["Ingest"])


class BatchIngestRequest(BaseModel):
    logs: list[LogEntryCreate]

class MockIngestRequest(BaseModel):
    count: int = Field(default=100, ge=1, le=10000)
    source_id: str | None = None



@router.post("/", status_code=202)
async def ingest_logs(request: Request, data: BatchIngestRequest, service: LogEntryService = Depends(get_log_entry_service)):
    producer = request.app.state.kafka_producer
    producer_service = KafkaProducerService(producer)
    for log in data.logs:
        await producer_service.send_log(log)
    return {"queued": len(data.logs)}

@router.post("/mock", status_code=201)
async def mock_ingest(request: MockIngestRequest, service: LogEntryService = Depends(get_log_entry_service)):
    logs = generate_log_entries(request.count, source_id=request.source_id)
    await service.index_log_entry_bulk(logs)
    return {"indexed": len(logs), "source_id": request.source_id}


@router.post("/mock/bg", status_code=201)
async def mock_ingest_bg(request: MockIngestRequest, background_tasks: BackgroundTasks, service: LogEntryService = Depends(get_log_entry_service)):
    logs = generate_log_entries(request.count, source_id=request.source_id)
    background_tasks.add_task(service.index_log_entry_bulk, logs)
    return {"queued": len(logs), "source_id": request.source_id}
