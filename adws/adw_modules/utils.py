"""Utility functions for ADW system."""

import json
import logging
import os
import re
import sys
import uuid
from datetime import datetime
from typing import Any, Optional


def make_adw_id() -> str:
    """Generate a short 8-character UUID for ADW tracking."""
    return str(uuid.uuid4())[:8]


def setup_logger(adw_id: str, trigger_type: str = "adw_plan_build") -> logging.Logger:
    """Set up logger that writes to both console and file using adw_id.

    Args:
        adw_id: The ADW workflow ID
        trigger_type: Type of trigger (adw_plan_build, trigger_webhook, etc.)

    Returns:
        Configured logger instance
    """
    # Create log directory: agents/{adw_id}/adw_plan_build/
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    log_dir = os.path.join(project_root, "agents", adw_id, trigger_type)
    os.makedirs(log_dir, exist_ok=True)

    # Log file path: agents/{adw_id}/adw_plan_build/execution.log
    log_file = os.path.join(log_dir, "execution.log")

    # Create logger with unique name using adw_id
    logger = logging.getLogger(f"adw_{adw_id}")
    logger.setLevel(logging.DEBUG)

    # Clear any existing handlers to avoid duplicates
    logger.handlers.clear()

    # File handler - captures everything
    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setLevel(logging.DEBUG)

    # Console handler - INFO and above
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # Format with timestamp for file
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Simpler format for console
    console_formatter = logging.Formatter('%(message)s')

    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Log initial setup message
    logger.info(f"ADW Logger initialized - ID: {adw_id}")
    logger.debug(f"Log file: {log_file}")

    return logger


def get_logger(adw_id: str) -> logging.Logger:
    """Get existing logger by ADW ID."""
    return logging.getLogger(f"adw_{adw_id}")


def get_project_root() -> str:
    """Get the project root directory (two levels up from adw_modules/)."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_safe_subprocess_env() -> dict:
    """Get a safe environment dict for subprocess calls.

    Strips CLAUDECODE to allow nested Claude Code execution,
    and ensures HOME is passed for OAuth token access.
    """
    env = os.environ.copy()
    env.pop("CLAUDECODE", None)
    return env


def parse_json(text: str) -> Optional[Any]:
    """Parse JSON from text, unwrapping markdown code fences if present.

    Handles common LLM output patterns:
    - Raw JSON
    - ```json ... ```
    - ``` ... ```
    """
    stripped = text.strip()

    # Try raw JSON first
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass

    # Try unwrapping markdown code fences
    fence_pattern = re.compile(r"```(?:json)?\s*\n?(.*?)\n?\s*```", re.DOTALL)
    match = fence_pattern.search(stripped)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    return None
