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

# Configure Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    PYTHONPATH=/app/src

# Copy Poetry configuration files
COPY pyproject.toml poetry.lock ./

# Install dependencies only (not the project itself)
RUN poetry install --only main --no-root && rm -rf $POETRY_CACHE_DIR

# Copy source code
COPY . .

# Install the project itself in the final step
RUN poetry install --only-root

# Expose FastAPI port
EXPOSE 8000

# Start the API with Uvicorn using Poetry
CMD ["poetry", "run", "uvicorn", "src.Miraveja.main:app", "--host", "0.0.0.0", "--port", "8000"]
