# File Server Docker Image
# Multi-stage build for smaller image size

FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN groupadd -r fileserver && useradd -r -g fileserver fileserver

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY src/ ./src/
COPY .env.example ./.env

# Create storage directory
RUN mkdir -p /data && chown -R fileserver:fileserver /data

# Switch to non-root user
USER fileserver

# Set environment variables
ENV PYTHONPATH=/app
ENV STORAGE_DIR=/data
ENV HOST=0.0.0.0
ENV PORT=8008

# Expose port
EXPOSE 8008

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8008/health')" || exit 1

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8008"]
