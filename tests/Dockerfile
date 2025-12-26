# Test runner container
FROM python:3.11-slim

WORKDIR /tests

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy test requirements first for caching
COPY tests/requirements.txt /tests/requirements.txt

# Install test dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (needed for unit tests)
COPY app/ /app/

# Copy test code
COPY tests/ /tests/
COPY pytest.ini /pytest.ini

# Set environment variables
ENV PYTHONPATH=/app:/tests
ENV PYTHONUNBUFFERED=1

# Default: run all tests
CMD ["pytest", "-v", "--tb=short"]
