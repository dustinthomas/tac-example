#!/usr/bin/env bash
set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( dirname "$SCRIPT_DIR" )"
PID_FILE="$PROJECT_ROOT/logs/webhook.pid"

# Stop webhook server
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo -e "${BLUE}Stopping webhook server (PID $PID)...${NC}"
        kill "$PID"
        # Wait up to 5 seconds for graceful shutdown
        for i in {1..5}; do
            if ! kill -0 "$PID" 2>/dev/null; then
                break
            fi
            sleep 1
        done
        # Force kill if still running
        if kill -0 "$PID" 2>/dev/null; then
            kill -9 "$PID" 2>/dev/null
        fi
        echo -e "${GREEN}Webhook server stopped.${NC}"
    else
        echo -e "${BLUE}Webhook server not running (stale PID file).${NC}"
    fi
    rm -f "$PID_FILE"
else
    echo -e "${BLUE}No PID file found. Checking for running processes...${NC}"
    PIDS=$(pgrep -f "trigger_webhook.py" 2>/dev/null || true)
    if [ -n "$PIDS" ]; then
        echo -e "${BLUE}Killing webhook processes: $PIDS${NC}"
        echo "$PIDS" | xargs kill 2>/dev/null
        echo -e "${GREEN}Done.${NC}"
    else
        echo -e "${BLUE}No webhook server running.${NC}"
    fi
fi

