#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# ///

"""PreToolUse hook: safety guardrails + event logging.

Blocks:
- Dangerous rm commands (rm -rf /, rm -rf ~, rm -rf .)
- Direct .env file access (read, write, edit)

Logs all PreToolUse events to session log.
"""

import json
import re
import sys

from utils.constants import get_session_id, log_event, parse_hook_input

# Patterns that should never be executed
DANGEROUS_RM_PATTERNS = [
    r"rm\s+.*-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]*\s+/\s*$",  # rm -rf /
    r"rm\s+.*-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]*\s+~",        # rm -rf ~
    r"rm\s+.*-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]*\s+\.\s*$",   # rm -rf .
    r"rm\s+.*-[a-zA-Z]*f[a-zA-Z]*r[a-zA-Z]*\s+/\s*$",    # rm -fr /
    r"rm\s+.*-[a-zA-Z]*f[a-zA-Z]*r[a-zA-Z]*\s+~",        # rm -fr ~
    r"rm\s+.*-[a-zA-Z]*f[a-zA-Z]*r[a-zA-Z]*\s+\.\s*$",   # rm -fr .
]

# Files that hooks should never allow access to
ENV_FILE_PATTERN = r"(^|/)\.env($|\.local$|\.production$|\.staging$)"


def check_dangerous_bash(command: str) -> str | None:
    """Return a reason string if the command is dangerous, else None."""
    for pattern in DANGEROUS_RM_PATTERNS:
        if re.search(pattern, command):
            return f"Blocked: destructive rm command: {command}"
    return None


def check_env_file_access(tool_name: str, tool_input: dict) -> str | None:
    """Return a reason string if the tool accesses .env files, else None."""
    file_path = ""
    if tool_name in ("Read", "Write", "Edit"):
        file_path = tool_input.get("file_path", "")
    elif tool_name == "Bash":
        cmd = tool_input.get("command", "")
        # Check if .env appears in bash commands (cat .env, vim .env, etc.)
        if re.search(ENV_FILE_PATTERN, cmd):
            return f"Blocked: .env file access in command: {cmd}"
        return None

    if file_path and re.search(ENV_FILE_PATTERN, file_path):
        return f"Blocked: direct .env file access: {file_path}"
    return None


def main() -> None:
    data = parse_hook_input()
    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})
    session_id = data.get("session_id", get_session_id())

    # Log the event
    log_event(session_id, "pre_tool_use.jsonl", {
        "event": "PreToolUse",
        "tool_name": tool_name,
        "tool_input": tool_input,
    })

    # Safety checks
    reason = None

    if tool_name == "Bash":
        command = tool_input.get("command", "")
        reason = check_dangerous_bash(command)
        if not reason:
            reason = check_env_file_access(tool_name, tool_input)
    elif tool_name in ("Read", "Write", "Edit"):
        reason = check_env_file_access(tool_name, tool_input)

    if reason:
        # Exit 2 = blocking error, stderr is fed back to Claude
        print(reason, file=sys.stderr)
        sys.exit(2)

    # Allow the tool to proceed (exit 0, no output needed)


if __name__ == "__main__":
    main()
