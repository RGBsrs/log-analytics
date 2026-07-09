from fastapi import FastAPI

from .api.routes.health import router as health_router
from .api.routes.log_sources import router as log_sources_router
from .core.config import get_settings
from .core.lifespan import lifespan

app = FastAPI(lifespan=lifespan)
cfg = get_settings()
app.include_router(health_router)
app.include_router(log_sources_router, prefix="/api/v1")
