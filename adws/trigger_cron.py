#!/usr/bin/env uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "schedule",
#     "python-dotenv",
#     "pydantic",
# ]
# ///

"""
Cron-based ADW trigger system that monitors GitHub issues and automatically processes them.

This script polls GitHub every 20 seconds to detect:
1. New issues without comments → triggers adw_plan_build
2. Issues where the latest comment contains an ADW keyword → routes to appropriate workflow

Supported keywords: adw, adw_sdlc, adw_patch, adw_plan_build_test, etc.
"""

import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Set, Optional

import schedule
from dotenv import load_dotenv

from github import fetch_open_issues, fetch_issue_comments, get_repo_url, extract_repo_path

# Load environment variables from current or parent directories
load_dotenv()

# Optional environment variables
GITHUB_PAT = os.getenv("GITHUB_PAT")

# Workflow keyword → script mapping
WORKFLOW_SCRIPTS = {
    "adw": "adw_plan_build.py",
    "adw_plan_build": "adw_plan_build.py",
    "adw_sdlc": "adw_sdlc.py",
    "adw_patch": "adw_patch.py",
    "adw_plan_build_test": "adw_plan_build_test.py",
    "adw_plan_build_review": "adw_plan_build_review.py",
    "adw_plan_build_test_review": "adw_plan_build_test_review.py",
}

# Get repository URL from git remote
try:
    GITHUB_REPO_URL = get_repo_url()
    REPO_PATH = extract_repo_path(GITHUB_REPO_URL)
except ValueError as e:
    print(f"ERROR: {e}")
    sys.exit(1)

# Track processed issues
processed_issues: Set[int] = set()
# Track issues with their last processed comment ID
issue_last_comment: Dict[int, Optional[int]] = {}

# Graceful shutdown flag
shutdown_requested = False


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global shutdown_requested
    print(f"\nINFO: Received signal {signum}, initiating graceful shutdown...")
    shutdown_requested = True


def resolve_workflow(comment_body: str) -> Optional[str]:
    """Resolve a comment body to a workflow script name. Returns None if no match."""
    keyword = comment_body.strip().lower()

    # Try longest keywords first to avoid prefix collisions
    for kw in sorted(WORKFLOW_SCRIPTS.keys(), key=len, reverse=True):
        if keyword == kw or keyword.startswith(kw):
            return WORKFLOW_SCRIPTS[kw]

    return None


def should_process_issue(issue_number: int) -> tuple[bool, str]:
    """Determine if an issue should be processed based on comments.

    Returns (should_process, workflow_script).
    """
    comments = fetch_issue_comments(REPO_PATH, issue_number)

    # If no comments, it's a new issue - process with default workflow
    if not comments:
        print(f"INFO: Issue #{issue_number} has no comments - marking for processing")
        return True, "adw_plan_build.py"

    # Get the latest comment
    latest_comment = comments[-1]
    comment_body = latest_comment.get("body", "").lower()
    comment_id = latest_comment.get("id")

    # Check if we've already processed this comment
    last_processed_comment = issue_last_comment.get(issue_number)
    if last_processed_comment == comment_id:
        return False, ""

    # Check if latest comment matches a workflow keyword
    workflow = resolve_workflow(comment_body)
    if workflow:
        print(f"INFO: Issue #{issue_number} - comment matches '{comment_body.strip()}' → {workflow}")
        issue_last_comment[issue_number] = comment_id
        return True, workflow

    return False, ""


def trigger_adw_workflow(issue_number: int, workflow_script: str = "adw_plan_build.py") -> bool:
    """Trigger an ADW workflow for a specific issue."""
    try:
        script_path = Path(__file__).parent / workflow_script

        print(f"INFO: Triggering {workflow_script} for issue #{issue_number}")

        cmd = ["uv", "run", str(script_path), str(issue_number)]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=script_path.parent.parent  # project root
        )

        if result.returncode == 0:
            print(f"INFO: Successfully triggered {workflow_script} for issue #{issue_number}")
            return True
        else:
            print(f"ERROR: Failed to trigger {workflow_script} for issue #{issue_number}")
            if result.stdout:
                print(f"ERROR stdout: {result.stdout}")
            if result.stderr:
                print(f"ERROR stderr: {result.stderr}")
            return False

    except Exception as e:
        print(f"ERROR: Exception while triggering workflow for issue #{issue_number}: {e}")
        return False


def check_and_process_issues():
    """Main function that checks for issues and processes qualifying ones."""
    if shutdown_requested:
        print(f"INFO: Shutdown requested, skipping check cycle")
        return

    start_time = time.time()
    print(f"INFO: Starting issue check cycle")

    try:
        issues = fetch_open_issues(REPO_PATH)

        if not issues:
            print(f"INFO: No open issues found")
            return

        new_qualifying_issues = []

        for issue in issues:
            issue_number = issue.number
            if not issue_number:
                continue

            if issue_number in processed_issues:
                continue

            should_process, workflow = should_process_issue(issue_number)
            if should_process:
                new_qualifying_issues.append((issue_number, workflow))

        if new_qualifying_issues:
            print(f"INFO: Found {len(new_qualifying_issues)} new qualifying issues")

            for issue_number, workflow in new_qualifying_issues:
                if shutdown_requested:
                    print(f"INFO: Shutdown requested, stopping issue processing")
                    break

                if trigger_adw_workflow(issue_number, workflow):
                    processed_issues.add(issue_number)
                else:
                    print(f"WARNING: Failed to process issue #{issue_number}, will retry in next cycle")
        else:
            print(f"INFO: No new qualifying issues found")

        cycle_time = time.time() - start_time
        print(f"INFO: Check cycle completed in {cycle_time:.2f} seconds")
        print(f"INFO: Total processed issues in session: {len(processed_issues)}")

    except Exception as e:
        print(f"ERROR: Error during check cycle: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main entry point for the cron trigger."""
    print(f"INFO: Starting ADW cron trigger")
    print(f"INFO: Repository: {REPO_PATH}")
    print(f"INFO: Polling interval: 20 seconds")
    print(f"INFO: Supported workflows: {list(WORKFLOW_SCRIPTS.keys())}")

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    schedule.every(20).seconds.do(check_and_process_issues)

    check_and_process_issues()

    print(f"INFO: Entering main scheduling loop")
    while not shutdown_requested:
        schedule.run_pending()
        time.sleep(1)

    print(f"INFO: Shutdown complete")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        print(__doc__)
        print("\nUsage: ./trigger_cron.py")
        print("\nEnvironment variables:")
        print("  GITHUB_PAT - (Optional) GitHub Personal Access Token")
        print(f"\nSupported workflow keywords: {list(WORKFLOW_SCRIPTS.keys())}")
        sys.exit(0)

    main()
