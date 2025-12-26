#!/bin/bash
#
# Test Runner Script
# Runs tests after waiting for services to be healthy
#
# Usage:
#   ./scripts/run_tests.sh [test_type] [options]
#
# Test types:
#   unit        - Run unit tests only (no dependencies required)
#   integration - Run integration tests (requires running services)
#   e2e         - Run end-to-end tests (requires full stack)
#   smoke       - Run quick smoke tests
#   all         - Run all tests
#
# Options:
#   --no-wait   - Skip waiting for services
#   --coverage  - Generate coverage report
#   --verbose   - Verbose output

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
APP_URL="${TEST_APP_URL:-http://localhost:8000}"
PROMETHEUS_URL="${TEST_PROMETHEUS_URL:-http://localhost:9090}"
GRAFANA_URL="${TEST_GRAFANA_URL:-http://localhost:3000}"

# Default values
TEST_TYPE="${1:-all}"
WAIT_FOR_SERVICES=true
COVERAGE=false
VERBOSE=""
MAX_WAIT=120

# Parse arguments
shift || true
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-wait)
            WAIT_FOR_SERVICES=false
            shift
            ;;
        --coverage)
            COVERAGE=true
            shift
            ;;
        --verbose|-v)
            VERBOSE="-v"
            shift
            ;;
        *)
            shift
            ;;
    esac
done

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       AI Monitoring Test Runner            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Function to wait for a service
wait_for_service() {
    local url=$1
    local name=$2
    local timeout=${3:-60}
    local start_time=$(date +%s)

    echo -e "${YELLOW}⏳ Waiting for $name at $url...${NC}"

    while true; do
        if curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null | grep -q "200\|204"; then
            echo -e "${GREEN}✓ $name is ready${NC}"
            return 0
        fi

        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))

        if [ $elapsed -ge $timeout ]; then
            echo -e "${RED}✗ Timeout waiting for $name${NC}"
            return 1
        fi

        sleep 2
    done
}

# Function to wait for all services
wait_for_all_services() {
    echo -e "${BLUE}Waiting for services to be ready...${NC}"
    echo ""

    local all_ready=true

    # Wait for application
    if ! wait_for_service "$APP_URL/health" "Application" $MAX_WAIT; then
        all_ready=false
    fi

    # Wait for Prometheus
    if ! wait_for_service "$PROMETHEUS_URL/-/ready" "Prometheus" $MAX_WAIT; then
        echo -e "${YELLOW}⚠ Prometheus not available, some tests may be skipped${NC}"
    fi

    # Wait for Grafana
    if ! wait_for_service "$GRAFANA_URL/api/health" "Grafana" $MAX_WAIT; then
        echo -e "${YELLOW}⚠ Grafana not available, some tests may be skipped${NC}"
    fi

    echo ""

    if [ "$all_ready" = false ]; then
        echo -e "${RED}Some required services are not ready${NC}"
        return 1
    fi

    return 0
}

# Build pytest command
build_pytest_cmd() {
    local cmd="pytest"

    case $TEST_TYPE in
        unit)
            cmd="$cmd tests/unit/"
            ;;
        integration)
            cmd="$cmd tests/integration/ -m integration"
            ;;
        e2e)
            cmd="$cmd tests/e2e/ -m e2e"
            ;;
        smoke)
            cmd="$cmd -m smoke"
            ;;
        all)
            cmd="$cmd tests/"
            ;;
        *)
            echo -e "${RED}Unknown test type: $TEST_TYPE${NC}"
            echo "Valid types: unit, integration, e2e, smoke, all"
            exit 1
            ;;
    esac

    if [ "$COVERAGE" = true ]; then
        cmd="$cmd --cov=app --cov-report=html --cov-report=term"
    fi

    if [ -n "$VERBOSE" ]; then
        cmd="$cmd -v"
    fi

    echo "$cmd"
}

# Run tests
run_tests() {
    cd "$PROJECT_DIR"

    local pytest_cmd=$(build_pytest_cmd)

    echo -e "${BLUE}Running: $pytest_cmd${NC}"
    echo ""

    # Set environment variables for tests
    export TEST_APP_HOST="${TEST_APP_HOST:-localhost}"
    export TEST_APP_PORT="${TEST_APP_PORT:-8000}"
    export TEST_PROMETHEUS_HOST="${TEST_PROMETHEUS_HOST:-localhost}"
    export TEST_PROMETHEUS_PORT="${TEST_PROMETHEUS_PORT:-9090}"
    export TEST_GRAFANA_HOST="${TEST_GRAFANA_HOST:-localhost}"
    export TEST_GRAFANA_PORT="${TEST_GRAFANA_PORT:-3000}"
    export PYTHONPATH="${PROJECT_DIR}/app:${PROJECT_DIR}/tests:${PYTHONPATH:-}"

    eval "$pytest_cmd"
}

# Main execution
main() {
    echo -e "${BLUE}Test type: ${TEST_TYPE}${NC}"
    echo -e "${BLUE}Wait for services: ${WAIT_FOR_SERVICES}${NC}"
    echo -e "${BLUE}Coverage: ${COVERAGE}${NC}"
    echo ""

    # Wait for services if needed (not for unit tests)
    if [ "$WAIT_FOR_SERVICES" = true ] && [ "$TEST_TYPE" != "unit" ]; then
        if ! wait_for_all_services; then
            if [ "$TEST_TYPE" = "unit" ]; then
                echo -e "${YELLOW}Continuing with unit tests only...${NC}"
            else
                echo -e "${RED}Cannot run $TEST_TYPE tests without services${NC}"
                exit 1
            fi
        fi
    fi

    echo -e "${BLUE}Starting tests...${NC}"
    echo ""

    if run_tests; then
        echo ""
        echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║           All tests passed! ✓              ║${NC}"
        echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
        exit 0
    else
        echo ""
        echo -e "${RED}╔════════════════════════════════════════════╗${NC}"
        echo -e "${RED}║           Some tests failed ✗              ║${NC}"
        echo -e "${RED}╚════════════════════════════════════════════╝${NC}"
        exit 1
    fi
}

main
