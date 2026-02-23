#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# ///

"""PostToolUse hook: log all tool executions to session log."""

from utils.constants import get_session_id, log_event, parse_hook_input


def main() -> None:
    data = parse_hook_input()
    session_id = data.get("session_id", get_session_id())

    log_event(session_id, "tool_use.jsonl", {
        "event": "PostToolUse",
        "tool_name": data.get("tool_name", ""),
        "tool_input": data.get("tool_input", {}),
    })


if __name__ == "__main__":
    main()
