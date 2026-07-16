from typing import AsyncGenerator

from elasticsearch import AsyncElasticsearch
from sqlalchemy.engine.events import exc
from app.core.config import get_settings
settings = get_settings()

def get_es_client() -> AsyncElasticsearch:
    return AsyncElasticsearch(hosts=[settings.es_host])


async def get_es() -> AsyncGenerator[AsyncElasticsearch, None]:
    client = get_es_client()
    try:
        yield client
    finally:
        await client.close()
