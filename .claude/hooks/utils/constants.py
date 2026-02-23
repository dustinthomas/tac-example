"""Shared constants and helpers for Claude Code hooks."""

import os
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Session logs go to <project_root>/logs/<session_id>/
PROJECT_ROOT = Path(__file__).resolve().parents[3]
LOG_BASE_DIR = PROJECT_ROOT / "logs"


def get_session_id() -> str:
    """Extract session_id from hook input data (already parsed) or env."""
    return os.environ.get("CLAUDE_SESSION_ID", "unknown")


def parse_hook_input() -> dict:
    """Read and parse JSON from stdin. Returns empty dict on failure."""
    try:
        raw = sys.stdin.read()
        if raw.strip():
            return json.loads(raw)
    except (json.JSONDecodeError, OSError):
        pass
    return {}


def ensure_session_log_dir(session_id: str) -> Path:
    """Create and return the session log directory."""
    log_dir = LOG_BASE_DIR / session_id
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def log_event(session_id: str, filename: str, data: dict) -> None:
    """Append a JSON line to a log file in the session directory."""
    log_dir = ensure_session_log_dir(session_id)
    log_path = log_dir / filename
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **data,
    }
    with open(log_path, "a") as f:
        f.write(json.dumps(entry) + "\n")
