# 🐍 MiraVeja API Service

The **MiraVeja API** is the core backend service for the MiraVeja AI-powered image gallery.  
It handles **image uploads, metadata management, search, recommendations**, and acts as the central coordinator for other services like the worker, vector database, object storage, and messaging system.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Running with Docker](#running-with-docker)
- [Development](#development)
- [Testing](#testing)
- [Linting & Formatting](#linting--formatting)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)

## Features

- REST API built with **FastAPI**.
- Async communication with **Kafka** for event-driven workflows.
- Integration with **MinIO** for image storage.
- Integration with **Qdrant** for vector-based semantic search.
- User authentication and authorization via **Keycloak** (supports SSO).
- Modular architecture with **API and background worker** separation.

## Architecture

The [High-Level Container Diagram](../docs/diagrams/high-level-container.puml) illustrates the main components:

- **API Service:** Central coordinator for all business logic.
- **Worker Service:** Processes heavy tasks asynchronously (thumbnails, embeddings, moderation).
- **Postgres:** Stores structured metadata (users, assets, tags, etc.).
- **MinIO:** Object storage for images.
- **Qdrant:** Vector database for semantic search.
- **Kafka:** Event streaming for decoupled communication.
- **Keycloak:** Identity and access management.

## Getting Started

### Requirements

- Python >= 3.10
- [Poetry](https://python-poetry.org/) for dependency management
- Docker & Docker Compose (for full stack setup)

## Environment Variables

The API requires several environment variables. These can be defined in a `.env` file:

```env
DATABASE_URL=postgresql://miraveja:miraveja_pass@postgres:5432/miraveja_db
MINIO_ENDPOINT=http://minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadminpass
QDRANT_URL=http://qdrant:6333
KAFKA_BROKER=kafka:9092
KEYCLOAK_URL=http://keycloak:8080
````

## Running with Docker

Build and run the API container with Docker Compose:

```bash
docker-compose up -d api
```

Check logs:

```bash
docker-compose logs -f api
```

The API will be available at `http://localhost:8000`.

## Development

Install dependencies using Poetry:

```bash
poetry install --with dev
```

Run the development server:

```bash
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Testing

Run tests with coverage:

```bash
poetry run pytest --cov=src --cov-report=term-missing
```

Test files should be placed under the `tests/` directory.

## Linting & Formatting

- **Black** (code formatting):

```bash
poetry run black src tests
```

- **Isort** (import sorting):

```bash
poetry run isort src tests
```

- **Pylint** (code linting):

```bash
poetry run pylint src
```

## API Documentation

The API automatically generates **OpenAPI docs**:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Contributing

- Follow **PEP8 / Black / Isort** conventions.
- Write tests for new features.
- Run `pytest` and lint checks before submitting pull requests.
- Use Kafka events and async workflows for heavy tasks instead of blocking API requests.

> The MiraVeja API is the backbone of the platform — it connects all services, manages events, and ensures a smooth experience for users and workers alike.
