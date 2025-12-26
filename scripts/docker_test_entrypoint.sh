#!/bin/bash
#
# Docker test entrypoint script
# Waits for services and runs tests in Docker container
#

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration from environment
APP_HOST="${TEST_APP_HOST:-app}"
APP_PORT="${TEST_APP_PORT:-8000}"
PROMETHEUS_HOST="${TEST_PROMETHEUS_HOST:-prometheus}"
PROMETHEUS_PORT="${TEST_PROMETHEUS_PORT:-9090}"
MAX_RETRIES="${MAX_RETRIES:-60}"
RETRY_INTERVAL="${RETRY_INTERVAL:-2}"

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    AI Monitoring Docker Test Runner        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Function to wait for service
wait_for_service() {
    local host=$1
    local port=$2
    local path=$3
    local name=$4
    local retries=0

    echo -e "${YELLOW}⏳ Waiting for $name ($host:$port$path)...${NC}"

    while [ $retries -lt $MAX_RETRIES ]; do
        if curl -sf "http://${host}:${port}${path}" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ $name is ready${NC}"
            return 0
        fi

        retries=$((retries + 1))
        sleep $RETRY_INTERVAL
    done

    echo -e "${RED}✗ Timeout waiting for $name${NC}"
    return 1
}

# Wait for application
echo -e "${BLUE}Waiting for services to start...${NC}"
echo ""

wait_for_service "$APP_HOST" "$APP_PORT" "/health" "Application"

# Optionally wait for observability stack
if [ "${WAIT_FOR_OBSERVABILITY:-true}" = "true" ]; then
    wait_for_service "$PROMETHEUS_HOST" "$PROMETHEUS_PORT" "/-/ready" "Prometheus" || \
        echo -e "${YELLOW}⚠ Prometheus not ready, some tests may be skipped${NC}"
fi

echo ""
echo -e "${BLUE}Starting tests...${NC}"
echo ""

# Run pytest with provided arguments or defaults
if [ $# -eq 0 ]; then
    pytest -v --tb=short
else
    pytest "$@"
fi
