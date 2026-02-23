#!/usr/bin/env bash
# Stop backend server and any ADW webhook/cron processes.
#
# Usage: bash scripts/stop_apps.sh

set -euo pipefail

echo "Stopping applications..."

# Kill Julia/Genie backend server
if pgrep -f "julia.*App.jl" > /dev/null 2>&1; then
    echo "Stopping Julia backend..."
    pkill -f "julia.*App.jl" || true
    echo "Julia backend stopped."
else
    echo "No Julia backend running."
fi

# Kill ADW webhook server (uvicorn/trigger_webhook)
if pgrep -f "trigger_webhook" > /dev/null 2>&1; then
    echo "Stopping webhook server..."
    pkill -f "trigger_webhook" || true
    echo "Webhook server stopped."
else
    echo "No webhook server running."
fi

# Kill ADW cron poller
if pgrep -f "trigger_cron" > /dev/null 2>&1; then
    echo "Stopping cron poller..."
    pkill -f "trigger_cron" || true
    echo "Cron poller stopped."
else
    echo "No cron poller running."
fi

echo "All applications stopped."
