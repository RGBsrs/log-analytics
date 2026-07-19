from typing import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from app.models.log_source import LogSource
from app.schemas.log_source import LogSourceCreate, LogSourceUpdate


class LogSourceService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: UUID) -> LogSource | None:
        return await self.session.get(LogSource, id)

    async def get_by_name(self, name: str) -> LogSource | None:
        query = select(LogSource).where(LogSource.source_type == name)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_names(self, names: list[str]) -> Sequence[LogSource]:
        query = select(LogSource).where(LogSource.source_type.in_(names))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_all(self, is_active: bool | None = None) -> Sequence[LogSource]:
        query = select(LogSource)
        if is_active is not None:
            query = query.where(LogSource.is_active.is_(is_active))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, data: LogSourceCreate) -> LogSource:
        log_source = LogSource(**data.model_dump())
        self.session.add(log_source)
        await self.session.commit()
        return log_source

    async def update(self, data: LogSourceUpdate, id_: UUID) -> LogSource | None:
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return
        log_source = await self.get_by_id(id_)
        if not log_source:
            return
        for field, value in update_data.items():
            setattr(log_source, field, value)
        self.session.add(log_source)
        await self.session.commit()
        return log_source

    async def delete(self, id: UUID) -> bool:
        log_source = await self.get_by_id(id)
        if not log_source:
            return False
        await self.session.delete(log_source)
        await self.session.commit()
        return True
