#!/usr/bin/env -S uv run
# /// script
# dependencies = ["fastapi", "uvicorn", "python-dotenv"]
# ///

"""
GitHub Webhook Trigger - AI Developer Workflow (ADW)

FastAPI webhook endpoint that receives GitHub issue events and triggers ADW workflows.
Responds immediately to meet GitHub's 10-second timeout by launching the appropriate
workflow script in the background.

Supported trigger keywords in issue comments:
- "adw" or "adw_plan_build" → adw_plan_build.py
- "adw_sdlc" → adw_sdlc.py
- "adw_patch" → adw_patch.py
- "adw_plan_build_test" → adw_plan_build_test.py
- "adw_plan_build_review" → adw_plan_build_review.py
- "adw_plan_build_test_review" → adw_plan_build_test_review.py

New issues default to adw_plan_build.py.

Usage: uv run trigger_webhook.py
"""

import os
import subprocess
import sys
from fastapi import FastAPI, Request
from dotenv import load_dotenv
import uvicorn
from utils import make_adw_id

# Load environment variables
load_dotenv()

# Configuration
PORT = int(os.getenv("PORT", "8001"))

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

# Create FastAPI app
app = FastAPI(title="ADW Webhook Trigger", description="GitHub webhook endpoint for ADW")

print(f"Starting ADW Webhook Trigger on port {PORT}")


def resolve_workflow(comment_body: str) -> tuple[str, str]:
    """Resolve a comment body to a workflow script and trigger reason.

    Returns (script_name, trigger_reason).
    """
    body_lower = comment_body.strip().lower()

    # Try exact match first (longest keywords first to avoid prefix collisions)
    for kw in sorted(WORKFLOW_SCRIPTS.keys(), key=len, reverse=True):
        if body_lower == kw:
            return WORKFLOW_SCRIPTS[kw], f"Comment with '{kw}' command"

    # Check if any line starts with an adw keyword (supports comments with
    # images or other content before/after the keyword)
    for line in body_lower.splitlines():
        line = line.strip()
        for kw in sorted(WORKFLOW_SCRIPTS.keys(), key=len, reverse=True):
            if line.startswith(kw):
                return WORKFLOW_SCRIPTS[kw], f"Comment with '{kw}' command"

    return "", ""


@app.post("/gh-webhook")
async def github_webhook(request: Request):
    """Handle GitHub webhook events."""
    try:
        event_type = request.headers.get("X-GitHub-Event", "")
        payload = await request.json()

        action = payload.get("action", "")
        issue = payload.get("issue", {})
        issue_number = issue.get("number")

        print(f"Received webhook: event={event_type}, action={action}, issue_number={issue_number}")

        should_trigger = False
        trigger_reason = ""
        workflow_script = "adw_plan_build.py"  # default

        # New issue opened → default workflow
        if event_type == "issues" and action == "opened" and issue_number:
            should_trigger = True
            trigger_reason = "New issue opened"

        # Issue comment → route by keyword
        elif event_type == "issue_comment" and action == "created" and issue_number:
            comment = payload.get("comment", {})
            comment_body = comment.get("body", "").strip().lower()

            print(f"Comment body: '{comment_body}'")

            script, reason = resolve_workflow(comment_body)
            if script:
                should_trigger = True
                workflow_script = script
                trigger_reason = reason

        if should_trigger:
            adw_id = make_adw_id()

            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
            trigger_script = os.path.join(script_dir, workflow_script)

            cmd = ["uv", "run", trigger_script, str(issue_number), adw_id]

            print(f"Launching: {' '.join(cmd)} (reason: {trigger_reason})")

            process = subprocess.Popen(
                cmd,
                cwd=project_root,
                env=os.environ.copy()
            )

            print(f"Background process started for issue #{issue_number} with ADW ID: {adw_id}")

            return {
                "status": "accepted",
                "issue": issue_number,
                "adw_id": adw_id,
                "workflow": workflow_script,
                "message": f"ADW workflow triggered for issue #{issue_number}",
                "reason": trigger_reason,
                "logs": f"agents/{adw_id}/"
            }
        else:
            print(f"Ignoring webhook: event={event_type}, action={action}, issue_number={issue_number}")
            return {
                "status": "ignored",
                "reason": f"Not a triggering event (event={event_type}, action={action})"
            }

    except Exception as e:
        print(f"Error processing webhook: {e}")
        return {
            "status": "error",
            "message": "Internal error processing webhook"
        }


@app.get("/health")
async def health():
    """Health check endpoint - runs comprehensive system health check."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        health_check_script = os.path.join(script_dir, "health_check.py")

        result = subprocess.run(
            ["uv", "run", health_check_script],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=script_dir
        )

        print("=== Health Check Output ===")
        print(result.stdout)
        if result.stderr:
            print("=== Health Check Errors ===")
            print(result.stderr)

        output_lines = result.stdout.strip().split('\n')
        is_healthy = result.returncode == 0

        warnings = []
        errors = []

        capturing_warnings = False
        capturing_errors = False

        for line in output_lines:
            if "Warnings:" in line:
                capturing_warnings = True
                capturing_errors = False
                continue
            elif "Errors:" in line:
                capturing_errors = True
                capturing_warnings = False
                continue
            elif "Next Steps:" in line:
                break

            if capturing_warnings and line.strip().startswith("-"):
                warnings.append(line.strip()[2:])
            elif capturing_errors and line.strip().startswith("-"):
                errors.append(line.strip()[2:])

        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "service": "adw-webhook-trigger",
            "health_check": {
                "success": is_healthy,
                "warnings": warnings,
                "errors": errors,
                "details": "Run health_check.py directly for full report"
            }
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "unhealthy",
            "service": "adw-webhook-trigger",
            "error": "Health check timed out"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "adw-webhook-trigger",
            "error": f"Health check failed: {str(e)}"
        }


if __name__ == "__main__":
    print(f"Starting server on http://0.0.0.0:{PORT}")
    print(f"Webhook endpoint: POST /gh-webhook")
    print(f"Health check: GET /health")
    print(f"Supported workflows: {list(WORKFLOW_SCRIPTS.keys())}")

    uvicorn.run(app, host="0.0.0.0", port=PORT)
