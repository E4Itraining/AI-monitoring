# AI Monitoring Platform - Makefile
# ================================
#
# Usage: make [target]
#
# Run 'make help' for a list of available targets

.PHONY: help init build up down restart logs status \
        test test-unit test-integration test-e2e test-smoke test-all test-coverage \
        test-docker test-docker-unit test-docker-integration test-docker-e2e \
        clean clean-volumes clean-all \
        demo warm-up load-test

# Default shell
SHELL := /bin/bash

# Docker compose files
COMPOSE_FILE := docker-compose.yml
COMPOSE_TEST_FILE := docker-compose.test.yml
COMPOSE_ENHANCED_FILE := docker-compose-enhanced.yml
COMPOSE_SCALABLE_FILE := docker-compose.scalable.yml

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m

#==============================================================================
# HELP
#==============================================================================

help: ## Show this help message
	@echo ""
	@echo "$(BLUE)AI Monitoring Platform$(NC)"
	@echo "$(BLUE)======================$(NC)"
	@echo ""
	@echo "$(GREEN)Services:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

#==============================================================================
# DOCKER SERVICES
#==============================================================================

init: ## Initialize data directories with correct permissions
	@echo "$(BLUE)Initializing data directories...$(NC)"
	@mkdir -p opensearch-data grafana-data tempo-data logs
	@# OpenSearch runs as UID 1000 inside container
	@if [ -w opensearch-data ]; then \
		chmod 777 opensearch-data 2>/dev/null || sudo chmod 777 opensearch-data; \
	fi
	@echo "$(GREEN)Data directories initialized$(NC)"

build: ## Build all Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	docker-compose -f $(COMPOSE_FILE) build

up: init ## Start all services
	@echo "$(BLUE)Starting services...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up -d
	@echo "$(GREEN)Services started!$(NC)"
	@echo "  App:        http://localhost:8000"
	@echo "  Grafana:    http://localhost:3000 (admin/admin)"
	@echo "  Prometheus: http://localhost:9090"

up-enhanced: init ## Start enhanced stack with alerting
	@echo "$(BLUE)Starting enhanced services...$(NC)"
	docker-compose -f $(COMPOSE_ENHANCED_FILE) up -d

up-scalable: init ## Start production scalable stack
	@echo "$(BLUE)Starting scalable services...$(NC)"
	docker-compose -f $(COMPOSE_SCALABLE_FILE) up -d

down: ## Stop all services
	@echo "$(BLUE)Stopping services...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down
	docker-compose -f $(COMPOSE_TEST_FILE) down 2>/dev/null || true

restart: down up ## Restart all services

logs: ## Show service logs
	docker-compose -f $(COMPOSE_FILE) logs -f

logs-app: ## Show application logs only
	docker-compose -f $(COMPOSE_FILE) logs -f app

status: ## Show service status
	@echo "$(BLUE)Service Status:$(NC)"
	@docker-compose -f $(COMPOSE_FILE) ps

health: ## Check health of all services
	@echo "$(BLUE)Health Check:$(NC)"
	@echo -n "  App:        " && curl -sf http://localhost:8000/health && echo "$(GREEN)OK$(NC)" || echo "$(RED)FAIL$(NC)"
	@echo -n "  Prometheus: " && curl -sf http://localhost:9090/-/ready && echo "$(GREEN)OK$(NC)" || echo "$(RED)FAIL$(NC)"
	@echo -n "  Grafana:    " && curl -sf http://localhost:3000/api/health && echo "$(GREEN)OK$(NC)" || echo "$(RED)FAIL$(NC)"

#==============================================================================
# TESTING - LOCAL
#==============================================================================

test: test-unit ## Run unit tests (default)

test-unit: ## Run unit tests only (no dependencies required)
	@echo "$(BLUE)Running unit tests...$(NC)"
	PYTHONPATH=app:tests pytest tests/unit/ -v --tb=short

test-integration: ## Run integration tests (requires running services)
	@echo "$(BLUE)Running integration tests...$(NC)"
	./scripts/run_tests.sh integration

test-e2e: ## Run end-to-end tests (requires full stack)
	@echo "$(BLUE)Running e2e tests...$(NC)"
	./scripts/run_tests.sh e2e

test-smoke: ## Run smoke tests (quick verification)
	@echo "$(BLUE)Running smoke tests...$(NC)"
	./scripts/run_tests.sh smoke

test-all: ## Run all tests
	@echo "$(BLUE)Running all tests...$(NC)"
	./scripts/run_tests.sh all

test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	PYTHONPATH=app:tests pytest tests/ -v --cov=app --cov-report=html --cov-report=term
	@echo "$(GREEN)Coverage report: htmlcov/index.html$(NC)"

#==============================================================================
# TESTING - DOCKER
#==============================================================================

test-docker: test-docker-unit ## Run unit tests in Docker (default)

test-docker-unit: ## Run unit tests in Docker container
	@echo "$(BLUE)Running unit tests in Docker...$(NC)"
	docker-compose -f $(COMPOSE_FILE) -f $(COMPOSE_TEST_FILE) run --rm test-unit

test-docker-integration: ## Run integration tests in Docker (starts services)
	@echo "$(BLUE)Running integration tests in Docker...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up -d
	docker-compose -f $(COMPOSE_FILE) -f $(COMPOSE_TEST_FILE) run --rm test-integration

test-docker-e2e: ## Run e2e tests in Docker (starts full stack)
	@echo "$(BLUE)Running e2e tests in Docker...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up -d
	docker-compose -f $(COMPOSE_FILE) -f $(COMPOSE_TEST_FILE) run --rm test-e2e

test-docker-smoke: ## Run smoke tests in Docker
	@echo "$(BLUE)Running smoke tests in Docker...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up -d
	docker-compose -f $(COMPOSE_FILE) -f $(COMPOSE_TEST_FILE) run --rm test-smoke

test-docker-all: ## Run all tests in Docker
	@echo "$(BLUE)Running all tests in Docker...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up -d
	docker-compose -f $(COMPOSE_FILE) -f $(COMPOSE_TEST_FILE) run --rm test-runner

#==============================================================================
# LOAD TESTING & DEMOS
#==============================================================================

warm-up: ## Run warm-up scenario (3 min)
	@echo "$(BLUE)Running warm-up scenario...$(NC)"
	./scripts/warm_up.sh

demo: ## Run full demo scenario (2 hours)
	@echo "$(BLUE)Running full demo...$(NC)"
	./scripts/run_full_demo.sh

load-drift: ## Run drift detection scenario
	@echo "$(BLUE)Running drift scenario...$(NC)"
	./scripts/progressive_drift.sh

load-injection: ## Run prompt injection scenario
	@echo "$(BLUE)Running injection scenario...$(NC)"
	./scripts/prompt_injections.sh

load-stress: ## Run latency stress scenario
	@echo "$(BLUE)Running stress scenario...$(NC)"
	./scripts/latence_stress.sh

load-risk: ## Run AI risk storm scenario
	@echo "$(BLUE)Running risk storm scenario...$(NC)"
	./scripts/ai_risk_storm.sh

#==============================================================================
# CLEANUP
#==============================================================================

clean: ## Stop services and remove containers
	@echo "$(BLUE)Cleaning up containers...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down --remove-orphans
	docker-compose -f $(COMPOSE_TEST_FILE) down --remove-orphans 2>/dev/null || true

clean-volumes: ## Remove Docker volumes
	@echo "$(YELLOW)Removing volumes...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down -v

clean-all: clean-volumes ## Remove containers, volumes, and images
	@echo "$(YELLOW)Removing images...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down --rmi local
	@echo "$(YELLOW)Cleaning test artifacts...$(NC)"
	rm -rf htmlcov .coverage .pytest_cache __pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

#==============================================================================
# DEVELOPMENT
#==============================================================================

install-test-deps: ## Install test dependencies locally
	@echo "$(BLUE)Installing test dependencies...$(NC)"
	pip install -r tests/requirements.txt

lint: ## Run linting (if configured)
	@echo "$(BLUE)Running linting...$(NC)"
	@if command -v flake8 &> /dev/null; then \
		flake8 app/ tests/; \
	else \
		echo "$(YELLOW)flake8 not installed, skipping$(NC)"; \
	fi

format: ## Format code (if configured)
	@echo "$(BLUE)Formatting code...$(NC)"
	@if command -v black &> /dev/null; then \
		black app/ tests/; \
	else \
		echo "$(YELLOW)black not installed, skipping$(NC)"; \
	fi

#==============================================================================
# CI/CD
#==============================================================================

ci-test: ## Run CI test pipeline
	@echo "$(BLUE)Running CI tests...$(NC)"
	docker-compose -f $(COMPOSE_FILE) -f $(COMPOSE_TEST_FILE) build test-unit
	docker-compose -f $(COMPOSE_FILE) -f $(COMPOSE_TEST_FILE) run --rm test-unit
	@echo "$(GREEN)CI tests passed!$(NC)"

ci-full: ## Run full CI pipeline with integration tests
	@echo "$(BLUE)Running full CI pipeline...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up -d --build
	sleep 30  # Wait for services
	docker-compose -f $(COMPOSE_FILE) -f $(COMPOSE_TEST_FILE) run --rm test-runner
	docker-compose -f $(COMPOSE_FILE) down
	@echo "$(GREEN)Full CI pipeline passed!$(NC)"
