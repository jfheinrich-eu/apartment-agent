PYTHON ?= python3
PIP ?= $(PYTHON) -m pip
VENV ?= .venv
VENV_BIN := $(VENV)/bin
VENV_PYTHON := $(VENV_BIN)/python
VENV_PIP := $(VENV_BIN)/pip
CONFIG ?= config/search_profile.yml

.PHONY: help venv install dev-install build test run run-once lint format clean

help:
	@echo "Available targets:"
	@echo "  make venv            - Create virtual environment"
	@echo "  make install         - Install project (demo adapter only)"
	@echo "  make dev-install     - Install with pytest (recommended)"
	@echo "  make build           - Build wheel and sdist"
	@echo "  make test            - Run tests"
	@echo "  make run             - Start scheduled runner"
	@echo "  make run-once        - Run one search cycle"
	@echo "  make lint            - Run syntax check"
	@echo "  make format          - Format with black (if installed)"
	@echo "  make clean           - Remove caches and build artifacts"

venv:
	$(PYTHON) -m venv $(VENV)

install: venv
	$(VENV_PIP) install -e .

dev-install: install
	$(VENV_PIP) install -e ".[dev]"

build: dev-install
	$(VENV_PYTHON) -m build

test: dev-install
	$(VENV_PYTHON) -m pytest tests/ -v

run: install
	$(VENV_BIN)/apartment-agent --config $(CONFIG)

run-once: install
	$(VENV_BIN)/apartment-agent --config $(CONFIG) --once

lint: install
	$(VENV_PYTHON) -m compileall -q apartment_agent tests

format: install
	@if $(VENV_PYTHON) -m black --version >/dev/null 2>&1; then \
		$(VENV_PYTHON) -m black apartment_agent tests; \
	else \
		echo "black is not installed. Install with: $(VENV_PIP) install black"; \
	fi

clean:
	rm -rf build dist .pytest_cache .mypy_cache .ruff_cache htmlcov
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
