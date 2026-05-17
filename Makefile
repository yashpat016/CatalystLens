SHELL := /bin/bash

COMPOSE ?= docker compose

.PHONY: help up down logs ps build migrate seed test test-api test-web fmt api-shell db-shell clean

help: ## Show this help.
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make <target>\n\nTargets:\n"} /^[a-zA-Z_-]+:.*##/ { printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

up: ## Build + start the full stack, run migrations, seed fixtures.
	$(COMPOSE) up --build -d
	@echo "Waiting for api container to be ready..."
	@for i in $$(seq 1 30); do \
		if $(COMPOSE) exec -T api python -c "import sys" 2>/dev/null; then break; fi; \
		sleep 1; \
	done
	$(MAKE) migrate
	$(MAKE) seed
	@echo ""
	@echo "Stack is up:"
	@echo "  API:   http://localhost:8000/api/health"
	@echo "  Web:   http://localhost:3000/ticker/AAPL"
	@echo "  Docs:  http://localhost:8000/docs"

down: ## Stop and remove containers.
	$(COMPOSE) down

logs: ## Tail logs from all services.
	$(COMPOSE) logs -f

ps: ## Show container status.
	$(COMPOSE) ps

build: ## Rebuild images without starting.
	$(COMPOSE) build

migrate: ## Apply Alembic migrations.
	$(COMPOSE) exec -T api alembic upgrade head

seed: ## Seed symbols + generate bar and fundamentals fixtures.
	$(COMPOSE) exec -T api python -m scripts.seed_symbols
	$(COMPOSE) exec -T api python -m scripts.generate_fixtures
	$(COMPOSE) exec -T api python -m scripts.generate_fundamentals_fixtures
	$(COMPOSE) exec -T api python -m scripts.generate_institutional_fixtures
	$(COMPOSE) exec -T api python -m scripts.generate_insider_fixtures

test: test-api test-web ## Run backend + frontend test suites.

test-api: ## Run backend pytest.
	$(COMPOSE) exec -T api pytest -v

test-web: ## Run frontend vitest.
	$(COMPOSE) exec -T web npm test -- --run

fmt: ## Format code (ruff + black + prettier).
	$(COMPOSE) exec -T api ruff check --fix app
	$(COMPOSE) exec -T api black app
	$(COMPOSE) exec -T web npx prettier --write .

api-shell: ## Open a shell inside the api container.
	$(COMPOSE) exec api /bin/bash

db-shell: ## Open psql inside the postgres container.
	$(COMPOSE) exec postgres psql -U $${POSTGRES_USER:-catalystlens} -d $${POSTGRES_DB:-catalystlens}

clean: ## Stop and remove containers + named volumes (DESTRUCTIVE).
	$(COMPOSE) down -v
