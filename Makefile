.PHONY: help install dev test test-cov lint format clean docker-up docker-down check serve

help:
	@echo "Available commands:"
	@echo "  install      Install dependencies"
	@echo "  dev          Run the FastAPI development server (standard fastapi dev)"
	@echo "  serve        Run the FastAPI server via CLI (uvicorn wrapper)"
	@echo "  test         Run tests"
	@echo "  test-cov     Run tests with coverage reporting"
	@echo "  lint         Run linting checks"
	@echo "  format       Run code formatting"
	@echo "  check        Run linting and tests"
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
	uv run pytest --cov=src --cov-report=term-missing

lint:
	ruff check .

format:
	ruff format .

check: lint test

clean:
	rm -rf .pytest_cache .ruff_cache .venv build dist *.egg-info test.db

docker-up:
	docker compose up --build

docker-down:
	docker compose down
