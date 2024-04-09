.PHONY: setup lint format

setup:
	@echo "Setting up hyko python sdk..."
	@pyenv install || true && \
		poetry install && \
		poetry run pre-commit install --hook-type pre-commit --hook-type pre-push && \
		poetry run gitlint install-hook

lint:
	@ruff check .

test: 
	@docker compose -f docker-compose.test.yml up --build --exit-code-from hyko_sdk_test


format:
	@ruff format .
