#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic"]
# ///

"""
ADW Full SDLC orchestrator: Plan → Build → Test → Review → Document.

After all phases complete, creates a pull request.

Usage: uv run adw_sdlc.py <github-issue-number> [adw-id]
"""

import sys
from dotenv import load_dotenv

from adw_modules.data_types import ADWWorkflow
from adw_modules.utils import make_adw_id, setup_logger
from adw_modules.github import make_issue_comment
from adw_modules.workflow_ops import check_error, format_issue_message
from adw_modules.git_ops import pull_request
from adw_modules.state import create_state, load_state, save_state
from adw_modules.orchestrator import run_pipeline

PHASES = [
    "adw_plan.py",
    "adw_build.py",
    "adw_test.py",
    "adw_review.py",
    "adw_document.py",
]


def main():
    load_dotenv()

    if len(sys.argv) < 2:
        print("Usage: uv run adw_sdlc.py <issue-number> [adw-id]")
        sys.exit(1)

    issue_number = sys.argv[1]
    adw_id = sys.argv[2] if len(sys.argv) > 2 else make_adw_id()

    logger = setup_logger(adw_id, "adw_sdlc")
    logger.info(f"ADW Full SDLC — ID: {adw_id}")

    # Pre-create state with SDLC workflow type so phases inherit it
    create_state(adw_id, issue_number, ADWWorkflow.SDLC)

    # Run all phases
    run_pipeline(PHASES, issue_number, adw_id)

    # Create PR after all phases succeed
    logger.info("\n=== Creating pull request ===")
    make_issue_comment(
        issue_number, format_issue_message(adw_id, "ops", "✅ Creating pull request")
    )

    pr_url, error = pull_request(adw_id, logger)
    check_error(error, issue_number, adw_id, "ops", "Error creating PR", logger)

    # Update state with PR URL
    state = load_state(adw_id)
    if state:
        state.pr_url = pr_url
        save_state(state)

    logger.info(f"Full SDLC completed. PR: {pr_url}")
    make_issue_comment(
        issue_number,
        format_issue_message(adw_id, "ops", f"✅ SDLC complete — PR: {pr_url}"),
    )


if __name__ == "__main__":
    main()
