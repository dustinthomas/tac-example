#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic"]
# ///

"""
ADW Plan Phase - Classify issue, create branch, generate plan, commit.

Usage: uv run adw_plan.py <github-issue-number> [adw-id]
"""

import sys
import os
from dotenv import load_dotenv

from adw_modules.data_types import ADWPhase, ADWWorkflow
from adw_modules.utils import make_adw_id, setup_logger
from adw_modules.agent import download_issue_images
from adw_modules.github import extract_repo_path, fetch_issue, get_repo_url, make_issue_comment
from adw_modules.workflow_ops import (
    build_plan,
    check_error,
    classify_issue,
    format_issue_message,
    get_plan_file,
    AGENT_PLANNER,
)
from adw_modules.git_ops import git_branch, git_commit
from adw_modules.state import create_state, load_state, advance_phase, save_state


def main():
    """Plan phase: classify → branch → plan → commit → push."""
    load_dotenv()

    if len(sys.argv) < 2:
        print("Usage: uv run adw_plan.py <issue-number> [adw-id]")
        sys.exit(1)

    issue_number = sys.argv[1]
    adw_id = sys.argv[2] if len(sys.argv) > 2 else make_adw_id()

    logger = setup_logger(adw_id, "adw_plan")
    logger.info(f"ADW Plan Phase - ID: {adw_id}")

    # Load or create state
    state = load_state(adw_id)
    if not state:
        state = create_state(adw_id, issue_number, ADWWorkflow.PLAN_BUILD)

    try:
        github_repo_url = get_repo_url()
        repo_path = extract_repo_path(github_repo_url)
    except ValueError as e:
        logger.error(f"Error getting repository URL: {e}")
        sys.exit(1)

    issue = fetch_issue(issue_number, repo_path)

    make_issue_comment(
        issue_number, format_issue_message(adw_id, "ops", "✅ Starting plan phase")
    )

    # Classify
    issue_command, error = classify_issue(issue, adw_id, logger)
    check_error(error, issue_number, adw_id, "ops", "Error classifying issue", logger)

    state.issue_class = issue_command
    advance_phase(state, ADWPhase.BRANCH)

    logger.info(f"Issue classified as: {issue_command}")
    make_issue_comment(
        issue_number,
        format_issue_message(adw_id, "ops", f"✅ Issue classified as: {issue_command}"),
    )

    # Branch
    branch_name, error = git_branch(issue, issue_command, adw_id, logger)
    check_error(error, issue_number, adw_id, "ops", "Error creating branch", logger)

    state.branch_name = branch_name
    advance_phase(state, ADWPhase.PLAN)

    logger.info(f"Working on branch: {branch_name}")
    make_issue_comment(
        issue_number,
        format_issue_message(adw_id, "ops", f"✅ Working on branch: {branch_name}"),
    )

    # Download issue images
    image_urls = issue.extract_image_urls()
    image_paths = []
    if image_urls:
        logger.info(f"Found {len(image_urls)} images in issue, downloading...")
        image_paths = download_issue_images(image_urls, adw_id)
        logger.info(f"Downloaded {len(image_paths)} images")

    # Plan
    logger.info("\n=== Building implementation plan ===")
    make_issue_comment(
        issue_number,
        format_issue_message(adw_id, AGENT_PLANNER, "✅ Building implementation plan"),
    )

    plan_response = build_plan(issue, issue_command, adw_id, logger, image_paths=image_paths)
    check_error(plan_response, issue_number, adw_id, AGENT_PLANNER, "Error building plan", logger)

    make_issue_comment(
        issue_number,
        format_issue_message(adw_id, AGENT_PLANNER, "✅ Implementation plan created"),
    )

    # Find plan file
    plan_file_path, error = get_plan_file(plan_response.output, adw_id, logger)
    check_error(error, issue_number, adw_id, "ops", "Error finding plan file", logger)

    state.plan_file = plan_file_path
    save_state(state)

    logger.info(f"Plan file: {plan_file_path}")
    make_issue_comment(
        issue_number,
        format_issue_message(adw_id, "ops", f"✅ Plan file created: {plan_file_path}"),
    )

    # Commit plan
    logger.info("\n=== Committing plan ===")
    commit_msg, error = git_commit(AGENT_PLANNER, adw_id, logger)
    check_error(error, issue_number, adw_id, AGENT_PLANNER, "Error committing plan", logger)

    # Mark plan phase complete, ready for build
    advance_phase(state, ADWPhase.BUILD)

    logger.info(f"Plan phase completed for issue #{issue_number}")
    make_issue_comment(
        issue_number,
        format_issue_message(adw_id, "ops", "✅ Plan phase completed"),
    )


if __name__ == "__main__":
    main()
