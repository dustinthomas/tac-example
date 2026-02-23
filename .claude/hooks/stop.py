#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# ///

"""Stop hook: log stop events and archive transcript.

Copies the session transcript to the session log directory as chat.jsonl
for post-session analysis.
"""

import shutil
from pathlib import Path

from utils.constants import ensure_session_log_dir, get_session_id, log_event, parse_hook_input


def main() -> None:
    data = parse_hook_input()
    session_id = data.get("session_id", get_session_id())

    log_event(session_id, "events.jsonl", {
        "event": "Stop",
    })

    # Copy transcript to session log dir if available
    transcript_path = data.get("transcript_path", "")
    if transcript_path:
        src = Path(transcript_path)
        if src.exists():
            log_dir = ensure_session_log_dir(session_id)
            dest = log_dir / "chat.jsonl"
            shutil.copy2(str(src), str(dest))


if __name__ == "__main__":
    main()
