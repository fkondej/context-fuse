#!/bin/bash
set -e

echo "Running Black..."
black context_fuse.py

echo "Running isort..."
isort context_fuse.py

echo "Running Flake8..."
flake8 context_fuse.py

echo "Running Pylint..."
pylint context_fuse.py

echo "Running mypy..."
mypy context_fuse.py
