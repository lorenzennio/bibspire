.PHONY: lint format test test-all clean build install dev-install pre-commit-install pre-commit-run

# Development targets
dev-install:
	pip install -e ".[dev]"

install:
	pip install -e .

# Pre-commit targets
pre-commit-install: dev-install
	pre-commit install

pre-commit-run:
	pre-commit run --all-files

# Code quality targets
lint:
	ruff check src/ tests/

lint-fix:
	ruff check --fix src/ tests/

format:
	ruff format src/ tests/

format-check:
	ruff format --check src/ tests/

# Test targets
test:
	pytest tests/ -v -m "not slow"

test-all:
	pytest tests/ -v

test-slow:
	pytest tests/ -v -m "slow"

test-cov:
	pytest tests/ -v -m "not slow" --cov=bibspire --cov-report=html --cov-report=term

test-cov-all:
	pytest tests/ -v --cov=bibspire --cov-report=html --cov-report=term

# Build targets
clean:
	rm -rf build/ dist/ *.egg-info/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

# Combined targets
check: lint format-check test

ci: lint format-check test-cov

all: dev-install pre-commit-install check build

# Help
help:
	@echo "Available targets:"
	@echo "  dev-install      - Install package in development mode with dev dependencies"
	@echo "  install          - Install package in development mode"
	@echo "  pre-commit-install - Install pre-commit hooks"
	@echo "  pre-commit-run   - Run pre-commit on all files"
	@echo "  lint             - Run Ruff linting checks"
	@echo "  lint-fix         - Run Ruff linting with auto-fix"
	@echo "  format           - Format code with Ruff"
	@echo "  format-check     - Check code formatting"
	@echo "  test             - Run fast tests only"
	@echo "  test-all         - Run all tests"
	@echo "  test-slow        - Run slow tests only"
	@echo "  test-cov         - Run fast tests with coverage"
	@echo "  test-cov-all     - Run all tests with coverage"
	@echo "  clean            - Clean build artifacts"
	@echo "  build            - Build package"
	@echo "  check            - Run linting, formatting check, and tests"
	@echo "  ci               - Run linting, formatting check, and tests with coverage"
	@echo "  all              - Install deps, install pre-commit, run checks, and build"
	@echo "  help             - Show this help message"
