from fastapi import APIRouter, Depends, Query  # noqa: I001
from elasticsearch import AsyncElasticsearch
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.elasticsearch import get_es
from app.schemas.log_entry import LogEntryCreate, LogEntryRead, LogLevel
from app.services.log_entry_service import LogEntryService

router = APIRouter(prefix="/logs", tags=["Logs"])

async def get_log_service(
    es_client: AsyncElasticsearch = Depends(get_es),
    session: AsyncSession = Depends(get_session),
) -> LogEntryService:
    return LogEntryService(es_client=es_client, session=session)

@router.post("/", response_model=LogEntryRead, status_code=201)
async def ingest_log_entry(
    data: LogEntryCreate,
    service: LogEntryService = Depends(get_log_service),
):
    return await service.index_log_entry(data)

@router.get("/", response_model=list[LogEntryRead])
async def search_log_entries(
    query: str | None = None,
    level: LogLevel | None = None,
    source_id: str | None = None,
    from_: int = Query(0, alias="from"),
    size: int = Query(20, le=100),
    service: LogEntryService = Depends(get_log_service),
):
    return await service.search_log_entries(query, level, source_id, from_, size)

@router.get("/stats")
async def get_stats(service: LogEntryService = Depends(get_log_service)):
    return await service.get_stats()


@router.delete("/{source_id}", status_code=204)
async def delete_by_source(
    source_id: str,
    service: LogEntryService = Depends(get_log_service),
):
    await service.delete_log(source_id)
