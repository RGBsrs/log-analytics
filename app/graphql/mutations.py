import json
import uuid

import strawberry
from strawberry import Info
from app.core.database import session_factory
from app.graphql.types import LogSourceType, LogEntryType, LogSourceInput, LogInput
from app.schemas.log_entry import LogEntryCreate, LogLevel
from app.schemas.log_source import LogSourceCreate
from app.services.log_entry_service import LogEntryService
from app.services.log_source_service import LogSourceService

@strawberry.type
class Mutation:

    @strawberry.mutation
    async def create_log_source(
        self,
        info: Info,
        input: LogSourceInput
    ) -> LogSourceType:
        session = info.context.get("session")
        service = LogSourceService(session)
        log_source_input = LogSourceCreate(
            name=input.name,
            source_type=input.source_type,
            description=input.description,
            is_active=input.is_active)
        log_source = await service.create(log_source_input)
        return LogSourceType(
            id=str(log_source.id),# pyright: ignore[reportArgumentType]
            name=log_source.name,
            source_type=log_source.source_type,
            description=log_source.description,
            is_active=log_source.is_active,
            created_at=log_source.created_at)

    @strawberry.mutation
    async def delete_log_source(
        self,
        info: Info,
        id: strawberry.ID
    ) -> bool:
        session = info.context.get("session")
        service = LogSourceService(session)
        try:
            return await service.delete(uuid.UUID(id))
        except Exception:
            return False

    @strawberry.mutation
    async def index_log_entry(
        self,
        info: Info,
        input: LogInput
    ) -> LogEntryType:
        es = info.context.get("es")
        service = LogEntryService(es)
        log_entry = LogEntryCreate(
            level=LogLevel(input.level),
            message=input.message,
            source_id=input.source_id,
            project=input.project,
            metadata=json.loads(input.metadata) if input.metadata else {}) # pyright: ignore[reportArgumentType]
        log_entry = await service.index_log_entry(log_entry)
        return LogEntryType(
            id=str(log_entry.id),
            level=log_entry.level,
            message=log_entry.message,
            source_id=log_entry.source_id,
            project=log_entry.project,
            timestamp=log_entry.timestamp,
            metadata=log_entry.metadata)  # pyright: ignore[reportArgumentType]
