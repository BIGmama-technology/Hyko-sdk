.PHONY: setup lint format

setup:
	@./scripts/setup.sh

lint:
	@ruff check .

test:
	@pytest .

format:
	@ruff format .
