from typing import OrderedDict

from faker import Faker
from app.schemas.log_entry import LogEntryCreate, LogLevel

fake = Faker()

LOG_LEVELS = [level.value for level in LogLevel]
LOG_LEVEL_WEIGHTS = [0.20, 0.50, 0.15, 0.10, 0.05]  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVELS_MAP = OrderedDict(zip(LOG_LEVELS, LOG_LEVEL_WEIGHTS))

LOG_TEMPLATES = [
    lambda: f"GET {fake.uri_path()} {fake.random_element([200, 201, 400, 404, 500])}",
    lambda: f"Database query took {fake.random_int(10, 5000)}ms",
    lambda: f"User {fake.uuid4()} authentication failed",
    lambda: f"Connection to {fake.hostname()} timed out",
    lambda: f"Successfully processed {fake.random_int(1, 1000)} records",
]


def generate_log_entry(source_id: str | None = None) -> LogEntryCreate:
    level = fake.random_element(
        LOG_LEVELS_MAP
    )
    message = fake.random_element(LOG_TEMPLATES)()
    source_id = source_id or fake.uuid4()
    return LogEntryCreate(level=LogLevel(level), message=message, source_id=source_id)


def generate_log_entries(count: int, source_id: str | None = None) -> list[LogEntryCreate]:
    return [generate_log_entry(source_id) for _ in range(count)]
