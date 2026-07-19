from datetime import datetime

from sqlalchemy.orm import Mapped


class LogPattern(Base):
    __tablename__ = "log_patterns"

    id: Mapped[uuid.UUID] = ...
    pattern: Mapped[str]
    level: Mapped[str]
    source_id: Mapped[str]
    first_seen: Mapped[datetime]
    last_seen: Mapped[datetime]
    occurrences: Mapped[int]
    is_new: Mapped[bool]
