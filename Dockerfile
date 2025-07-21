# Multi-stage build for NMAP-AI Docker image
FROM python:3.10-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    nmap \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd --create-home --shell /bin/bash app

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data logs results config && \
    chown -R app:app /app

# Switch to app user
USER app

# Initialize AI models and databases (this would be done at runtime in production)
RUN python -m nmap_ai.setup --init-models --init-db || true

# Expose ports
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/api/health')" || exit 1

# Default command
CMD ["python", "-m", "nmap_ai", "--web", "--host", "0.0.0.0", "--port", "8080"]

# Development stage
FROM base as development

USER root

# Install development dependencies
RUN pip install -r requirements-dev.txt

# Install additional development tools
RUN apt-get update && apt-get install -y \
    vim \
    curl \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER app

# Override command for development
CMD ["python", "-m", "nmap_ai", "--web", "--host", "0.0.0.0", "--port", "8080", "--debug"]

# Production stage
FROM base as production

# Production optimizations
ENV PYTHONOPTIMIZE=1

# Remove development files
RUN find . -name "*.pyc" -delete && \
    find . -name "__pycache__" -type d -exec rm -rf {} + || true

# Production command with gunicorn
RUN pip install gunicorn

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "nmap_ai.web.main:app"]
