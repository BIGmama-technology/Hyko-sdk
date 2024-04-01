.PHONY: setup lint format

setup:
	@./scripts/setup.sh

lint:
	@ruff check .

test:
	@pytest .

test: @docker compose -f docker-compose.test.yml up --build --exit-code-from hyko_sdk_test



format:
	@ruff format .
