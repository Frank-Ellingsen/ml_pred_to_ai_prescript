# Stage 1: Base image
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app/src

WORKDIR /app

# Install system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency definition
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create application user for security
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/data/processed /app/data/feedback /app/artifacts/models /app/artifacts/reports && \
    chown -R appuser:appuser /app

# Copy source code and configurations
COPY config/ /app/config/
COPY knowledge/ /app/knowledge/
COPY src/ /app/src/
COPY scripts/ /app/scripts/
COPY pyproject.toml /app/

# Switch to non-root user
USER appuser

# Initialize database schema on startup if not present
RUN python -m finance_ai.cli init-database && \
    python -m finance_ai.cli seed-database

EXPOSE 8000 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command launches FastAPI backend
CMD ["uvicorn", "finance_ai.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
