#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic"]
# ///

"""
ADW Patch Workflow - Targeted patch for existing issues/PRs.

Triggered by 'adw_patch' keyword in issue comments.
Creates a minimal patch plan, implements it, and creates a PR.

Usage: uv run adw_patch.py <github-issue-number> [adw-id]
"""

import sys
from dotenv import load_dotenv

from adw_modules.data_types import ADWPhase, ADWWorkflow, AgentTemplateRequest
from adw_modules.utils import make_adw_id, setup_logger
from adw_modules.github import extract_repo_path, fetch_issue, get_repo_url, make_issue_comment
from adw_modules.workflow_ops import (
    check_error,
    format_issue_message,
    implement_plan,
    AGENT_IMPLEMENTOR,
)
from adw_modules.git_ops import git_branch, git_commit, pull_request
from adw_modules.agent import execute_template
from adw_modules.state import create_state, advance_phase, save_state

AGENT_PATCHER = "sdlc_patcher"


def main():
    """Patch workflow: classify → branch → patch plan → implement → commit → PR."""
    load_dotenv()

    if len(sys.argv) < 2:
        print("Usage: uv run adw_patch.py <issue-number> [adw-id]")
        sys.exit(1)

    issue_number = sys.argv[1]
    adw_id = sys.argv[2] if len(sys.argv) > 2 else make_adw_id()

    logger = setup_logger(adw_id, "adw_patch")
    logger.info(f"ADW Patch Workflow - ID: {adw_id}")

    state = create_state(adw_id, issue_number, ADWWorkflow.PATCH)

    try:
        github_repo_url = get_repo_url()
        repo_path = extract_repo_path(github_repo_url)
    except ValueError as e:
        logger.error(f"Error getting repository URL: {e}")
        sys.exit(1)

    issue = fetch_issue(issue_number, repo_path)

    make_issue_comment(
        issue_number, format_issue_message(adw_id, "ops", "✅ Starting patch workflow")
    )

    # Create branch (always bugfix for patches)
    branch_name, error = git_branch(issue, "/bug", adw_id, logger)
    check_error(error, issue_number, adw_id, "ops", "Error creating branch", logger)

    state.branch_name = branch_name
    state.issue_class = "/bug"
    advance_phase(state, ADWPhase.PLAN)

    # Generate patch plan via /patch command
    logger.info("\n=== Generating patch plan ===")
    request = AgentTemplateRequest(
        agent_name=AGENT_PATCHER,
        slash_command="/patch",
        args=[f"{issue.title}: {issue.body}"],
        adw_id=adw_id,
        model="opus",
    )

    response = execute_template(request)
    check_error(response, issue_number, adw_id, AGENT_PATCHER, "Error creating patch plan", logger)

    # The patch plan output IS the plan — use it directly for implementation
    state.plan_file = f"patch plan from issue #{issue_number}"
    advance_phase(state, ADWPhase.BUILD)

    make_issue_comment(
        issue_number,
        format_issue_message(adw_id, AGENT_PATCHER, "✅ Patch plan created"),
    )

    # Commit patch plan (if /patch created files)
    commit_msg, error = git_commit(AGENT_PATCHER, adw_id, logger)
    # Don't fail if nothing to commit
    if error:
        logger.info(f"No patch plan files to commit (expected): {error}")

    # Implement
    logger.info("\n=== Implementing patch ===")
    implement_response = implement_plan(
        f"Implement the patch for issue #{issue_number}: {issue.title}\n{issue.body}",
        adw_id,
        logger,
    )
    check_error(
        implement_response, issue_number, adw_id, AGENT_IMPLEMENTOR,
        "Error implementing patch", logger,
    )

    # Commit implementation
    commit_msg, error = git_commit(AGENT_IMPLEMENTOR, adw_id, logger)
    check_error(error, issue_number, adw_id, AGENT_IMPLEMENTOR, "Error committing patch", logger)

    advance_phase(state, ADWPhase.PR)

    # Create PR
    logger.info("\n=== Creating pull request ===")
    pr_url, error = pull_request(adw_id, logger)
    check_error(error, issue_number, adw_id, "ops", "Error creating PR", logger)

    state.pr_url = pr_url
    save_state(state)

    logger.info(f"Patch workflow completed. PR: {pr_url}")
    make_issue_comment(
        issue_number,
        format_issue_message(adw_id, "ops", f"✅ Patch PR created: {pr_url}"),
    )


if __name__ == "__main__":
    main()
