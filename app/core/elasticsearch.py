from collections.abc import AsyncGenerator

from elasticsearch import AsyncElasticsearch

from app.core.config import get_settings
from app.core.es_mappings import LOGS_INDEX_MAPPING

settings = get_settings()

def get_es_client() -> AsyncElasticsearch:
    return AsyncElasticsearch(hosts=[settings.es_host])


async def get_es() -> AsyncGenerator[AsyncElasticsearch, None]:
    client = get_es_client()
    try:
        yield client
    finally:
        await client.close()


async def create_es_index(client: AsyncElasticsearch) -> None:
    if not await client.indices.exists(index=settings.es_index_logs):
        await client.indices.create(
            index=settings.es_index_logs,
            body=LOGS_INDEX_MAPPING
        )
