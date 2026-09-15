.PHONY: install run test lint

install:
	pip install -r requirements-dev.txt

run:
	PYTHONPATH=src uvicorn notes_backend.api.main:app --reload --host 0.0.0.0 --port 8000

test:
	PYTHONPATH=src pytest --cov=src --cov-report=term-missing

lint:
	ruff check src tests
