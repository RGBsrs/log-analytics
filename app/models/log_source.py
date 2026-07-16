import uuid
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.functions import func
from sqlalchemy.types import UUID as SQLAlchemyUUID
from sqlalchemy.types import DateTime, String, Text

from app.models.base import Base


class LogSource(Base):
    __tablename__ = "log_sources"

    id: Mapped[uuid.UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String, index=True)
    source_type: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
