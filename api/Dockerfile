# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies and Poetry
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libgomp1 \
    && pip install --no-cache-dir poetry==2.0.1 \
    && rm -rf /var/lib/apt/lists/*

# Configure Poetry to not use virtualenvs in Docker
RUN poetry config virtualenvs.create false

# Copy and install core package first
COPY ./core /core
RUN cd /core && poetry install --only main

# Copy Poetry configuration files
COPY ./api/pyproject.toml ./api/poetry.lock ./api/README.md ./

# Install api dependencies
RUN poetry install --only main --no-root

# Copy application source code
COPY ./api/src ./src

# Install the api package itself
RUN poetry install --only-root

# Expose FastAPI port
EXPOSE 8002

# Start the API with Uvicorn
CMD ["poetry", "run", "uvicorn", "MiravejaApi.main:app", "--host", "0.0.0.0", "--port", "8002", "--reload"]
