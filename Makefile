.PHONY: install
install: ## Install the virtual environment, pull submodules, and install the pre-commit hooks
	@echo "🚀 Creating virtual environment using uv"
	@uv sync
	@sudo apt install -y moreutils
	@uv run pre-commit install
	@uv run scripts/setup_huggingface_structure.sh ffr
	@uv run git submodule update --init --recursive

.PHONY: ffr-charts
ffr-charts: ## Upload FFR charts to HuggingFace Datasets repo (TODO: need to restrict this to certain roles in GitHub)
	@echo "🚀 Downloading dataset from Flash Flash Revolution's API..."
	@uv run python huggingface/datasets/ffr/charts/download_ffr_charts.py
	@uv run scripts/update_huggingface.py \
		--repo-id stepmanai/ffr_charts \
		--folder huggingface/datasets/ffr/charts \
		--repo-type dataset

.PHONY: clean
clean: ## Factory reset workspace in local environment
	@echo "🧹 Cleaning up build, bytecode, and documentation files..."
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -type f -name '*.py[co]' -delete
	@rm -rf .venv dist build .mypy_cache .pytest_cache .ruff_cache site acubed.egg-info huggingface
	@echo "✅ Clean complete."

.PHONY: check
check: ## Run code quality tools.
	@echo "🚀 Checking lock file consistency with 'pyproject.toml'"
	@uv lock --locked
	@echo "🚀 Linting code: Running pre-commit"
	@uv run pre-commit run -a
	@echo "🚀 Static type checking: Running mypy"
	@uv run mypy

.PHONY: test
test: ## Test the code with pytest
	@echo "🚀 Testing code: Running pytest"
	@uv run python -m pytest --doctest-modules

.PHONY: build
build: clean-build ## Build wheel file
	@echo "🚀 Creating wheel file"
	@uvx --from build pyproject-build --installer uv

.PHONY: clean-build
clean-build: ## Clean build artifacts
	@echo "🚀 Removing build artifacts"
	@uv run python -c "import shutil; import os; shutil.rmtree('dist') if os.path.exists('dist') else None"

.PHONY: publish
publish: ## Publish a release to PyPI.
	@echo "🚀 Publishing."
	@uvx twine upload --repository-url https://upload.pypi.org/legacy/ dist/*

.PHONY: build-and-publish
build-and-publish: build publish ## Build and publish.

.PHONY: docs-test
docs-test: ## Test if documentation can be built without warnings or errors
	@uv run mkdocs build -s

.PHONY: docs
docs: ## Build and serve the documentation
	@uv run mkdocs serve

.PHONY: help
help:
	@uv run python -c "import re; \
	[[print(f'\033[36m{m[0]:<20}\033[0m {m[1]}') for m in re.findall(r'^([a-zA-Z_-]+):.*?## (.*)$$', open(makefile).read(), re.M)] for makefile in ('$(MAKEFILE_LIST)').strip().split()]"

.DEFAULT_GOAL := help
