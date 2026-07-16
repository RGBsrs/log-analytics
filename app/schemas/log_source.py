import uuid
from datetime import datetime

from pydantic import BaseModel
from pydantic.config import ConfigDict


class LogSourceBase(BaseModel):
    name: str
    description: str | None = None
    source_type: str
    is_active: bool = True


class LogSourceCreate(LogSourceBase):
    pass


class LogSourceRead(LogSourceBase):
    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LogSourceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    source_type: str | None = None
    is_active: bool | None = None
