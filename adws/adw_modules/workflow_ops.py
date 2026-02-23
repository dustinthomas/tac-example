"""Shared workflow operations for ADW pipeline.

Contains operations used across multiple phase scripts:
classify, plan, implement, and error handling.
"""

import glob
import logging
import os
import subprocess
import sys
from typing import List, Optional, Tuple, Union

from adw_modules.agent import execute_template
from adw_modules.utils import get_safe_subprocess_env
from adw_modules.data_types import (
    AgentPromptResponse,
    AgentTemplateRequest,
    GitHubIssue,
    IssueClassSlashCommand,
)
from adw_modules.github import make_issue_comment

# Agent name constants
AGENT_PLANNER = "sdlc_planner"
AGENT_IMPLEMENTOR = "sdlc_implementor"
AGENT_CLASSIFIER = "issue_classifier"
AGENT_PLAN_FINDER = "plan_finder"


def format_issue_message(
    adw_id: str, agent_name: str, message: str, session_id: Optional[str] = None
) -> str:
    """Format a message for issue comments with ADW tracking."""
    if session_id:
        return f"{adw_id}_{agent_name}_{session_id}: {message}"
    return f"{adw_id}_{agent_name}: {message}"


def check_error(
    error_or_response: Union[Optional[str], AgentPromptResponse],
    issue_number: str,
    adw_id: str,
    agent_name: str,
    error_prefix: str,
    logger: logging.Logger,
) -> None:
    """Check for errors and handle them uniformly.

    Posts error to GitHub issue and exits with code 1 on failure.
    """
    error = None

    if isinstance(error_or_response, AgentPromptResponse):
        if not error_or_response.success:
            error = error_or_response.output
    else:
        error = error_or_response

    if error:
        logger.error(f"{error_prefix}: {error}")
        make_issue_comment(
            issue_number,
            format_issue_message(adw_id, agent_name, f"❌ {error_prefix}: {error}"),
        )
        sys.exit(1)


def classify_issue(
    issue: GitHubIssue, adw_id: str, logger: logging.Logger
) -> Tuple[Optional[IssueClassSlashCommand], Optional[str]]:
    """Classify GitHub issue and return appropriate slash command.
    Returns (command, error_message) tuple."""
    issue_template_request = AgentTemplateRequest(
        agent_name=AGENT_CLASSIFIER,
        slash_command="/classify_issue",
        args=[issue.model_dump_json(indent=2, by_alias=True)],
        adw_id=adw_id,
        model="sonnet",
    )

    logger.debug(
        f"issue_template_request: {issue_template_request.model_dump_json(indent=2, by_alias=True)}"
    )

    issue_response = execute_template(issue_template_request)

    logger.debug(
        f"issue_response: {issue_response.model_dump_json(indent=2, by_alias=True)}"
    )

    if not issue_response.success:
        return None, issue_response.output

    issue_command = issue_response.output.strip().strip("`")

    if issue_command == "0":
        return None, f"No command selected: {issue_response.output}"

    valid_commands = ["/chore", "/bug", "/feature"]

    if issue_command in valid_commands:
        return issue_command, None  # type: ignore

    raw = issue_response.output.lower()
    for cmd in valid_commands:
        if cmd in raw or cmd.lstrip("/") in raw:
            logger.warning(
                f"Classifier returned verbose output, extracted '{cmd}' from: "
                f"{issue_response.output[:120]}"
            )
            return cmd, None  # type: ignore

    return None, f"Invalid command selected: {issue_response.output}"


def build_plan(
    issue: GitHubIssue,
    command: str,
    adw_id: str,
    logger: logging.Logger,
    image_paths: Optional[List[str]] = None,
) -> AgentPromptResponse:
    """Build implementation plan for the issue using the specified command."""
    issue_plan_template_request = AgentTemplateRequest(
        agent_name=AGENT_PLANNER,
        slash_command=command,
        args=[issue.title + ": " + issue.body],
        adw_id=adw_id,
        image_paths=image_paths or [],
        model="sonnet",
    )

    logger.debug(
        f"issue_plan_template_request: {issue_plan_template_request.model_dump_json(indent=2, by_alias=True)}"
    )

    issue_plan_response = execute_template(issue_plan_template_request)

    logger.debug(
        f"issue_plan_response: {issue_plan_response.model_dump_json(indent=2, by_alias=True)}"
    )

    return issue_plan_response


def get_plan_file(
    plan_output: str, adw_id: str, logger: logging.Logger
) -> Tuple[Optional[str], Optional[str]]:
    """Get the path to the plan file that was just created.
    Returns (file_path, error_message) tuple."""
    request = AgentTemplateRequest(
        agent_name=AGENT_PLAN_FINDER,
        slash_command="/find_plan_file",
        args=[plan_output],
        adw_id=adw_id,
        model="sonnet",
    )

    response = execute_template(request)

    if not response.success:
        return None, response.output

    file_path = response.output.strip()

    if file_path and file_path != "0" and "/" in file_path:
        return file_path, None
    elif file_path == "0":
        return None, "No plan file found in output"
    else:
        return None, f"Invalid file path response: {file_path}"


def implement_plan(
    plan_file: str, adw_id: str, logger: logging.Logger
) -> AgentPromptResponse:
    """Implement the plan using the /implement command."""
    implement_template_request = AgentTemplateRequest(
        agent_name=AGENT_IMPLEMENTOR,
        slash_command="/implement",
        args=[plan_file],
        adw_id=adw_id,
        model="sonnet",
    )

    logger.debug(
        f"implement_template_request: {implement_template_request.model_dump_json(indent=2, by_alias=True)}"
    )

    implement_response = execute_template(implement_template_request)

    logger.debug(
        f"implement_response: {implement_response.model_dump_json(indent=2, by_alias=True)}"
    )

    return implement_response


def run_e2e_screenshots(logger: logging.Logger) -> List[str]:
    """Run Playwright e2e tests and collect screenshot paths.

    Returns list of .png file paths from test-results/.
    Returns empty list on failure (e2e failures should not block the review).
    """
    frontend_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
    frontend_dir = os.path.normpath(frontend_dir)
    results_dir = os.path.join(frontend_dir, "test-results")

    # Clean previous results
    if os.path.isdir(results_dir):
        for old_png in glob.glob(os.path.join(results_dir, "**", "*.png"), recursive=True):
            os.remove(old_png)

    logger.info("Running Playwright e2e tests for screenshots...")
    try:
        subprocess.run(
            ["npx", "playwright", "test", "--reporter=list"],
            cwd=frontend_dir,
            env=get_safe_subprocess_env(),
            timeout=300,
            capture_output=True,
            text=True,
        )
    except subprocess.TimeoutExpired:
        logger.warning("Playwright timed out after 300s")
    except Exception as e:
        logger.warning(f"Playwright execution failed: {e}")

    # Collect screenshots regardless of test exit code
    screenshots = sorted(glob.glob(os.path.join(results_dir, "**", "*.png"), recursive=True))
    logger.info(f"Collected {len(screenshots)} screenshot(s) from e2e tests")
    return screenshots
