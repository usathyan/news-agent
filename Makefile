.PHONY: help clean install build test lint format run venv

help:
	@echo "Available targets:"
	@echo "  make venv       - Create virtual environment using uv"
	@echo "  make install    - Install dependencies using uv"
	@echo "  make clean      - Remove build artifacts and cache"
	@echo "  make build      - Build the project"
	@echo "  make test       - Run tests with pytest"
	@echo "  make lint       - Run ruff linter"
	@echo "  make format     - Format code with black and ruff"
	@echo "  make run        - Run the news-agent CLI"
	@echo "  make dev        - Install in development mode"

venv:
	uv venv

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf .cache/
	rm -rf .venv/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete

install: venv
	uv pip install -e ".[dev]"

dev: install

build:
	uv pip install build
	python -m build

test:
	pytest tests/ -v

lint:
	ruff check src/ tests/
	mypy src/

format:
	black src/ tests/
	ruff check --fix src/ tests/

run:
	news-agent --help
