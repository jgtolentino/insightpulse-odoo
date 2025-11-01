## === Unsloth targets ===
.PHONY: unsloth-up unsloth-down unsloth-logs unsloth-sh unsloth-api

UNSL_COMPOSE = docker compose -f docker-compose.simple.yml -f docker-compose.unsloth.yml

unsloth-up:
	$(UNSL_COMPOSE) up -d unsloth unsloth-api

unsloth-down:
	$(UNSL_COMPOSE) down

unsloth-logs:
	docker logs -f unsloth

unsloth-sh:
	docker exec -it unsloth bash

unsloth-api:
	curl -s http://localhost:8000/health | jq .
