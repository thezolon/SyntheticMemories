FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY service/ /app/
COPY config.yml /app/config.yml
COPY web/ /app/web/

# Create data directory
RUN mkdir -p /data

# Expose port
EXPOSE 8768

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8768/health')"

# Run service
CMD ["python", "memory_service.py"]
