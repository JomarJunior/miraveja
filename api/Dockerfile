# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies and Poetry
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && pip install poetry \
    && rm -rf /var/lib/apt/lists/*

# Copy shared package first (needed for miraveja-core dependency)
COPY ./shared /shared

# Add shared package to Python path
ENV PYTHONPATH="${PYTHONPATH}:/shared/src"

# Copy Poetry configuration files  
COPY ./api/pyproject.toml ./api/poetry.lock ./api/README.md ./

# Configure Poetry to not use virtualenvs in Docker
RUN poetry config virtualenvs.create false

# Install dependencies (miraveja-core already installed above)
RUN poetry install --only main --no-root

# Copy source code
COPY ./api/src ./src
COPY ./api/alembic.ini ./api/alembic ./

# Install the project itself in the final step
RUN poetry install --only-root

# Expose FastAPI port
EXPOSE 8002

# Start the API with Uvicorn using Poetry
CMD ["poetry", "run", "uvicorn", "src.MiravejaApi.main:app", "--host", "0.0.0.0", "--port", "8002", "--reload", "--reload-dir", "/app", "--reload-dir", "/shared/src"]
