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
        ...

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
        service = LogEntryService(es)
        stats = await service.get_stats()
        return [LogStatsType(
            level=s["key"],
            count=s["doc_count"],
        ) for s in stats]
