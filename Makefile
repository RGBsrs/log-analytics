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
