.PHONY: install dev test lint format clean help

help:
	@echo "FastAPI Todo API - Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make dev        - Run development server"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Lint code"
	@echo "  make format     - Format code"
	@echo "  make clean      - Clean cache files"

install:
	pip install -e ".[dev]"

dev:
	uvicorn api_service.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest -v --cov=api_service --cov-report=term-missing

lint:
	ruff check .
	mypy src/

format:
	ruff format .

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov .coverage
	rm -f todos.db

docker-build:
	docker build -t fastapi-todo-api .

docker-run:
	docker run -p 8000:8000 --env-file .env fastapi-todo-api
