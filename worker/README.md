# 🔄 MiraVeja Worker Service

Background worker service for MiraVeja that processes asynchronous tasks via Kafka event streaming.

## Overview

The Worker service consumes events from Kafka and processes background tasks such as:

- Generating image embeddings for semantic search
- Creating thumbnails for images
- Processing metadata extraction
- Handling long-running computational tasks

## Architecture

The worker follows the same **Clean Architecture** pattern as the API:

```bash
worker/
├── src/
│   └── MiravejaWorker/
│       ├── Configuration/           # Configuration models (Pydantic)
│       │   └── Models.py
│       ├── Shared/                  # Shared infrastructure
│       │   ├── WorkerDependencies.py    # Core DI registration
│       │   └── Events/
│       │       └── Infrastructure/
│       │           └── Kafka/
│       │               └── EventConsumer.py
│       ├── Gallery/                 # Gallery bounded context
│       │   ├── Infrastructure/
│       │   │   └── Handlers/       # Event handlers
│       │   └── Domain/
│       │       └── Services/       # Worker-specific services
│       ├── Member/                  # Member bounded context
│       │   └── Infrastructure/
│       │       └── Handlers/
│       └── main.py                 # Application entry point
├── tests/                          # Unit and integration tests
├── pyproject.toml                  # Poetry dependencies
├── Dockerfile                      # Container definition
└── README.md
```

## Key Components

### 1. Configuration (`Configuration/Models.py`)

- `WorkerConfig`: Main configuration model
- `LoggerConfig`: Logging configuration
- `DatabaseConfig`: Database connection settings
- `QdrantConfig`: Vector database configuration
- All configs load from environment variables

### 2. Event Consumer (`Shared/Events/Infrastructure/Kafka/EventConsumer.py`)

- Consumes events from Kafka topics
- Routes events to registered handlers
- Supports wildcard event subscriptions
- Handles errors gracefully with logging

### 3. Dependency Injection (`Shared/WorkerDependencies.py`)

- Registers infrastructure dependencies
- Database engine and session management
- Boto3 S3 client for MinIO
- Unit of Work factory for transactions

### 4. Main Entry Point (`main.py`)

- Loads configuration from environment
- Initializes DI container
- Registers all dependencies
- Starts Kafka consumer loop

## Getting Started

### Prerequisites

- Python >= 3.10
- [Poetry](https://python-poetry.org/) for dependency management
- Access to Kafka broker
- Access to PostgreSQL database
- Access to MinIO/S3 storage

### Installation

```bash
# Navigate to worker directory
cd worker

# Install dependencies
poetry install

# Or using pip
pip install -e .
```

### Configuration

Create a `.env` file in the project root (or set environment variables):

```env
# Worker
WORKER_NAME=MiravejaWorker
WORKER_VERSION=0.0.0
DEBUG=false

# Logging
LOGGER_NAME=MiravejaWorker
LOGGER_LEVEL=INFO
LOGGER_TARGET=FILE
LOGGER_DIR=./logs
LOGGER_FILENAME=worker.log

# Database
DATABASE_TYPE=postgresql
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USER=miraveja
DATABASE_PASSWORD=miraveja
DATABASE_NAME=miraveja
DATABASE_MAX_CONNECTIONS=10

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC_PREFIX=miraveja
KAFKA_CONSUMER_GROUP_ID=miraveja-worker-group
KAFKA_CONSUMER_AUTO_OFFSET_RESET=earliest

# MinIO (S3-compatible storage)
MINIO_ENDPOINT_URL=http://localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_REGION=us-east-1
MINIO_BUCKET_NAME=miraveja

# Qdrant (Vector Database)
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=image_embeddings
```

### Running the Worker

#### Development

```bash
# Using Poetry
poetry run python src/MiravejaWorker/main.py

# Or activate the virtual environment
poetry shell
python src/MiravejaWorker/main.py
```

#### Docker

```bash
# Build the image
docker build -t miraveja-worker .

# Run the container
docker run --env-file .env miraveja-worker
```

#### Docker Compose

```bash
# From project root
docker-compose up worker
```

## Event Processing Flow

1. **Event Published**: API publishes event to Kafka (e.g., `image.uploaded`)
2. **Consumer Receives**: Worker's `KafkaEventConsumer` receives the event
3. **Event Routing**: Consumer routes to registered handler(s)
4. **Handler Execution**: Handler processes the event (e.g., generates embedding)
5. **Result Storage**: Handler stores results (e.g., embedding to Qdrant)
6. **Logging**: All steps are logged for observability

## Adding New Event Handlers

### 1. Create Handler

```python
# Gallery/Infrastructure/Handlers/ImageUploadedEventHandler.py
from MiravejaCore.Shared.Events.Domain.Interfaces import DomainEvent
from MiravejaCore.Shared.Logging.Interfaces import ILogger


class ImageUploadedEventHandler:
    def __init__(self, logger: ILogger):
        self._logger = logger
    
    async def Handle(self, event: DomainEvent) -> None:
        imageId = event.aggregateId
        self._logger.Info(f"Processing image.uploaded: {imageId}")
        # Process the event...
```

### 2. Register Handler

```python
# Gallery/Infrastructure/GalleryWorkerDependencies.py
class GalleryWorkerDependencies:
    @staticmethod
    def RegisterDependencies(container: Container):
        container.RegisterFactories({
            ImageUploadedEventHandler.__name__: lambda c: ImageUploadedEventHandler(
                logger=c.Get(ILogger.__name__),
            ),
        })
```

### 3. Subscribe to Events

```python
# In main.py
from MiravejaWorker.Gallery.Infrastructure.GalleryWorkerDependencies import GalleryWorkerDependencies

# Register dependencies
GalleryWorkerDependencies.RegisterDependencies(container)

# Subscribe handler to event
kafkaConsumer.Subscribe(
    "image.uploaded",
    container.Get(ImageUploadedEventHandler.__name__)
)
```

## Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src --cov-report=term-missing

# Run specific test file
poetry run pytest tests/Gallery/test_image_uploaded_handler.py
```

## Code Quality

```bash
# Format code
poetry run black src tests

# Sort imports
poetry run isort src tests

# Lint code
poetry run pylint src
```

## Deployment

The worker is deployed as a Docker container alongside other MiraVeja services:

```yaml
# docker-compose.yml
worker:
  build: ./worker
  env_file: .env
  depends_on:
    - kafka
    - postgres
    - minio
    - qdrant
  restart: unless-stopped
```

## Monitoring

- **Logs**: Structured logs written to `./logs/worker.log`
- **Metrics**: (TODO) Expose Prometheus metrics
- **Health**: (TODO) Health check endpoint

## Troubleshooting

### Worker Not Consuming Events

1. Check Kafka connection: `KAFKA_BOOTSTRAP_SERVERS`
2. Verify topic exists: `kafka-topics --list`
3. Check consumer group: `kafka-consumer-groups --describe --group miraveja-worker-group`

### Database Connection Issues

1. Verify credentials in `.env`
2. Check database is accessible: `psql -h localhost -U miraveja`
3. Review connection pool settings

### High Memory Usage

1. Adjust `DATABASE_MAX_CONNECTIONS`
2. Review batch processing logic
3. Consider adding memory limits in Docker

## Contributing

Follow the same conventions as the API:

- **Naming**: PascalCase for functions/methods, camelCase for variables
- **Architecture**: Clean Architecture with bounded contexts
- **Testing**: Write tests for all handlers and services
- **Documentation**: Document complex logic and configurations

## License

MIT License - See [LICENSE](../LICENSE) file
