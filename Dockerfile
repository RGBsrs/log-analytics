FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project --no-dev

COPY . .

RUN uv sync --frozen --no-dev

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY --from=builder /app/app ./app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
