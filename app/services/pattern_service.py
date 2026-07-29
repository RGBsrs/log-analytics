import re
from collections import defaultdict
from typing import ClassVar

from elasticsearch._async.client import AsyncElasticsearch
from fastapi import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql import select

from app.core.database import get_session
from app.core.elasticsearch import get_es
from app.models.log_patterns import LogPattern
from app.schemas.log_entry import LogSearchResult
from app.services.log_entry_service import LogEntryService


class PatternExtractor:
    __VARIABLE_PATTERNS: ClassVar = [
        r'\d+\.\d+\.\d+\.\d+',          # IP адреси
        r'[0-9a-f-]{36}',               # UUID
        r'\b\d+\b',                      # числа
        r'[a-zA-Z0-9._-]+-\d+',         # host-1, db-primary-2
        r'/[^\s]+',                      # шляхи /api/v1/...
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+', # email
    ]
    def __init__(self) -> None:
        self.__COMPILED_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in self.__VARIABLE_PATTERNS]

    def extract_template(self, text: str) -> str:
        splitted = text.split()
        template = []
        for word in splitted:
            for pattern in self.__COMPILED_PATTERNS:
                if pattern.match(word):
                    template.append("{var}")
                    break
            else:
                template.append(word)
        return ' '.join(template) if template else text


class PatternService:
    def __init__(self, es: AsyncElasticsearch, session: AsyncSession):
        self.es = es
        self.session = session
        self.extractor = PatternExtractor()

    async def _fetch_messages(self, hours: int = 24) -> list[LogSearchResult]:
        service = LogEntryService(self.es, self.session)
        return await service.fetch_messages(hours)

    async def _get_by_pattern(self, pattern: str) -> LogPattern | None:
        result = await self.session.execute(
            select(LogPattern).where(LogPattern.pattern.like(f"%{pattern}%"))
        )
        return result.scalar_one_or_none()

    async def save_pattern(self, pattern: str, level: str, source_id: str, count: int) -> LogPattern:
        existing_pattern = await self._get_by_pattern(pattern)
        new_pattern = None
        if existing_pattern:
            existing_pattern.occurrences += count
            existing_pattern.is_new = False
        else:
            new_pattern = LogPattern(
                pattern=pattern,
                level=level,
                source_id=source_id,
                occurrences=count,
            )
            self.session.add(new_pattern)
        await self.session.commit()
        return existing_pattern or new_pattern  # pyright: ignore[reportReturnType]

    async def get_all(self) -> list[LogPattern]:
        result = await self.session.execute(select(LogPattern))
        return list(result.scalars().all())

    async def get_new(self) -> list[LogPattern]:
        result = await self.session.execute(
            select(LogPattern).\
                where(LogPattern.is_new == True).\
                order_by(LogPattern.first_seen.desc())
        )
        return list(result.scalars().all())

    async def analyze(self, hours: int = 24) -> dict:
        messages = await self._fetch_messages(hours)
        groups: dict[tuple, list] = defaultdict(list)
        for log_message in messages:
            pattern = self.extractor.extract_template(log_message.message)
            if pattern:
                key = (pattern, log_message.level, log_message.source_id)
                groups[key].append(log_message)

        for (pattern, level, source_id), items in groups.items():
            count = len(items)
            await self.save_pattern(pattern, level, source_id, count)

        return {"analyzed": len(messages), "groups": len(groups), "hours": hours}


async def get_pattern_service(
    es: AsyncElasticsearch = Depends(get_es),
    session: AsyncSession = Depends(get_session),
) -> PatternService:
    return PatternService(es, session)

if __name__ == "__main__":
    text = "User abc@test.com login failed from 192.168.1.1 Query took 1523ms on db-replica-3"
    extractor = PatternExtractor()
    print(extractor.extract_template(text))
