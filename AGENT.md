# Repo Guidelines

This repository uses a basic code-style and linting setup.

## Development Rules

- Format code with `black` and organize imports with `isort`.
- Ensure `flake8`, `pylint`, and `mypy` pass without errors.
- Use the provided `./run_checks.sh` script to run all checks.

## Tests

Currently this repository does not include automated unit tests, but
running `./run_checks.sh` is required before committing any changes.

