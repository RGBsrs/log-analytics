import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.log_source import LogSourceCreate, LogSourceRead, LogSourceUpdate
from app.services.log_source_service import LogSourceService

router = APIRouter(prefix="/log-sources", tags=["Log Sources"])

async def get_log_source_service(session: AsyncSession = Depends(get_session)) -> LogSourceService:
    return LogSourceService(session)


@router.get("/", response_model=list[LogSourceRead])
async def get_log_sources(service: LogSourceService = Depends(get_log_source_service)):
    return await service.get_all()


@router.post("/", response_model=LogSourceRead, status_code=status.HTTP_201_CREATED)
async def create_log_source(data: LogSourceCreate, service: LogSourceService = Depends(get_log_source_service)):
    return await service.create(data)


@router.get("/{id}", response_model=LogSourceRead)
async def get_log_source(id: str, service: LogSourceService = Depends(get_log_source_service)):
    log_source = await service.get_by_id(uuid.UUID(id))
    if log_source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log source not found")
    return log_source

@router.patch("/{id}", response_model=LogSourceRead)
async def update_log_source(id: str, data: LogSourceUpdate, service: LogSourceService = Depends(get_log_source_service)):
    return await service.update(data, uuid.UUID(id))

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_log_source(id: str, service: LogSourceService = Depends(get_log_source_service)):
    result = await service.delete(uuid.UUID(id))
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log source not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
