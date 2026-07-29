up:
	docker compose up --build -d

down:
	docker compose down

watch:
	docker compose watch

logs:
	docker compose logs -f api

ps:
	docker compose ps

health:
	curl -s http://localhost:8000/health | python3 -m json.tool

clean:
	docker compose down -v  # видаляє також volumes (дані!)

restart-api:
	docker compose restart api

rebuild-api:
	docker compose up -d --build api

migrate:
	@if [ -z "$(msg)" ]; then echo "Помилка: вкажи msg=\"...\""; exit 1; fi
	uv run alembic revision --autogenerate -m "$(msg)"

migrate-up:
	uv run alembic upgrade head

migrate-down:
	uv run alembic downgrade -1

migrate-history:
	uv run alembic history

.PHONY: migrate migrate-up migrate-down migrate-history
