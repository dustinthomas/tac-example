#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic"]
# ///

"""
ADW Build Phase - Implement plan, commit, push.

Requires a prior plan phase (state must have plan_file set).

Usage: uv run adw_build.py <adw-id>
"""

import sys
from dotenv import load_dotenv

from adw_modules.data_types import ADWPhase
from adw_modules.utils import setup_logger
from adw_modules.github import make_issue_comment
from adw_modules.workflow_ops import (
    check_error,
    format_issue_message,
    implement_plan,
    AGENT_IMPLEMENTOR,
)
from adw_modules.git_ops import git_commit
from adw_modules.state import load_state, advance_phase, mark_error


def main():
    """Build phase: checkout → implement → commit → push."""
    load_dotenv()

    if len(sys.argv) < 2:
        print("Usage: uv run adw_build.py <adw-id>")
        sys.exit(1)

    adw_id = sys.argv[1]

    logger = setup_logger(adw_id, "adw_build")
    logger.info(f"ADW Build Phase - ID: {adw_id}")

    # Load state from plan phase
    state = load_state(adw_id)
    if not state:
        logger.error(f"No state found for ADW ID: {adw_id}. Run plan phase first.")
        sys.exit(1)

    if not state.plan_file:
        logger.error("No plan file in state. Run plan phase first.")
        mark_error(state, "No plan file in state")
        sys.exit(1)

    issue_number = state.issue_number

    make_issue_comment(
        issue_number, format_issue_message(adw_id, "ops", "✅ Starting build phase")
    )

    # Implement
    logger.info(f"\n=== Implementing solution from {state.plan_file} ===")
    make_issue_comment(
        issue_number,
        format_issue_message(adw_id, AGENT_IMPLEMENTOR, "✅ Implementing solution"),
    )

    implement_response = implement_plan(state.plan_file, adw_id, logger)
    check_error(
        implement_response, issue_number, adw_id, AGENT_IMPLEMENTOR,
        "Error implementing solution", logger,
    )

    make_issue_comment(
        issue_number,
        format_issue_message(adw_id, AGENT_IMPLEMENTOR, "✅ Solution implemented"),
    )

    # Commit
    logger.info("\n=== Committing implementation ===")
    commit_msg, error = git_commit(AGENT_IMPLEMENTOR, adw_id, logger)
    check_error(
        error, issue_number, adw_id, AGENT_IMPLEMENTOR,
        "Error committing implementation", logger,
    )

    advance_phase(state, ADWPhase.TEST)

    logger.info(f"Build phase completed for issue #{issue_number}")
    make_issue_comment(
        issue_number,
        format_issue_message(adw_id, "ops", "✅ Build phase completed"),
    )


if __name__ == "__main__":
    main()
