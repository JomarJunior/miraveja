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
COPY ./worker/pyproject.toml ./worker/poetry.lock ./worker/README.md ./

# Install worker dependencies
RUN poetry install --only main --no-root

# Copy application source code
COPY ./worker/src ./src

# Install the worker package itself
RUN poetry install --only-root

# Worker does not expose ports (background service)

# Start the worker process
CMD ["poetry", "run", "python", "-m", "MiravejaWorker.main"]
