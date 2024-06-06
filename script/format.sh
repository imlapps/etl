#!/bin/bash 

set -e 

cd "$(dirname "$0")/.."


poetry run isort wikipedia_transform
poetry run black wikipedia_transform
