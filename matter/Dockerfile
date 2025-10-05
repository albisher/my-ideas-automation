# Matter Server Dockerfile
# Based on Python Matter Server implementation
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    bluetooth \
    bluez \
    libbluetooth-dev \
    avahi-daemon \
    libavahi-compat-libdnssd-dev \
    libnl-3-dev \
    libnl-route-3-dev \
    libglib2.0-dev \
    libdbus-1-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python Matter Server with all dependencies
RUN pip install --no-cache-dir \
    python-matter-server[server] \
    aiorun \
    cryptography

# Create data directory
RUN mkdir -p /data

# Set working directory
WORKDIR /data

# Expose ports
EXPOSE 5580 5581

# Run Matter Server
CMD ["python", "-m", "matter_server.server", "--storage-path", "/data", "--port", "5580"]

