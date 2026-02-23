#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# ///

"""UserPromptSubmit hook: log user prompts to session log."""

from utils.constants import get_session_id, log_event, parse_hook_input


def main() -> None:
    data = parse_hook_input()
    session_id = data.get("session_id", get_session_id())

    log_event(session_id, "events.jsonl", {
        "event": "UserPromptSubmit",
        "prompt": data.get("prompt", ""),
    })


if __name__ == "__main__":
    main()
