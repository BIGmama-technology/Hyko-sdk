#!/usr/bin/env bash
# Print trace of commands
set -x

pyenv install

poetry install

poetry run pre-commit install --hook-type pre-commit --hook-type pre-push
poetry run gitlint install-hook

poetry shell
