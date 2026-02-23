#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic"]
# ///

"""
ADW Plan → Build → Test orchestrator.

Usage: uv run adw_plan_build_test.py <github-issue-number> [adw-id]
"""

import sys
from dotenv import load_dotenv
from adw_modules.utils import make_adw_id
from adw_modules.orchestrator import run_pipeline

PHASES = ["adw_plan.py", "adw_build.py", "adw_test.py"]


def main():
    load_dotenv()

    if len(sys.argv) < 2:
        print("Usage: uv run adw_plan_build_test.py <issue-number> [adw-id]")
        sys.exit(1)

    issue_number = sys.argv[1]
    adw_id = sys.argv[2] if len(sys.argv) > 2 else make_adw_id()

    print(f"ADW Plan → Build → Test — ID: {adw_id}")
    run_pipeline(PHASES, issue_number, adw_id)


if __name__ == "__main__":
    main()
