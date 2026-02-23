#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic"]
# ///

"""
ADW Test Phase - Run tests with auto-resolution retry loop.

Calls /test, and on failure calls /resolve_failed_test then retries.
Max retries: MAX_TEST_RETRY_ATTEMPTS (4).

Usage: uv run adw_test.py <adw-id>
"""

import sys
from dotenv import load_dotenv

from adw_modules.data_types import (
    ADWPhase,
    AgentTemplateRequest,
    E2ETestResult,
    TestResult,
)
from adw_modules.utils import setup_logger, parse_json
from adw_modules.github import make_issue_comment
from adw_modules.agent import execute_template
from adw_modules.workflow_ops import format_issue_message, AGENT_IMPLEMENTOR
from adw_modules.git_ops import git_commit
from adw_modules.state import load_state, advance_phase, mark_error, save_state

MAX_TEST_RETRY_ATTEMPTS = 4
AGENT_TESTER = "sdlc_tester"
AGENT_TEST_RESOLVER = "sdlc_test_resolver"


def run_tests(adw_id: str, attempt: int) -> E2ETestResult:
    """Run the /test command and parse results."""
    request = AgentTemplateRequest(
        agent_name=f"{AGENT_TESTER}_attempt_{attempt}",
        slash_command="/test",
        args=[],
        adw_id=adw_id,
        model="sonnet",
    )

    response = execute_template(request)

    if not response.success:
        return E2ETestResult(
            all_passed=False,
            results=[TestResult(suite="all", passed=False, output="", error=response.output)],
            attempt=attempt,
        )

    # Try to parse JSON output from /test
    parsed = parse_json(response.output)
    if parsed and isinstance(parsed, list):
        test_results = []
        all_passed = True
        for item in parsed:
            tr = TestResult(
                suite=item.get("suite", "unknown"),
                passed=item.get("passed", False),
                output=item.get("output", ""),
                error=item.get("error"),
            )
            test_results.append(tr)
            if not tr.passed:
                all_passed = False
        return E2ETestResult(all_passed=all_passed, results=test_results, attempt=attempt)

    # Fallback: check for common pass indicators in raw output
    raw = response.output.lower()
    passed = "all tests passed" in raw or ("pass" in raw and "fail" not in raw)
    return E2ETestResult(
        all_passed=passed,
        results=[TestResult(suite="all", passed=passed, output=response.output)],
        attempt=attempt,
    )


def resolve_failed_tests(adw_id: str, test_output: str, attempt: int) -> bool:
    """Call /resolve_failed_test to attempt auto-fix."""
    request = AgentTemplateRequest(
        agent_name=f"{AGENT_TEST_RESOLVER}_attempt_{attempt}",
        slash_command="/resolve_failed_test",
        args=[test_output],
        adw_id=adw_id,
        model="opus",
    )

    response = execute_template(request)
    return response.success


def main():
    """Test phase with retry loop."""
    load_dotenv()

    if len(sys.argv) < 2:
        print("Usage: uv run adw_test.py <adw-id>")
        sys.exit(1)

    adw_id = sys.argv[1]

    logger = setup_logger(adw_id, "adw_test")
    logger.info(f"ADW Test Phase - ID: {adw_id}")

    state = load_state(adw_id)
    if not state:
        logger.error(f"No state found for ADW ID: {adw_id}. Run plan/build first.")
        sys.exit(1)

    issue_number = state.issue_number

    make_issue_comment(
        issue_number, format_issue_message(adw_id, "ops", "✅ Starting test phase")
    )

    for attempt in range(1, MAX_TEST_RETRY_ATTEMPTS + 1):
        logger.info(f"\n=== Test attempt {attempt}/{MAX_TEST_RETRY_ATTEMPTS} ===")
        make_issue_comment(
            issue_number,
            format_issue_message(adw_id, AGENT_TESTER, f"🧪 Running tests (attempt {attempt})"),
        )

        test_result = run_tests(adw_id, attempt)
        state.test_results.append(test_result)
        save_state(state)

        if test_result.all_passed:
            logger.info("All tests passed!")
            make_issue_comment(
                issue_number,
                format_issue_message(adw_id, AGENT_TESTER, "✅ All tests passed"),
            )
            advance_phase(state, ADWPhase.REVIEW)
            return

        # Tests failed
        failed_suites = [r.suite for r in test_result.results if not r.passed]
        logger.warning(f"Tests failed in: {', '.join(failed_suites)}")

        if attempt >= MAX_TEST_RETRY_ATTEMPTS:
            break

        # Try to resolve
        logger.info("Attempting auto-resolution...")
        make_issue_comment(
            issue_number,
            format_issue_message(adw_id, AGENT_TEST_RESOLVER, "🔧 Attempting to fix test failures"),
        )

        # Collect failure output for resolution
        failure_output = "\n".join(
            f"Suite: {r.suite}\nError: {r.error or r.output}"
            for r in test_result.results if not r.passed
        )

        resolved = resolve_failed_tests(adw_id, failure_output, attempt)
        if resolved:
            # Commit the fix
            commit_msg, error = git_commit(AGENT_TEST_RESOLVER, adw_id, logger)
            if error:
                logger.warning(f"Could not commit test fix: {error}")
        else:
            logger.warning("Auto-resolution failed")

    # All retries exhausted
    logger.error(f"Tests still failing after {MAX_TEST_RETRY_ATTEMPTS} attempts")
    mark_error(state, f"Tests failed after {MAX_TEST_RETRY_ATTEMPTS} attempts")
    make_issue_comment(
        issue_number,
        format_issue_message(
            adw_id, AGENT_TESTER,
            f"❌ Tests still failing after {MAX_TEST_RETRY_ATTEMPTS} attempts"
        ),
    )
    sys.exit(1)


if __name__ == "__main__":
    main()
