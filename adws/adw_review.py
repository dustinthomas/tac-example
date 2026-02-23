#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic"]
# ///

"""
ADW Review Phase - Code review with blocker resolution loop.

Calls /review, and if blockers found calls /implement to fix them.
Max retries: MAX_REVIEW_RETRY_ATTEMPTS (3).

Usage: uv run adw_review.py <adw-id>
"""

import sys
from dotenv import load_dotenv

from adw_modules.data_types import (
    ADWPhase,
    AgentTemplateRequest,
    ReviewIssue,
    ReviewResult,
)
from adw_modules.utils import setup_logger, parse_json
from adw_modules.github import make_issue_comment, post_review_comment_with_screenshots
from adw_modules.agent import execute_template
from adw_modules.workflow_ops import (
    format_issue_message,
    implement_plan,
    run_e2e_screenshots,
    AGENT_IMPLEMENTOR,
)
from adw_modules.git_ops import git_commit
from adw_modules.state import load_state, advance_phase, mark_error, save_state

MAX_REVIEW_RETRY_ATTEMPTS = 3
AGENT_REVIEWER = "sdlc_reviewer"


def run_review(adw_id: str, plan_file: str, attempt: int) -> ReviewResult:
    """Run the /review command and parse results."""
    request = AgentTemplateRequest(
        agent_name=f"{AGENT_REVIEWER}_attempt_{attempt}",
        slash_command="/review",
        args=[plan_file],
        adw_id=adw_id,
        model="opus",
    )

    response = execute_template(request)

    if not response.success:
        return ReviewResult(
            approved=False,
            issues=[ReviewIssue(file="unknown", severity="blocker", description=response.output)],
            summary=f"Review failed: {response.output}",
            attempt=attempt,
        )

    # Try to parse JSON output
    parsed = parse_json(response.output)
    if parsed and isinstance(parsed, dict):
        issues = []
        for item in parsed.get("issues", []):
            issues.append(ReviewIssue(
                file=item.get("file", "unknown"),
                line=item.get("line"),
                severity=item.get("severity", "suggestion"),
                description=item.get("description", ""),
            ))
        return ReviewResult(
            approved=parsed.get("approved", len(issues) == 0),
            issues=issues,
            screenshots=parsed.get("screenshots", []),
            summary=parsed.get("summary", response.output[:200]),
            attempt=attempt,
        )

    # Fallback: assume approved if no blockers mentioned
    raw = response.output.lower()
    has_blockers = "blocker" in raw and ("approved" not in raw or "not approved" in raw)
    return ReviewResult(
        approved=not has_blockers,
        summary=response.output[:500],
        attempt=attempt,
    )


def main():
    """Review phase with blocker resolution loop."""
    load_dotenv()

    if len(sys.argv) < 2:
        print("Usage: uv run adw_review.py <adw-id>")
        sys.exit(1)

    adw_id = sys.argv[1]

    logger = setup_logger(adw_id, "adw_review")
    logger.info(f"ADW Review Phase - ID: {adw_id}")

    state = load_state(adw_id)
    if not state:
        logger.error(f"No state found for ADW ID: {adw_id}.")
        sys.exit(1)

    if not state.plan_file:
        logger.error("No plan file in state.")
        sys.exit(1)

    issue_number = state.issue_number

    make_issue_comment(
        issue_number, format_issue_message(adw_id, "ops", "✅ Starting review phase")
    )

    # Run Playwright e2e tests to capture screenshots before review
    e2e_screenshots = run_e2e_screenshots(logger)

    for attempt in range(1, MAX_REVIEW_RETRY_ATTEMPTS + 1):
        logger.info(f"\n=== Review attempt {attempt}/{MAX_REVIEW_RETRY_ATTEMPTS} ===")
        make_issue_comment(
            issue_number,
            format_issue_message(adw_id, AGENT_REVIEWER, f"🔍 Running review (attempt {attempt})"),
        )

        review_result = run_review(adw_id, state.plan_file, attempt)
        # Merge e2e screenshots into review result
        if e2e_screenshots:
            review_result.screenshots = list(set(review_result.screenshots + e2e_screenshots))
        state.review_results.append(review_result)
        save_state(state)

        if review_result.approved:
            logger.info("Review approved!")
            comment = format_issue_message(adw_id, AGENT_REVIEWER, "✅ Review approved")
            if review_result.screenshots:
                post_review_comment_with_screenshots(
                    issue_number, comment, review_result.screenshots,
                )
            else:
                make_issue_comment(issue_number, comment)
            advance_phase(state, ADWPhase.DOCUMENT)
            return

        # Review found blockers
        blockers = [i for i in review_result.issues if i.severity == "blocker"]
        logger.warning(f"Review found {len(blockers)} blockers")

        if attempt >= MAX_REVIEW_RETRY_ATTEMPTS:
            break

        # Try to fix blockers
        logger.info("Attempting to resolve blockers...")
        make_issue_comment(
            issue_number,
            format_issue_message(adw_id, AGENT_IMPLEMENTOR, "🔧 Fixing review blockers"),
        )

        blocker_desc = "\n".join(
            f"- [{b.file}:{b.line or '?'}] {b.description}" for b in blockers
        )
        fix_response = implement_plan(
            f"Fix these review blockers:\n{blocker_desc}", adw_id, logger
        )

        if fix_response.success:
            commit_msg, error = git_commit(AGENT_REVIEWER, adw_id, logger)
            if error:
                logger.warning(f"Could not commit review fix: {error}")

    # All retries exhausted
    logger.error(f"Review blockers not resolved after {MAX_REVIEW_RETRY_ATTEMPTS} attempts")
    mark_error(state, f"Review blockers after {MAX_REVIEW_RETRY_ATTEMPTS} attempts")
    last_review = state.review_results[-1] if state.review_results else None
    failure_comment = format_issue_message(
        adw_id, AGENT_REVIEWER,
        f"❌ Review blockers not resolved after {MAX_REVIEW_RETRY_ATTEMPTS} attempts"
    )
    if last_review and last_review.screenshots:
        post_review_comment_with_screenshots(
            issue_number, failure_comment, last_review.screenshots,
        )
    else:
        make_issue_comment(issue_number, failure_comment)
    sys.exit(1)


if __name__ == "__main__":
    main()
