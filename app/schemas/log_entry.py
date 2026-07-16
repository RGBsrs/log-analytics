from enum import StrEnum

from pydantic import BaseModel, Field
from datetime import UTC, datetime
import uuid

LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogEntryBase(BaseModel):
    level: LogLevel
    message: str
    source_id: str
    project: str = "default"
    metadata: dict = Field(default_factory=dict)


class LogEntry(LogEntryBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

class LogEntryCreate(LogEntryBase):
    pass
