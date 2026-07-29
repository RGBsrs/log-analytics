import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LogPatternRead(BaseModel):
    id: uuid.UUID
    pattern: str
    level: str
    source_id: str
    occurrences: int
    is_new: bool
    first_seen: datetime
    last_seen: datetime

    model_config = ConfigDict(from_attributes=True)
