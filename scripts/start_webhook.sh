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
LOG_FILE="$PROJECT_ROOT/logs/webhook.log"

# Ensure logs directory exists
mkdir -p "$PROJECT_ROOT/logs"

# Check if already running
if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    echo -e "${RED}Webhook server already running (PID $(cat "$PID_FILE"))${NC}"
    echo -e "Run ${BLUE}./scripts/stop_webhook.sh${NC} to stop it first."
    exit 1
fi

# Cleanup on exit
cleanup() {
    echo -e "\n${BLUE}Shutting down webhook server...${NC}"
    jobs -p | xargs -r kill 2>/dev/null
    wait 2>/dev/null
    rm -f "$PID_FILE"
    echo -e "${GREEN}Stopped.${NC}"
    exit 0
}

trap cleanup EXIT INT TERM

# Start webhook server (tee to both terminal and log file)
echo -e "${BLUE}Starting webhook server...${NC}"
echo -e "${BLUE}  Local:  http://localhost:8001${NC}"
echo -e "${BLUE}  Public: https://agent-dev.tail44087f.ts.net${NC}"
echo -e "${BLUE}  Logs:   $LOG_FILE${NC}"
echo ""
echo "Press Ctrl+C to stop..."
echo ""

cd "$PROJECT_ROOT"
PYTHONUNBUFFERED=1 uv run adws/trigger_webhook.py 2>&1 | tee "$LOG_FILE" &
WEBHOOK_PID=$!
echo "$WEBHOOK_PID" > "$PID_FILE"

wait
