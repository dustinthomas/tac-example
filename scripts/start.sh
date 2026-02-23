#!/usr/bin/env bash
set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}Starting QCI Fab UI...${NC}"

# Derive PROJECT_ROOT from script location
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( dirname "$SCRIPT_DIR" )"

# Check vendor libs exist
VENDOR_DIR="$PROJECT_ROOT/backend/public/js/vendor"
if [ ! -f "$VENDOR_DIR/vue.esm-browser.js" ]; then
    echo -e "${RED}Vendor libs not found. Running download-vendor.sh...${NC}"
    bash "$SCRIPT_DIR/download-vendor.sh"
fi

# Build frontend if needed
APP_JS_DIR="$PROJECT_ROOT/backend/public/js/app"
if [ ! -f "$APP_JS_DIR/main.js" ]; then
    echo -e "${BLUE}Building frontend...${NC}"
    cd "$PROJECT_ROOT/frontend"
    if [ ! -d "node_modules" ]; then
        echo -e "${BLUE}Installing npm dependencies...${NC}"
        npm install
    fi
    npm run build
fi

# Function to cleanup on exit
cleanup() {
    echo -e "\n${BLUE}Shutting down...${NC}"
    jobs -p | xargs -r kill 2>/dev/null
    wait 2>/dev/null
    echo -e "${GREEN}Stopped.${NC}"
    exit 0
}

trap cleanup EXIT INT TERM

# Start Genie.jl backend
echo -e "${GREEN}Starting Genie.jl backend...${NC}"
cd "$PROJECT_ROOT/backend"
julia --project=. src/App.jl &
BACKEND_PID=$!

# Wait for backend to start
echo "Waiting for backend..."
sleep 5

if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}Backend failed to start!${NC}"
    exit 1
fi

echo -e "${GREEN}QCI Fab UI is running!${NC}"
echo -e "${BLUE}  http://localhost:8000${NC}"
echo ""
echo "Press Ctrl+C to stop..."

wait
