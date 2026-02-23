#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic"]
# ///

"""
ADW Plan & Build - AI Developer Workflow (ADW)

Orchestrator that runs plan then build phases sequentially.

Usage: uv run adw_plan_build.py <github-issue-number> [adw-id]
"""

import sys
import os
from typing import Tuple, Optional
from dotenv import load_dotenv

from adw_modules.data_types import ADWWorkflow
from adw_modules.utils import make_adw_id, setup_logger
from adw_modules.agent import download_issue_images
from adw_modules.github import extract_repo_path, fetch_issue, get_repo_url, make_issue_comment
from adw_modules.workflow_ops import (
    build_plan,
    check_error,
    classify_issue,
    format_issue_message,
    get_plan_file,
    implement_plan,
    AGENT_PLANNER,
    AGENT_IMPLEMENTOR,
)
from adw_modules.git_ops import git_branch, git_commit, pull_request
from adw_modules.state import create_state, advance_phase, mark_error, save_state
from adw_modules.data_types import ADWPhase


def check_env_vars(logger=None) -> None:
    """Check that all required environment variables are set."""
    required_vars: list[str] = []
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        error_msg = "Error: Missing required environment variables:"
        if logger:
            logger.error(error_msg)
            for var in missing_vars:
                logger.error(f"  - {var}")
        else:
            print(error_msg, file=sys.stderr)
            for var in missing_vars:
                print(f"  - {var}", file=sys.stderr)
        sys.exit(1)


def parse_args(logger=None) -> Tuple[str, Optional[str]]:
    """Parse command line arguments."""
    if len(sys.argv) < 2:
        usage_msg = [
            "Usage: uv run adw_plan_build.py <issue-number> [adw-id]",
            "Example: uv run adw_plan_build.py 123",
            "Example: uv run adw_plan_build.py 123 abc12345",
        ]
        if logger:
            for msg in usage_msg:
                logger.error(msg)
        else:
            for msg in usage_msg:
                print(msg)
        sys.exit(1)

    issue_number = sys.argv[1]
    adw_id = sys.argv[2] if len(sys.argv) > 2 else None

    return issue_number, adw_id


def main():
    """Main entry point."""
    load_dotenv()

    issue_number, adw_id = parse_args()

    if not adw_id:
        adw_id = make_adw_id()

    logger = setup_logger(adw_id, "adw_plan_build")
    logger.info(f"ADW ID: {adw_id}")

    check_env_vars(logger)

    # Initialize state
    state = create_state(adw_id, issue_number, ADWWorkflow.PLAN_BUILD)

    try:
        github_repo_url: str = get_repo_url()
        repo_path: str = extract_repo_path(github_repo_url)
    except ValueError as e:
        logger.error(f"Error getting repository URL: {e}")
        mark_error(state, str(e))
        sys.exit(1)

    issue = fetch_issue(issue_number, repo_path)

    logger.debug(f"issue: {issue.model_dump_json(indent=2, by_alias=True)}")
    make_issue_comment(
        issue_number, format_issue_message(adw_id, "ops", "✅ Starting ADW workflow")
    )

    # Classify the issue
    issue_command, error = classify_issue(issue, adw_id, logger)
    check_error(error, issue_number, adw_id, "ops", "Error classifying issue", logger)

    state.issue_class = issue_command
    advance_phase(state, ADWPhase.BRANCH)

    logger.info(f"issue_command: {issue_command}")
    make_issue_comment(
        issue_number,
        format_issue_message(adw_id, "ops", f"✅ Issue classified as: {issue_command}"),
    )

    # Create git branch
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

    # Build the implementation plan
    logger.info("\n=== Building implementation plan ===")
    make_issue_comment(
        issue_number,
        format_issue_message(adw_id, AGENT_PLANNER, "✅ Building implementation plan"),
    )

    issue_plan_response = build_plan(issue, issue_command, adw_id, logger, image_paths=image_paths)
    check_error(
        issue_plan_response, issue_number, adw_id, AGENT_PLANNER, "Error building plan", logger,
    )

    logger.debug(f"issue_plan_response.output: {issue_plan_response.output}")
    make_issue_comment(
        issue_number,
        format_issue_message(adw_id, AGENT_PLANNER, "✅ Implementation plan created"),
    )

    # Get the path to the plan file
    logger.info("\n=== Finding plan file ===")
    plan_file_path, error = get_plan_file(issue_plan_response.output, adw_id, logger)
    check_error(error, issue_number, adw_id, "ops", "Error finding plan file", logger)

    state.plan_file = plan_file_path
    save_state(state)

    logger.info(f"plan_file_path: {plan_file_path}")
    make_issue_comment(
        issue_number,
        format_issue_message(adw_id, "ops", f"✅ Plan file created: {plan_file_path}"),
    )

    # Commit the plan
    logger.info("\n=== Committing plan ===")
    make_issue_comment(
        issue_number, format_issue_message(adw_id, AGENT_PLANNER, "✅ Committing plan")
    )
    commit_msg, error = git_commit(AGENT_PLANNER, adw_id, logger)
    check_error(error, issue_number, adw_id, AGENT_PLANNER, "Error committing plan", logger)

    advance_phase(state, ADWPhase.BUILD)

    # Implement the plan
    logger.info("\n=== Implementing solution ===")
    make_issue_comment(
        issue_number,
        format_issue_message(adw_id, AGENT_IMPLEMENTOR, "✅ Implementing solution"),
    )
    implement_response = implement_plan(plan_file_path, adw_id, logger)
    check_error(
        implement_response, issue_number, adw_id, AGENT_IMPLEMENTOR, "Error implementing solution", logger,
    )

    logger.debug(f"implement_response.output: {implement_response.output}")
    make_issue_comment(
        issue_number,
        format_issue_message(adw_id, AGENT_IMPLEMENTOR, "✅ Solution implemented"),
    )

    # Commit the implementation
    logger.info("\n=== Committing implementation ===")
    make_issue_comment(
        issue_number,
        format_issue_message(adw_id, AGENT_IMPLEMENTOR, "✅ Committing implementation"),
    )
    commit_msg, error = git_commit(AGENT_IMPLEMENTOR, adw_id, logger)
    check_error(
        error, issue_number, adw_id, AGENT_IMPLEMENTOR, "Error committing implementation", logger,
    )

    advance_phase(state, ADWPhase.PR)

    # Create pull request
    logger.info("\n=== Creating pull request ===")
    make_issue_comment(
        issue_number, format_issue_message(adw_id, "ops", "✅ Creating pull request")
    )

    pr_url, error = pull_request(adw_id, logger)
    check_error(error, issue_number, adw_id, "ops", "Error creating pull request", logger)

    state.pr_url = pr_url
    advance_phase(state, ADWPhase.PR)

    logger.info(f"\nPull request created: {pr_url}")
    make_issue_comment(
        issue_number,
        format_issue_message(adw_id, "ops", f"✅ Pull request created: {pr_url}"),
    )

    logger.info(f"ADW workflow completed successfully for issue #{issue_number}")
    make_issue_comment(
        issue_number,
        format_issue_message(adw_id, "ops", "✅ ADW workflow completed successfully"),
    )


if __name__ == "__main__":
    main()
