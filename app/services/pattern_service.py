import re
from tkinter.constants import N

from elasticsearch._async.client import AsyncElasticsearch
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.services.log_entry_service import LogEntryService


class PatternExtractor:
    __VARIABLE_PATTERNS = [
        r'\d+\.\d+\.\d+\.\d+',          # IP адреси
        r'[0-9a-f-]{36}',               # UUID
        r'\b\d+\b',                      # числа
        r'[a-zA-Z0-9._-]+-\d+',         # host-1, db-primary-2
        r'/[^\s]+',                      # шляхи /api/v1/...
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+', # email
    ]

    __COMPILED_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in __VARIABLE_PATTERNS]

    @classmethod
    def extract_template(cls, text: str) -> str:
        splitted = text.split()
        template = []
        for word in splitted:
            for pattern in cls.__COMPILED_PATTERNS:
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
        self.extractor = PatternExtractor

    async def _fetch_messages(self, hours: int = 24) -> list[str]:
        service = LogEntryService(self.es, self.session)
        return await service.fetch_messages(hours)

    async def analyze(self, hours: int = 24) -> None:
        messages = await self._fetch_messages(hours)
        pass


if __name__ == "__main__":
    text = "User abc@test.com login failed from 192.168.1.1 Query took 1523ms on db-replica-3"
    print(PatternExtractor.extract_template(text))
