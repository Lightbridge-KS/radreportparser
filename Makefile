# Default target (runs when you just type 'make')
.DEFAULT_GOAL := help

# Help target - lists available commands
help:
	@echo "Available commands:"
	@echo "  docs    - Build Docs"
	@echo "  docs-preview    - Preview Docs"

docs doc documentation:
	$(MAKE) -C docs docs

doc-preview docs-preview:
	cd docs && quarto preview

build-pkg:
	python -m build

# Mark targets that don't create files
.PHONY: help docs docs-serve build-pkg