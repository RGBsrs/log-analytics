from datetime import datetime
import uuid

from graphql.pyutils.merge_kwargs import T
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.functions import func
from sqlalchemy.types import UUID as SQLAlchemyUUID, DateTime

from app.models.base import Base


class LogPattern(Base):
    __tablename__ = "log_patterns"

    id: Mapped[uuid.UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    pattern: Mapped[str]
    level: Mapped[str]
    source_id: Mapped[str]
    first_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    occurrences: Mapped[int] = mapped_column(default=1)
    is_new: Mapped[bool] = mapped_column(default=True)
