from fastapi import FastAPI

from .api.routes.health import router as health_router
from .api.routes.log_sources import router as log_sources_router
from .core.config import get_settings
from .core.lifespan import lifespan
from app.api.routes.logs import router as logs_router
from app.api.routes.ingest import router as ingest_router
from app.graphql.schema import graphql_router

API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"

app = FastAPI(lifespan=lifespan)
cfg = get_settings()
app.include_router(health_router)
app.include_router(log_sources_router, prefix=API_PREFIX)
app.include_router(logs_router, prefix=API_PREFIX)
app.include_router(ingest_router, prefix=API_PREFIX)
app.include_router(graphql_router, prefix="/graphql")
