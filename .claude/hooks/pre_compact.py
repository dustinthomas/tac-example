#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# ///

"""PreCompact hook: log context compaction events."""

from utils.constants import get_session_id, log_event, parse_hook_input


def main() -> None:
    data = parse_hook_input()
    session_id = data.get("session_id", get_session_id())

    log_event(session_id, "events.jsonl", {
        "event": "PreCompact",
    })


if __name__ == "__main__":
    main()
