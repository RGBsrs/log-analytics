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

migrate:
	@if [ -z "$(msg)" ]; then echo "Помилка: вкажи msg=\"...\""; exit 1; fi
	docker compose exec api alembic revision --autogenerate -m "$(msg)"

migrate-up:
	docker compose exec api alembic upgrade head

migrate-down:
	docker compose exec api alembic downgrade -1

migrate-history:
	docker compose exec api alembic history

.PHONY: migrate migrate-up migrate-down migrate-history
