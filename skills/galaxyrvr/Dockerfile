# GalaxyRVR Docker Container
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    iputils-ping \
    iproute2 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
COPY requirements-web.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt -r requirements-web.txt

# Copy application files
COPY *.py ./
COPY templates/ ./templates/

# Expose web dashboard port
EXPOSE 5050

# Default to web dashboard (can override with docker run command)
CMD ["python", "web_dashboard.py"]
