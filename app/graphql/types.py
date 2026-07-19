import strawberry
from datetime import datetime

from app.schemas.log_entry import LogLevel

@strawberry.type
class LogSourceType:
    id: strawberry.ID
    name: str
    source_type: str
    description: str | None
    is_active: bool
    created_at: datetime

@strawberry.type
class LogEntryType:
    id: str
    level: str
    message: str
    source_id: str
    project: str
    timestamp: datetime
    metadata: strawberry.scalars.JSON
    source: LogSourceType | None = None  # ← нове поле

@strawberry.type
class LogStatsType:
    level: str
    count: int

@strawberry.input
class LogSourceInput:
    name: str
    source_type: str
    description: str | None = None
    is_active: bool = True

@strawberry.input
class LogInput:
    level: str
    message: str
    source_id: str
    project: str = "default"
    metadata: strawberry.scalars.JSON = strawberry.field(default_factory=dict)

@strawberry.input
class LogFilterInput:
    query: str | None = None
    level: str | None = None
    source_id: str | None = None
    page: int = 0
    size: int = 20

    def to_dict(self):
        return {
            "query": self.query,
            "level": LogLevel(self.level) if self.level else None,
            "source_id": self.source_id,
            "page": self.page,
            "size": self.size,
        }
