from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.elasticsearch import get_es_client
from app.core.es_mappings import LOGS_INDEX_MAPPING


@asynccontextmanager
async def lifespan(app: FastAPI):
    es = get_es_client()
    settings = get_settings()
    if not await es.indices.exists(index=settings.es_index_logs):
        await es.indices.create(
            index=settings.es_index_logs,
            body=LOGS_INDEX_MAPPING
        )
    yield
    await es.close()
    print("Shutting down...")
