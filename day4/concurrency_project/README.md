
# Day 4 — Async API Data Aggregator

## Overview
A Python application that fetches users, posts, and comments
concurrently from a public REST API.

## Technologies
- Python 3.11
- asyncio
- httpx
- pytest
- pytest-cov
- uv

## Features
- Concurrent HTTP GET requests
- Async HTTP client
- Error handling and request timeouts
- JSON response validation
- Automated tests with mocked HTTP responses

## Project Structure
- api_client.py — API communication and aggregation
- main.py — Application entry point
- test_api_client.py — Automated tests

## Installation
uv sync

## Run
uv run python main.py

## Tests
uv run pytest -v

## Coverage
uv run pytest --cov=api_client --cov-report=term-missing

## Results
- 6 tests passed
- 100% statement coverage for api_client.py

## API
https://jsonplaceholder.typicode.com
