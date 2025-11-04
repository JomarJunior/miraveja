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

# Copy core package first (needed for miraveja-core dependency)
COPY ./core /core

# Install core package directly with pip first
RUN cd /core && pip install -e .

# Add core package to Python path (for runtime)
ENV PYTHONPATH="${PYTHONPATH}:/core/src"

# Copy Poetry configuration files  
COPY ./worker/pyproject.toml ./worker/poetry.lock* ./worker/README.md ./

# Configure Poetry to not use virtualenvs in Docker
RUN poetry config virtualenvs.create false

# Install dependencies (excluding miraveja-core which is already installed)
RUN poetry install --only main --no-root

# Copy source code
COPY ./worker/src ./src

# Install the project itself in the final step
RUN poetry install --only-root

# Worker does not expose ports (background service)

# Start the worker process
CMD ["poetry", "run", "python", "src/MiravejaWorker/main.py"]
