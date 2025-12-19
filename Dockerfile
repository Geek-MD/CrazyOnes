# Use Alpine Linux for ARM architecture (suitable for Raspberry Pi 3B)
# Alpine is lightweight and includes all necessary build tools
FROM python:3.10-alpine

# Set working directory
WORKDIR /app

# Install system dependencies required for Python packages
# - gcc, musl-dev, linux-headers: Required for building Python packages
# - libffi-dev: Required for some cryptography packages
# - libxml2-dev, libxslt-dev: Required for lxml
RUN apk update && \
    apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    libffi-dev \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/cache/apk/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY crazyones.py .
COPY config.json .
COPY scripts/ ./scripts/

# Create data directory for persistent storage
RUN mkdir -p /app/data

# Copy entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Set entrypoint
ENTRYPOINT ["docker-entrypoint.sh"]
