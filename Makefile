# Help target - lists available commands
help:
	@echo "Available commands:"

# Test
.PHONY: test-ci
test-ci:
	pytest --cov=radreportparser --cov-report=xml

# Install in editable mode
.PHONY: install-edit
install-edit: 
	python -m pip install -e .

# Doc in CI environment
.PHONY: docs-ci
docs-ci: 
	$(MAKE) -C docs docs

# Doc in interative environment
.PHONY: docs doc documentation
docs doc documentation: install-edit
	$(MAKE) -C docs docs

# Quarto Preview
.PHONY: preview
preview: docs
	cd docs && quarto preview

# Quarto Preview (No Doc)
.PHONY: prev
prev:
	cd docs && quarto preview

# Quarto Render
.PHONY: render
render: docs
	cd docs && quarto render

.PHONY: build-pkg
build-pkg:
	python -m build


# Default target (runs when you just type 'make')
.DEFAULT_GOAL := help