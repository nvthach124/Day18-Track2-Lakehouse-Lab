## Day 18 Lakehouse Lab — student UX
## Run `make` (no args) to see commands.

COMPOSE := docker compose -f docker/docker-compose.yml

.DEFAULT_GOAL := help

help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n\nTargets:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

up: ## Start MinIO + Spark/Jupyter (first run pulls ~2 GB images)
	$(COMPOSE) up -d
	@echo ""
	@echo "  Jupyter Lab → http://localhost:8888  (token: lakehouse)"
	@echo "  MinIO       → http://localhost:9001  (minioadmin / minioadmin)"
	@echo ""
	@echo "  Run 'make smoke' to verify the stack works end-to-end."
	@echo "  Run 'make data'  to generate the 1M-row Bronze sample for NB4."

down: ## Stop containers (data persists)
	$(COMPOSE) down

clean: ## Stop AND wipe MinIO data + ivy cache (full reset)
	$(COMPOSE) down -v

logs: ## Tail logs from all services
	$(COMPOSE) logs -f --tail=50

smoke: ## Run a 30-second end-to-end smoke test
	$(COMPOSE) exec -T spark python /workspace/scripts/verify.py

data: ## Generate 1M-row sample dataset into Bronze
	$(COMPOSE) exec -T spark python /workspace/scripts/generate_data.py

shell: ## Open bash shell in the Spark container
	$(COMPOSE) exec spark bash

ps: ## Show service status
	$(COMPOSE) ps

.PHONY: help up down clean logs smoke data shell ps
