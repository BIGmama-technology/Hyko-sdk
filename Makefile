.PHONY: setup lint format

.PHONY: setup
setup: ## - Setup the repository
	@echo "Setting up the sdk..."
	@pyenv install || true && \
		poetry install && \
		poetry run pre-commit install --hook-type pre-commit --hook-type pre-push && \
		poetry run gitlint install-hook || true

lint:
	poetry run ruff check .

format:
	poetry run ruff format .
