from cmath import log
from xxlimited import new

from elasticsearch import AsyncElasticsearch

from app.core.config import get_settings
from app.schemas.log_entry import LogEntryRead, LogEntryCreate


class LogEntryService:
    def __init__(self, es_client: AsyncElasticsearch):
        self.es_client = es_client
        self.settings = get_settings()

    async def index_log_entry(self, log_entry: LogEntryCreate) -> LogEntryRead:
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

    async def get_stats(self) -> dict:
        body = {
            "size": 0,
            "aggs": {
                "by_level": {
                    "terms": {"field": "level"}
                }
            }
        }
        response = await self.es_client.search(body=body)
        return response["aggregations"]

    async def delete_log(self, source_id: str, /) -> None:
        await self.es_client.delete_by_query(
            index=self.settings.es_index_logs,
            body={"query": {"match": {"source_id": source_id}}}
        )
