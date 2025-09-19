.PHONY: help install install-dev test lint format clean build upload docker-build docker-run

# Default target
help:
	@echo "Available commands:"
	@echo "  install      Install the package"
	@echo "  install-dev  Install development dependencies"
	@echo "  test         Run tests"
	@echo "  lint         Run linting (flake8, mypy)"
	@echo "  format       Format code (black, isort)"
	@echo "  clean        Clean build artifacts"
	@echo "  build        Build package"
	@echo "  upload       Upload to PyPI"
	@echo "  docker-build Build Docker image"
	@echo "  docker-run   Run Docker container"

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

# Testing
test:
	pytest -v --cov=fim --cov-report=term-missing --cov-report=html

# Code quality
lint:
	flake8 src/fim tests
	mypy src/fim

format:
	black src/fim tests
	isort src/fim tests

# Build and distribution
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -f .coverage
	rm -rf htmlcov/

build: clean
	python -m build

upload: build
	twine upload dist/*

# Docker
docker-build:
	docker build -t fim:latest .

docker-run:
	docker run --rm -it -v $(PWD):/workspace fim:latest

# Development workflow
dev: install-dev format lint test

# CI workflow
ci: lint test
