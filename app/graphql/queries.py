import uuid

import strawberry
from strawberry.types import Info

from app.graphql.types import LogEntryType, LogSourceType, LogStatsType, LogFilterInput
from app.services.log_entry_service import LogEntryService
from app.services.log_source_service import LogSourceService

@strawberry.type
class Query:

    @strawberry.field
    async def logs(
        self,
        info: Info,
        filter: LogFilterInput | None = None
    ) -> list[LogEntryType]:
        es = info.context["es"]
        session = info.context["session"]
        log_entry_service = LogEntryService(es, session)
        log_source_service = LogSourceService(session)
        filter_data = filter.to_dict() if filter else {"size": 20}
        filter_data["from_"] = filter_data.get("page", 0) * filter_data.get("size", 20)
        filter_data.pop("page", None)
        logs = await log_entry_service.search_log_entries(
            **filter_data,  # pyright: ignore[reportArgumentType]
        )
        source_ids = list({log.source_id for log in logs})
        sources = await log_source_service.get_by_names(source_ids)
        source_map = {s.id: s for s in sources}
        return [LogEntryType(
            id=str(log_.id),  # pyright: ignore[reportArgumentType]
            level=log_.level,
            message=log_.message,
            source_id=log_.source_id,
            project=log_.project,
            timestamp=log_.timestamp,
            metadata=log_.metadata,  # pyright: ignore[reportArgumentType]
            source=LogSourceType(
                id=str(s.id),  # pyright: ignore[reportArgumentType]
                name=s.name,
                source_type=s.source_type,
                description=s.description,
                is_active=s.is_active,
                created_at=s.created_at,
            ) if (s := source_map.get(uuid.UUID(log_.source_id))) else None,
        ) for log_ in logs]

    @strawberry.field
    async def log_sources(self, info: Info) -> list[LogSourceType]:
        session = info.context["session"]
        service = LogSourceService(session)
        sources = await service.get_all()
        return [LogSourceType(
            id=str(s.id),  # pyright: ignore[reportArgumentType]
            name=s.name,
            source_type=s.source_type,
            description=s.description,
            is_active=s.is_active,
            created_at=s.created_at,
        ) for s in sources]

    @strawberry.field
    async def log_stats(self, info: Info) -> list[LogStatsType]:
        es = info.context["es"]
        session = info.context["session"]
        service = LogEntryService(es, session)
        stats = await service.get_stats()
        return [LogStatsType(
            level=s["key"],
            count=s["doc_count"],
        ) for s in stats]
