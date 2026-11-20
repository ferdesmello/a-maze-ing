PYTHON		= python3
PIP			= pip
MAIN_SCRIPT	= a_maze_ing.py
CONFIG_FILE	= config.txt
VENV_DIR	= venv
VENV_BIN	= $(VENV_DIR)/bin

.PHONY: all install run debug clean lint lint-strict help

all: run

# Install project dependencies
install:
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_BIN)/$(PIP) install --upgrade pip
	@if [ -f requirements.txt ]; then \
		$(VENV_BIN)/$(PIP) install -r requirements.txt; \
	fi

# Execute the main script
run:
	@if [ -d "$(VENV_DIR)" ]; then \
		$(VENV_BIN)/$(PYTHON) $(MAIN_SCRIPT) $(CONFIG_FILE); \
	else \
		$(PYTHON) $(MAIN_SCRIPT) $(CONFIG_FILE); \
	fi

# Run the main script in debug mode using pdb
debug:
	@if [ -d "$(VENV_DIR)" ]; then \
		$(VENV_BIN)/$(PYTHON) -m pdb $(MAIN_SCRIPT) $(CONFIG_FILE); \
	else \
		$(PYTHON) -m pdb $(MAIN_SCRIPT) $(CONFIG_FILE); \
	fi

# Remove temporary files or caches
clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache
	find . -type f -name "*.pyc" -delete

# Mandatory lint rule with specified flags
lint:
	@if [ -d "$(VENV_DIR)" ]; then \
		$(VENV_BIN)/flake8 . && \
		$(VENV_BIN)/mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs .; \
	else \
		flake8 . && \
		mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs .; \
	fi

# Optional strict lint rule
lint-strict:
	@if [ -d "$(VENV_DIR)" ]; then \
		$(VENV_BIN)/flake8 . && \
		$(VENV_BIN)/mypy --strict .; \
	else \
		flake8 . && \
		mypy --strict .; \
	fi

help:
	@echo "Available targets:"
	@echo "  install     - Create a virtual environment and install dependencies"
	@echo "  run         - Execute the main maze generator script"
	@echo "  debug       - Run the script using Python's built-in debugger (pdb)"
	@echo "  clean       - Remove cache and temporary files"
	@echo "  lint        - Run flake8 and mypy with required standard flags"
	@echo "  lint-strict - Run flake8 and mypy with strict mode"
