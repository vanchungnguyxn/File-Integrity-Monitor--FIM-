# File Integrity Monitor Docker Image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ src/
COPY pyproject.toml .
COPY README.md .
COPY LICENSE .

# Install the package
RUN pip install -e .

# Create a non-root user
RUN groupadd -r fim && useradd -r -g fim fim
RUN chown -R fim:fim /app
USER fim

# Create workspace directory
RUN mkdir -p /workspace
WORKDIR /workspace

# Set the default command
ENTRYPOINT ["fim"]
CMD ["--help"]
