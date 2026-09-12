.PHONY: help install dev test test-cov lint format clean docker-up docker-down check serve security

help:
	@echo "Available commands:"
	@echo "  install      Install dependencies"
	@echo "  dev          Run the FastAPI development server (standard fastapi dev)"
	@echo "  serve        Run the FastAPI server via CLI (uvicorn wrapper)"
	@echo "  test         Run tests"
	@echo "  test-cov     Run tests (coverage report; same gate as test)"
	@echo "  lint         Run ruff check and format --check (matches CI)"
	@echo "  format       Run ruff format"
	@echo "  check        Run linting and tests"
	@echo "  security     Run bandit + pip-audit (matches security.yml gates)"
	@echo "  clean        Remove temporary files"
	@echo "  docker-up    Start the application using Docker Compose"
	@echo "  docker-down  Stop the application using Docker Compose"

install:
	uv sync

dev:
	fastapi dev src/python_template/api/main.py

serve:
	uv run python-template serve

test:
	uv run pytest

test-cov:
	uv run pytest --cov-report=term-missing

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff format .

check: lint test

security:
	uv run bandit -r src/ -ll -ii
	uv export --frozen --no-dev --no-hashes --no-emit-project -o requirements-audit.txt >/dev/null
	uv run pip-audit -r requirements-audit.txt --no-deps --disable-pip
	rm -f requirements-audit.txt

clean:
	rm -rf .pytest_cache .ruff_cache build dist *.egg-info test.db .coverage htmlcov requirements-audit.txt

docker-up:
	docker compose up --build

docker-down:
	docker compose down
