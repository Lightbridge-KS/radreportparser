# Default target (runs when you just type 'make')
.DEFAULT_GOAL := help

# Help target - lists available commands
help:
	@echo "Available commands:"
# Test
test-ci:
	pytest --cov=radreportparser --cov-report=xml

# Install in editable mode
install-edit: 
	python -m pip install -e .

# Doc in CI environment
docs-ci: 
	$(MAKE) -C docs docs

# Doc in interative environment
docs doc documentation: install-edit
	$(MAKE) -C docs docs

# Quarto Preview
preview: docs
	cd docs && quarto preview

build-pkg:
	python -m build

# Mark targets that don't create files
.PHONY: help docs docs-ci install-edit preview build-pkg