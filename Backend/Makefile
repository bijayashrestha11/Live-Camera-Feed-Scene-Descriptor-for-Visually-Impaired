.PHONY: install dev-install run run-debug test lint format clean docker-build docker-run logs logs-error logs-clear help

# Python
PYTHON := python3
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest

# Directories
SRC_DIR := src/scene_descriptor
SCRIPTS_DIR := scripts
TESTS_DIR := tests
LOGS_DIR := logs

# Default target
.DEFAULT_GOAL := help

#===============================================================================
# Installation
#===============================================================================

install: ## Install production dependencies
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

dev-install: ## Install development dependencies
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt
	$(PIP) install -e .

#===============================================================================
# Running
#===============================================================================

run: ## Run the server
	$(PYTHON) -m scene_descriptor --host 0.0.0.0 --port 8080

run-debug: ## Run the server with debug logging
	$(PYTHON) -m scene_descriptor --host 0.0.0.0 --port 8080 -v

run-ssl: ## Run the server with SSL (requires cert files)
	$(PYTHON) -m scene_descriptor --host 0.0.0.0 --port 8080 --cert-file cert.pem --key-file key.pem

#===============================================================================
# Testing
#===============================================================================

test: ## Run tests with coverage
	$(PYTEST) $(TESTS_DIR)/ -v --cov=$(SRC_DIR) --cov-report=term-missing

test-html: ## Run tests with HTML coverage report
	$(PYTEST) $(TESTS_DIR)/ -v --cov=$(SRC_DIR) --cov-report=html
	@echo "Coverage report: htmlcov/index.html"

test-quick: ## Run tests without coverage
	$(PYTEST) $(TESTS_DIR)/ -v

#===============================================================================
# Code Quality
#===============================================================================

lint: ## Run linters
	flake8 $(SRC_DIR)/ $(SCRIPTS_DIR)/
	mypy $(SRC_DIR)/

format: ## Format code with black and isort
	black $(SRC_DIR)/ $(SCRIPTS_DIR)/ $(TESTS_DIR)/
	isort $(SRC_DIR)/ $(SCRIPTS_DIR)/ $(TESTS_DIR)/

format-check: ## Check code formatting without changes
	black --check $(SRC_DIR)/ $(SCRIPTS_DIR)/ $(TESTS_DIR)/
	isort --check-only $(SRC_DIR)/ $(SCRIPTS_DIR)/ $(TESTS_DIR)/

#===============================================================================
# Logs
#===============================================================================

logs: ## View main application log
	tail -f $(LOGS_DIR)/app.log

logs-error: ## View error log
	tail -f $(LOGS_DIR)/error.log

logs-all: ## View all logs
	tail -f $(LOGS_DIR)/*.log

logs-clear: ## Clear all log files
	rm -f $(LOGS_DIR)/*.log
	@echo "Logs cleared"

#===============================================================================
# Docker
#===============================================================================

docker-build: ## Build Docker image
	docker build -t scene-descriptor:latest .

docker-run: ## Run with Docker
	docker run -p 8080:8080 scene-descriptor:latest

docker-run-gpu: ## Run with Docker and GPU support
	docker run --gpus all -p 8080:8080 scene-descriptor:latest

docker-compose-up: ## Run with docker-compose
	docker-compose up

docker-compose-down: ## Stop docker-compose
	docker-compose down

#===============================================================================
# Cleanup
#===============================================================================

clean: ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info
	rm -rf .pytest_cache/ .coverage htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "Cleaned build artifacts"

clean-all: clean logs-clear ## Clean everything including logs
	@echo "Cleaned all artifacts and logs"

#===============================================================================
# Scripts
#===============================================================================

caption: ## Run batch captioning (use INPUT=path/to/video)
	$(PYTHON) -m scripts.batch_caption --input $(INPUT)

caption-dir: ## Caption all videos in a directory (use DIR=path/to/dir)
	$(PYTHON) -m scripts.batch_caption --input $(DIR) --output captions.csv

#===============================================================================
# Help
#===============================================================================

help: ## Show this help message
	@echo "Scene Descriptor - Makefile Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
