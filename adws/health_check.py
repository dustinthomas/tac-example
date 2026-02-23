#!/usr/bin/env uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "python-dotenv",
#     "pydantic",
# ]
# ///

"""
Health Check Script for ADW System

Usage:
uv run adws/health_check.py [issue_number]

This script performs comprehensive health checks:
1. Validates all required environment variables
2. Checks git repository configuration
3. Tests Claude Code CLI functionality
4. Verifies Julia, PostgreSQL, and Node.js availability
5. Returns structured results
"""

import os
import sys
import json
import subprocess
import tempfile
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import argparse
import re

ADW_PIPELINE_VERSION = "ADW Pipeline v2.0"

from dotenv import load_dotenv
from pydantic import BaseModel

# Import git repo functions from github module
from github import get_repo_url, extract_repo_path, make_issue_comment

# Load environment variables
load_dotenv()


class CheckResult(BaseModel):
    """Individual check result."""

    success: bool
    error: Optional[str] = None
    warning: Optional[str] = None
    details: Dict[str, Any] = {}


class HealthCheckResult(BaseModel):
    """Structure for health check results."""

    success: bool
    timestamp: str
    checks: Dict[str, CheckResult]
    warnings: List[str] = []
    errors: List[str] = []


def check_env_vars() -> CheckResult:
    """Check required environment variables."""
    required_vars = {
        "CLAUDE_CODE_PATH": "Path to Claude Code CLI (defaults to 'claude')",
    }

    optional_vars = {
        "ANTHROPIC_API_KEY": "(Optional) Anthropic API Key - only needed if not using OAuth (Teams/Pro subscription)",
        "GITHUB_PAT": "(Optional) GitHub Personal Access Token - only needed if using different account than 'gh auth login'",
    }

    missing_required = []
    missing_optional = []

    # Check required vars
    for var, desc in required_vars.items():
        if not os.getenv(var):
            if var == "CLAUDE_CODE_PATH":
                # This has a default, so not critical
                continue
            missing_required.append(f"{var} ({desc})")

    # Check optional vars
    for var, desc in optional_vars.items():
        if not os.getenv(var):
            missing_optional.append(f"{var} ({desc})")

    success = len(missing_required) == 0

    return CheckResult(
        success=success,
        error="Missing required environment variables" if not success else None,
        details={
            "missing_required": missing_required,
            "missing_optional": missing_optional,
            "claude_code_path": os.getenv("CLAUDE_CODE_PATH", "claude"),
        },
    )


def check_git_repo() -> CheckResult:
    """Check git repository configuration using github module."""
    try:
        # Get repo URL using the github module function
        repo_url = get_repo_url()
        repo_path = extract_repo_path(repo_url)

        return CheckResult(
            success=True,
            details={
                "repo_url": repo_url,
                "repo_path": repo_path,
            },
        )
    except ValueError as e:
        return CheckResult(success=False, error=str(e))


def check_julia() -> CheckResult:
    """Check that Julia is installed and meets minimum version (1.12+)."""
    try:
        result = subprocess.run(
            ["julia", "--version"], capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return CheckResult(
                success=False,
                error="Julia is installed but --version returned non-zero",
            )

        version_output = result.stdout.strip()
        # Parse version from "julia version 1.12.0" or similar
        match = re.search(r"(\d+)\.(\d+)\.(\d+)", version_output)
        if not match:
            return CheckResult(
                success=False,
                error=f"Could not parse Julia version from: {version_output}",
            )

        major, minor, patch = int(match.group(1)), int(match.group(2)), int(match.group(3))
        version_str = f"{major}.{minor}.{patch}"
        meets_minimum = (major, minor) >= (1, 12)

        return CheckResult(
            success=meets_minimum,
            error=f"Julia {version_str} found but 1.12+ required" if not meets_minimum else None,
            details={
                "version": version_str,
                "meets_minimum": meets_minimum,
            },
        )
    except FileNotFoundError:
        return CheckResult(
            success=False,
            error="Julia is not installed. Install from https://julialang.org/downloads/",
        )
    except subprocess.TimeoutExpired:
        return CheckResult(success=False, error="Julia --version timed out")


def check_postgresql() -> CheckResult:
    """Check that PostgreSQL is running and accessible."""
    # Try pg_isready first (fastest check)
    try:
        result = subprocess.run(
            ["pg_isready", "-h", "localhost"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return CheckResult(
                success=True,
                details={"method": "pg_isready", "output": result.stdout.strip()},
            )
    except FileNotFoundError:
        pass  # pg_isready not available, try psql
    except subprocess.TimeoutExpired:
        pass

    # Fall back to psql connectivity test
    try:
        result = subprocess.run(
            ["psql", "-h", "localhost", "-U", "fab_ui", "-d", "fab_ui_dev", "-c", "SELECT 1;"],
            capture_output=True, text=True, timeout=5,
            env={**os.environ, "PGPASSWORD": os.getenv("PGPASSWORD", "")},
        )
        if result.returncode == 0:
            return CheckResult(
                success=True,
                details={"method": "psql", "database": "fab_ui_dev"},
            )
        else:
            return CheckResult(
                success=False,
                error=f"PostgreSQL connection failed: {result.stderr.strip()}",
                details={"method": "psql"},
            )
    except FileNotFoundError:
        return CheckResult(
            success=False,
            error="Neither pg_isready nor psql found. Install PostgreSQL client tools.",
        )
    except subprocess.TimeoutExpired:
        return CheckResult(
            success=False,
            error="PostgreSQL connection timed out",
        )


def check_node() -> CheckResult:
    """Check that Node.js and npm are available (dev dependency for frontend)."""
    node_version = None
    npm_version = None

    try:
        result = subprocess.run(
            ["node", "--version"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            node_version = result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    try:
        result = subprocess.run(
            ["npm", "--version"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            npm_version = result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    if node_version and npm_version:
        return CheckResult(
            success=True,
            details={"node_version": node_version, "npm_version": npm_version},
        )
    elif node_version:
        return CheckResult(
            success=False,
            error="Node.js found but npm is missing",
            details={"node_version": node_version},
        )
    else:
        return CheckResult(
            success=False,
            error="Node.js is not installed. Required for frontend dev tooling (tsc, vitest).",
        )


def check_claude_code() -> CheckResult:
    """Test Claude Code CLI functionality."""
    claude_path = os.getenv("CLAUDE_CODE_PATH", "claude")

    # First check if Claude Code is installed
    try:
        result = subprocess.run(
            [claude_path, "--version"], capture_output=True, text=True
        )
        if result.returncode != 0:
            return CheckResult(
                success=False,
                error=f"Claude Code CLI not functional at '{claude_path}'",
            )
    except FileNotFoundError:
        return CheckResult(
            success=False,
            error=f"Claude Code CLI not found at '{claude_path}'. Please install or set CLAUDE_CODE_PATH correctly.",
        )

    # Test with a simple prompt
    test_prompt = "What is 2+2? Just respond with the number, nothing else."

    # Prepare environment - unset CLAUDECODE to allow nested execution
    env = os.environ.copy()
    env.pop("CLAUDECODE", None)
    if os.getenv("GITHUB_PAT"):
        env["GH_TOKEN"] = os.getenv("GITHUB_PAT")

    try:
        # Create temporary file for output
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False
        ) as tmp:
            output_file = tmp.name

        # Run Claude Code
        cmd = [
            claude_path,
            "-p",
            test_prompt,
            "--model",
            "haiku",
            "--output-format",
            "stream-json",
            "--verbose",
            "--dangerously-skip-permissions",
        ]

        with open(output_file, "w") as f:
            result = subprocess.run(
                cmd, stdout=f, stderr=subprocess.PIPE, text=True, env=env, timeout=30
            )

        if result.returncode != 0:
            return CheckResult(
                success=False, error=f"Claude Code test failed: {result.stderr}"
            )

        # Parse output to verify it worked
        claude_responded = False
        response_text = ""

        try:
            with open(output_file, "r") as f:
                for line in f:
                    if line.strip():
                        msg = json.loads(line)
                        if msg.get("type") == "result":
                            claude_responded = True
                            response_text = msg.get("result", "")
                            break
        finally:
            # Clean up temp file
            if os.path.exists(output_file):
                os.unlink(output_file)

        return CheckResult(
            success=claude_responded,
            details={
                "test_passed": "4" in response_text,
                "response": response_text[:100] if response_text else "No response",
            },
        )

    except subprocess.TimeoutExpired:
        return CheckResult(
            success=False, error="Claude Code test timed out after 30 seconds"
        )
    except Exception as e:
        return CheckResult(success=False, error=f"Claude Code test error: {str(e)}")


def check_github_cli() -> CheckResult:
    """Check if GitHub CLI is installed and authenticated."""
    try:
        # Check if gh is installed
        result = subprocess.run(["gh", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            return CheckResult(success=False, error="GitHub CLI (gh) is not installed")

        # Check authentication status
        env = os.environ.copy()
        if os.getenv("GITHUB_PAT"):
            env["GH_TOKEN"] = os.getenv("GITHUB_PAT")

        result = subprocess.run(
            ["gh", "auth", "status"], capture_output=True, text=True, env=env
        )

        authenticated = result.returncode == 0

        return CheckResult(
            success=authenticated,
            error="GitHub CLI not authenticated" if not authenticated else None,
            details={"installed": True, "authenticated": authenticated},
        )

    except FileNotFoundError:
        return CheckResult(
            success=False,
            error="GitHub CLI (gh) is not installed. Install with: sudo pacman -S github-cli",
            details={"installed": False},
        )


def run_health_check() -> HealthCheckResult:
    """Run all health checks and return results."""
    result = HealthCheckResult(
        success=True, timestamp=datetime.now().isoformat(), checks={}
    )

    # Check environment variables
    env_check = check_env_vars()
    result.checks["environment"] = env_check
    if not env_check.success:
        result.success = False
        if env_check.error:
            result.errors.append(env_check.error)
        # Add specific missing vars to errors
        missing_required = env_check.details.get("missing_required", [])
        result.errors.extend(
            [f"Missing required env var: {var}" for var in missing_required]
        )

    # Check git repository
    git_check = check_git_repo()
    result.checks["git_repository"] = git_check
    if not git_check.success:
        result.success = False
        if git_check.error:
            result.errors.append(git_check.error)
    elif git_check.warning:
        result.warnings.append(git_check.warning)

    # Check GitHub CLI
    gh_check = check_github_cli()
    result.checks["github_cli"] = gh_check
    if not gh_check.success:
        result.success = False
        if gh_check.error:
            result.errors.append(gh_check.error)

    # Check Julia
    julia_check = check_julia()
    result.checks["julia"] = julia_check
    if not julia_check.success:
        result.success = False
        if julia_check.error:
            result.errors.append(julia_check.error)

    # Check PostgreSQL
    pg_check = check_postgresql()
    result.checks["postgresql"] = pg_check
    if not pg_check.success:
        result.success = False
        if pg_check.error:
            result.errors.append(pg_check.error)

    # Check Node.js
    node_check = check_node()
    result.checks["nodejs"] = node_check
    if not node_check.success:
        result.success = False
        if node_check.error:
            result.errors.append(node_check.error)

    # Check Claude Code (works with either API key or OAuth session)
    claude_check = check_claude_code()
    result.checks["claude_code"] = claude_check
    if not claude_check.success:
        result.success = False
        if claude_check.error:
            result.errors.append(claude_check.error)

    return result


def main():
    """Main entry point."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="ADW System Health Check")
    parser.add_argument(
        "issue_number",
        nargs="?",
        help="Optional GitHub issue number to post results to",
    )
    args = parser.parse_args()

    print(f"Running ADW System Health Check... ({ADW_PIPELINE_VERSION})\n")

    result = run_health_check()

    # Print summary
    status_icon = "PASS" if result.success else "FAIL"
    print(
        f"[{status_icon}] Overall Status: {'HEALTHY' if result.success else 'UNHEALTHY'}"
    )
    print(f"Timestamp: {result.timestamp}\n")

    # Print detailed results
    print("Check Results:")
    print("-" * 50)

    for check_name, check_result in result.checks.items():
        status = "PASS" if check_result.success else "FAIL"
        print(f"\n[{status}] {check_name.replace('_', ' ').title()}:")

        # Print check-specific details
        for key, value in check_result.details.items():
            if value is not None and key not in [
                "missing_required",
                "missing_optional",
            ]:
                print(f"   {key}: {value}")

        if check_result.error:
            print(f"   Error: {check_result.error}")
        if check_result.warning:
            print(f"   Warning: {check_result.warning}")

    # Print warnings
    if result.warnings:
        print("\nWarnings:")
        for warning in result.warnings:
            print(f"   - {warning}")

    # Print errors
    if result.errors:
        print("\nErrors:")
        for error in result.errors:
            print(f"   - {error}")

    # Print next steps
    if not result.success:
        print("\nNext Steps:")
        if any("ANTHROPIC_API_KEY" in e for e in result.errors):
            print("   1. Set ANTHROPIC_API_KEY in your .env file")
        if any("GitHub CLI" in e for e in result.errors):
            print("   2. Install GitHub CLI: sudo pacman -S github-cli")
            print("   3. Authenticate: gh auth login")
        if any("Julia" in e for e in result.errors):
            print("   4. Install Julia 1.12+: https://julialang.org/downloads/")
        if any("PostgreSQL" in e for e in result.errors):
            print("   5. Start PostgreSQL: sudo systemctl start postgresql")
        if any("Node" in e for e in result.errors):
            print("   6. Install Node.js: sudo pacman -S nodejs npm")

    # If issue number provided, post comment
    if args.issue_number:
        print(f"\nPosting health check results to issue #{args.issue_number}...")
        status_label = "HEALTHY" if result.success else "UNHEALTHY"
        comment = f"Health check completed: {status_label}"
        try:
            make_issue_comment(args.issue_number, comment)
            print(f"Posted health check comment to issue #{args.issue_number}")
        except Exception as e:
            print(f"Failed to post comment: {e}")

    # Return appropriate exit code
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
