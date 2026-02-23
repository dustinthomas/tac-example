#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic"]
# ///

"""
GitHub Operations Module - AI Developer Workflow (ADW)

This module contains all GitHub-related operations including:
- Issue fetching and manipulation
- Comment posting
- Repository path extraction
- Issue status management
"""

import subprocess
import sys
import os
import json
from typing import Dict, List, Optional
from adw_modules.data_types import GitHubIssue, GitHubIssueListItem


def get_github_env() -> Optional[dict]:
    """Get environment with GitHub token set up. Returns None if no GITHUB_PAT."""
    github_pat = os.getenv("GITHUB_PAT")
    if not github_pat:
        return None

    env = {
        "GH_TOKEN": github_pat,
        "PATH": os.environ.get("PATH", ""),
    }
    return env


def get_repo_url() -> str:
    """Get GitHub repository URL from git remote."""
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        raise ValueError(
            "No git remote 'origin' found. Please ensure you're in a git repository with a remote."
        )
    except FileNotFoundError:
        raise ValueError("git command not found. Please ensure git is installed.")


def extract_repo_path(github_url: str) -> str:
    """Extract owner/repo from GitHub URL."""
    if github_url.startswith("git@github.com:"):
        return github_url.replace("git@github.com:", "").replace(".git", "")
    return github_url.replace("https://github.com/", "").replace(".git", "")


def fetch_issue(issue_number: str, repo_path: str) -> GitHubIssue:
    """Fetch GitHub issue using gh CLI and return typed model."""
    cmd = [
        "gh",
        "issue",
        "view",
        issue_number,
        "-R",
        repo_path,
        "--json",
        "number,title,body,state,author,assignees,labels,milestone,comments,createdAt,updatedAt,closedAt,url",
    ]

    env = get_github_env()

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)

        if result.returncode == 0:
            issue_data = json.loads(result.stdout)
            issue = GitHubIssue(**issue_data)
            return issue
        else:
            print(result.stderr, file=sys.stderr)
            sys.exit(result.returncode)
    except FileNotFoundError:
        print("Error: GitHub CLI (gh) is not installed.", file=sys.stderr)
        print("\nTo install gh:", file=sys.stderr)
        print("  - macOS: brew install gh", file=sys.stderr)
        print("  - Linux: sudo pacman -S github-cli  # Manjaro/Arch", file=sys.stderr)
        print(
            "  - Other: See https://github.com/cli/cli#installation",
            file=sys.stderr,
        )
        print("\nAfter installation, authenticate with: gh auth login", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error parsing issue data: {e}", file=sys.stderr)
        sys.exit(1)


def make_issue_comment(issue_id: str, comment: str) -> None:
    """Post a comment to a GitHub issue using gh CLI."""
    github_repo_url = get_repo_url()
    repo_path = extract_repo_path(github_repo_url)

    cmd = [
        "gh",
        "issue",
        "comment",
        issue_id,
        "-R",
        repo_path,
        "--body",
        comment,
    ]

    env = get_github_env()

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)

        if result.returncode == 0:
            print(f"Successfully posted comment to issue #{issue_id}")
        else:
            print(f"Error posting comment: {result.stderr}", file=sys.stderr)
            sys.exit(result.returncode)
    except Exception as e:
        print(f"Error posting comment: {e}", file=sys.stderr)
        sys.exit(1)


def mark_issue_in_progress(issue_id: str) -> None:
    """Mark issue as in progress by adding label and comment."""
    github_repo_url = get_repo_url()
    repo_path = extract_repo_path(github_repo_url)

    cmd = [
        "gh",
        "issue",
        "edit",
        issue_id,
        "-R",
        repo_path,
        "--add-label",
        "in_progress",
    ]

    env = get_github_env()

    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print(f"Note: Could not add 'in_progress' label: {result.stderr}")

    cmd = [
        "gh",
        "issue",
        "edit",
        issue_id,
        "-R",
        repo_path,
        "--add-assignee",
        "@me",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode == 0:
        print(f"Assigned issue #{issue_id} to self")


def _create_screenshots_branch(repo_path: str, env: dict) -> bool:
    """Create the 'screenshots' branch from the default branch HEAD."""
    try:
        # Get default branch SHA
        result = subprocess.run(
            ["gh", "api", f"repos/{repo_path}/git/ref/heads/main"],
            capture_output=True, text=True, env=env, timeout=15,
        )
        if result.returncode != 0:
            print(f"Could not get main branch ref: {result.stderr}", file=sys.stderr)
            return False

        sha = json.loads(result.stdout).get("object", {}).get("sha")
        if not sha:
            return False

        # Create the screenshots branch
        payload = json.dumps({"ref": "refs/heads/screenshots", "sha": sha})
        create = subprocess.run(
            ["gh", "api", f"repos/{repo_path}/git/refs", "--method", "POST", "--input", "-"],
            input=payload, capture_output=True, text=True, env=env, timeout=15,
        )
        if create.returncode == 0:
            print("Created 'screenshots' branch")
            return True
        print(f"Failed to create screenshots branch: {create.stderr}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error creating screenshots branch: {e}", file=sys.stderr)
        return False


def upload_screenshot_to_github(file_path: str, repo_path: str, issue_number: str) -> Optional[str]:
    """Upload a screenshot to GitHub via issue comment attachment.

    Uses gh api to upload the file as a repository asset, returns the hosted URL.
    Falls back gracefully (returns None) on failure.
    """
    if not os.path.isfile(file_path):
        print(f"Screenshot file not found: {file_path}", file=sys.stderr)
        return None

    env = get_github_env()
    filename = os.path.basename(file_path)

    # Upload via gh api to repo contents (as a temporary approach, use issue body edit trick)
    # Actually, GitHub doesn't have a direct image upload API for issues.
    # Best approach: upload to repo as a blob in a known path, then reference it.
    # Simpler: use `gh issue comment` with file attachment via stdin isn't supported.
    # Most reliable: upload as release asset or use the camo proxy.
    # Pragmatic approach: encode as base64 in a repo file, or just reference local path.

    # Use gh api to upload to repo contents in a screenshots branch
    import base64
    try:
        with open(file_path, "rb") as f:
            content_b64 = base64.b64encode(f.read()).decode()

        upload_path = f"screenshots/issue-{issue_number}/{filename}"
        payload = json.dumps({
            "message": f"Upload screenshot {filename} for issue #{issue_number}",
            "content": content_b64,
            "branch": "screenshots",
        })

        cmd = [
            "gh", "api",
            f"repos/{repo_path}/contents/{upload_path}",
            "--method", "PUT",
            "--input", "-",
        ]

        result = subprocess.run(
            cmd, input=payload, capture_output=True, text=True, env=env, timeout=30,
        )

        if result.returncode == 0:
            data = json.loads(result.stdout)
            download_url = data.get("content", {}).get("download_url")
            if download_url:
                print(f"Uploaded screenshot: {download_url}")
                return download_url
            return None
        else:
            # Branch might not exist — create it and retry
            if "Reference does not exist" in result.stderr or "Not Found" in result.stderr:
                if _create_screenshots_branch(repo_path, env):
                    retry = subprocess.run(
                        cmd, input=payload, capture_output=True, text=True, env=env, timeout=30,
                    )
                    if retry.returncode == 0:
                        data = json.loads(retry.stdout)
                        download_url = data.get("content", {}).get("download_url")
                        if download_url:
                            print(f"Uploaded screenshot (after branch create): {download_url}")
                            return download_url
                print(f"Screenshots branch creation/upload failed: {result.stderr}", file=sys.stderr)
            else:
                print(f"Screenshot upload failed: {result.stderr}", file=sys.stderr)
            return None

    except Exception as e:
        print(f"Error uploading screenshot: {e}", file=sys.stderr)
        return None


def post_review_comment_with_screenshots(
    issue_number: str,
    comment_text: str,
    screenshot_paths: List[str],
) -> None:
    """Post a review comment with embedded screenshots to a GitHub issue.

    Uploads each screenshot and embeds the URL in the comment.
    Falls back to text-only comment if uploads fail.
    """
    github_repo_url = get_repo_url()
    repo_path = extract_repo_path(github_repo_url)

    screenshot_md_parts: List[str] = []
    for path in screenshot_paths:
        url = upload_screenshot_to_github(path, repo_path, issue_number)
        if url:
            name = os.path.basename(path)
            screenshot_md_parts.append(f"![{name}]({url})")

    if screenshot_md_parts:
        screenshots_section = "\n\n### Screenshots\n" + "\n".join(screenshot_md_parts)
        full_comment = comment_text + screenshots_section
    else:
        full_comment = comment_text

    make_issue_comment(issue_number, full_comment)


def fetch_open_issues(repo_path: str) -> List[GitHubIssueListItem]:
    """Fetch all open issues from the GitHub repository."""
    try:
        cmd = [
            "gh",
            "issue",
            "list",
            "--repo",
            repo_path,
            "--state",
            "open",
            "--json",
            "number,title,body,labels,createdAt,updatedAt",
            "--limit",
            "1000",
        ]

        env = get_github_env()

        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True, env=env
        )

        issues_data = json.loads(result.stdout)
        issues = [GitHubIssueListItem(**issue_data) for issue_data in issues_data]
        print(f"Fetched {len(issues)} open issues")
        return issues

    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to fetch issues: {e.stderr}", file=sys.stderr)
        return []
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse issues JSON: {e}", file=sys.stderr)
        return []


def fetch_issue_comments(repo_path: str, issue_number: int) -> List[Dict]:
    """Fetch all comments for a specific issue."""
    try:
        cmd = [
            "gh",
            "issue",
            "view",
            str(issue_number),
            "--repo",
            repo_path,
            "--json",
            "comments",
        ]

        env = get_github_env()

        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True, env=env
        )
        data = json.loads(result.stdout)
        comments = data.get("comments", [])

        comments.sort(key=lambda c: c.get("createdAt", ""))

        return comments

    except subprocess.CalledProcessError as e:
        print(
            f"ERROR: Failed to fetch comments for issue #{issue_number}: {e.stderr}",
            file=sys.stderr,
        )
        return []
    except json.JSONDecodeError as e:
        print(
            f"ERROR: Failed to parse comments JSON for issue #{issue_number}: {e}",
            file=sys.stderr,
        )
        return []
