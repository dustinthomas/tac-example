#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic"]
# ///

"""
ADW Document Phase - Generate feature documentation.

Usage: uv run adw_document.py <adw-id>
"""

import sys
from dotenv import load_dotenv

from adw_modules.data_types import (
    ADWPhase,
    AgentTemplateRequest,
    DocumentationResult,
)
from adw_modules.utils import setup_logger, parse_json
from adw_modules.github import make_issue_comment
from adw_modules.agent import execute_template
from adw_modules.workflow_ops import format_issue_message
from adw_modules.git_ops import git_commit
from adw_modules.state import load_state, advance_phase, save_state

AGENT_DOCUMENTER = "sdlc_documenter"


def main():
    """Document phase: generate docs → commit."""
    load_dotenv()

    if len(sys.argv) < 2:
        print("Usage: uv run adw_document.py <adw-id>")
        sys.exit(1)

    adw_id = sys.argv[1]

    logger = setup_logger(adw_id, "adw_document")
    logger.info(f"ADW Document Phase - ID: {adw_id}")

    state = load_state(adw_id)
    if not state:
        logger.error(f"No state found for ADW ID: {adw_id}.")
        sys.exit(1)

    if not state.plan_file:
        logger.error("No plan file in state.")
        sys.exit(1)

    issue_number = state.issue_number

    make_issue_comment(
        issue_number,
        format_issue_message(adw_id, "ops", "✅ Starting documentation phase"),
    )

    # Run /document
    request = AgentTemplateRequest(
        agent_name=AGENT_DOCUMENTER,
        slash_command="/document",
        args=[state.plan_file],
        adw_id=adw_id,
        model="sonnet",
    )

    logger.info("\n=== Generating documentation ===")
    response = execute_template(request)

    if not response.success:
        logger.warning(f"Documentation generation failed: {response.output}")
        make_issue_comment(
            issue_number,
            format_issue_message(adw_id, AGENT_DOCUMENTER, f"⚠️ Documentation failed: {response.output[:200]}"),
        )
        # Non-fatal — continue pipeline
        advance_phase(state, ADWPhase.PR)
        return

    # Parse results
    parsed = parse_json(response.output)
    if parsed and isinstance(parsed, dict):
        doc_result = DocumentationResult(
            files_created=parsed.get("files_created", []),
            summary=parsed.get("summary", response.output[:200]),
        )
    else:
        doc_result = DocumentationResult(
            summary=response.output[:500],
        )

    state.documentation = doc_result
    save_state(state)

    # Commit docs
    commit_msg, error = git_commit(AGENT_DOCUMENTER, adw_id, logger)
    if error:
        logger.warning(f"Could not commit docs: {error}")

    advance_phase(state, ADWPhase.PR)

    logger.info("Documentation phase completed")
    make_issue_comment(
        issue_number,
        format_issue_message(adw_id, AGENT_DOCUMENTER, "✅ Documentation generated"),
    )


if __name__ == "__main__":
    main()
