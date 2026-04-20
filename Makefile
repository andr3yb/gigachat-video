.PHONY: up down restart logs build ps

up:
	docker compose up -d postgres redis backend celery_worker

up-all:
	docker compose up -d

down:
	docker compose down

down-v:
	docker compose down -v

restart:
	docker compose restart backend celery_worker

build:
	docker compose up -d --build backend celery_worker

ps:
	docker compose ps

logs:
	docker compose logs -f backend celery_worker
