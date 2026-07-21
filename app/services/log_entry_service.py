from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_session
from app.core.elasticsearch import get_es_client
from app.schemas.log_entry import LogEntryRead, LogEntryCreate
from app.schemas.log_source import LogSourceCreate
from app.services.log_source_service import LogSourceService


class LogEntryService:
    def __init__(self, es_client: AsyncElasticsearch, session: AsyncSession):
        self.es_client = es_client
        self.session = session
        self.settings = get_settings()

    async def index_log_entry(self, log_entry: LogEntryCreate) -> LogEntryRead:
        log_source_service = LogSourceService(self.session)
        log_source = await log_source_service.get_by_name(log_entry.source_id)
        if log_source is None:
            await log_source_service.create(LogSourceCreate(
                name=log_entry.source_id,
                source_type="auto",
                description="Auto-created from log ingestion"
            ))
        new_log = LogEntryRead(**log_entry.model_dump())

        await self.es_client.index(
            index=self.settings.es_index_logs,
            id=new_log.id,
            document=new_log.model_dump()
        )
        return new_log

    async def search_log_entries(
        self, query: str | None = None,
        level: str | None = None,
        source_id: str | None = None,
        from_: int = 0,
        size: int = 0) -> list[LogEntryRead]:
        must = []
        filter_ = []
        if query:
            must.append({"match": {"message": query}})
        if level:
            filter_.append({"term": {"level": level}})
        if source_id:
            filter_.append({"term": {"source_id": source_id}})

        body = {
            "query": {"bool": {"must": must, "filter": filter_}},
            "sort": [{"timestamp": "desc"}],
            "from": from_,
            "size": size
        }
        response = await self.es_client.search(body=body)
        return [LogEntryRead(**hit["_source"]) for hit in response["hits"]["hits"]]

    async def get_stats(self) -> list[dict]:
        body = {
            "size": 0,
            "aggs": {
                "by_level": {
                    "terms": {"field": "level"}
                }
            }
        }
        response = await self.es_client.search(body=body)
        return response["aggregations"]["by_level"]["buckets"]

    async def delete_log(self, source_id: str, /) -> None:
        await self.es_client.delete_by_query(
            index=self.settings.es_index_logs,
            body={"query": {"match": {"source_id": source_id}}}
        )

    async def index_log_entry_bulk(self, logs: list[LogEntryCreate]) -> list[LogEntryRead]:
        new_logs = [LogEntryRead(**new_log.model_dump()) for new_log in logs]
        unique_sources = list({log_.source_id for log_ in new_logs})
        log_source_service = LogSourceService(self.session)
        existing = await log_source_service.get_by_names(unique_sources)
        existing_names = {s.name for s in existing}
        for name in unique_sources:
            if name not in existing_names:
                await log_source_service.create(LogSourceCreate(
                    name=name,
                    source_type="auto",
                    description="Auto-created from log ingestion"
                ))
        body = [
            {
                "_index": self.settings.es_index_logs,
                "_id": new_log.id,
                **new_log.model_dump()
            }
            for new_log in new_logs
        ]
        count, _ = await async_bulk(self.es_client, body)
        print(f"Indexed {count} log entries")
        return new_logs

    async def fetch_messages(self, hours: int = 24) -> list[str]:
        query = {
            "size": 0,
            "query": {
                "range": {
                    "timestamp": {
                        "gte": f"now-{hours}h"
                    }
                }
            },
            "aggs": {
                "by_message": {
                    "terms": {
                        "field": "message.keyword",
                        "size": 1000
                    },
                    "aggs": {
                        "level": {"terms": {"field": "level", "size": 1}},
                        "source": {"terms": {"field": "source_id", "size": 1}}
                    }
                }
            }
        }
        result = await self.es_client.search(body=query)
        return [hit["_source"]["message"] for hit in result["hits"]["hits"]]


def get_log_entry_service(session: AsyncSession = Depends(get_session)) -> LogEntryService:
    es_client = get_es_client()
    return LogEntryService(es_client, session)
