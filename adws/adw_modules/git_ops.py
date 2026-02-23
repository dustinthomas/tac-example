"""Git operations module for ADW pipeline.

Provides functions for branch creation, committing, and pushing
via Claude Code slash commands.
"""

import logging
from typing import Optional, Tuple

from adw_modules.agent import execute_template
from adw_modules.data_types import (
    AgentPromptResponse,
    AgentTemplateRequest,
    GitHubIssue,
    IssueClassSlashCommand,
)

# Agent name constants
AGENT_BRANCH_GENERATOR = "branch_generator"
AGENT_PR_CREATOR = "pr_creator"


def git_branch(
    issue: GitHubIssue,
    issue_class: IssueClassSlashCommand,
    adw_id: str,
    logger: logging.Logger,
) -> Tuple[Optional[str], Optional[str]]:
    """Generate and create a git branch for the issue.
    Returns (branch_name, error_message) tuple."""
    issue_type = issue_class.replace("/", "")
    issue_description = f"{issue.title}: {issue.body}"

    request = AgentTemplateRequest(
        agent_name=AGENT_BRANCH_GENERATOR,
        slash_command="/generate_branch_name",
        args=[issue_type, issue_description],
        adw_id=adw_id,
        model="sonnet",
    )

    response = execute_template(request)

    if not response.success:
        return None, response.output

    branch_name = response.output.strip()
    logger.info(f"Created branch: {branch_name}")
    return branch_name, None


def git_commit(
    agent_name: str,
    adw_id: str,
    logger: logging.Logger,
) -> Tuple[Optional[str], Optional[str]]:
    """Create a git commit with a properly formatted message.
    Returns (commit_message, error_message) tuple."""
    unique_agent_name = f"{agent_name}_committer"

    request = AgentTemplateRequest(
        agent_name=unique_agent_name,
        slash_command="/commit",
        args=[],
        adw_id=adw_id,
        model="sonnet",
    )

    response = execute_template(request)

    if not response.success:
        return None, response.output

    commit_message = response.output.strip()
    logger.info(f"Created commit: {commit_message}")
    return commit_message, None


def pull_request(
    adw_id: str,
    logger: logging.Logger,
) -> Tuple[Optional[str], Optional[str]]:
    """Create a pull request for the implemented changes.
    Returns (pr_url, error_message) tuple."""
    request = AgentTemplateRequest(
        agent_name=AGENT_PR_CREATOR,
        slash_command="/pull_request",
        args=[],
        adw_id=adw_id,
        model="sonnet",
    )

    response = execute_template(request)

    if not response.success:
        return None, response.output

    pr_url = response.output.strip()
    logger.info(f"Created pull request: {pr_url}")
    return pr_url, None
