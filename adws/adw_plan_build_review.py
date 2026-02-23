#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic"]
# ///

"""
ADW Plan → Build → Review orchestrator.

Usage: uv run adw_plan_build_review.py <github-issue-number> [adw-id]
"""

import sys
from dotenv import load_dotenv
from adw_modules.utils import make_adw_id
from adw_modules.orchestrator import run_pipeline

PHASES = ["adw_plan.py", "adw_build.py", "adw_review.py"]


def main():
    load_dotenv()

    if len(sys.argv) < 2:
        print("Usage: uv run adw_plan_build_review.py <issue-number> [adw-id]")
        sys.exit(1)

    issue_number = sys.argv[1]
    adw_id = sys.argv[2] if len(sys.argv) > 2 else make_adw_id()

    print(f"ADW Plan → Build → Review — ID: {adw_id}")
    run_pipeline(PHASES, issue_number, adw_id)


if __name__ == "__main__":
    main()
