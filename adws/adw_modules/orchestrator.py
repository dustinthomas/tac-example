"""Orchestrator utilities for chaining ADW phase scripts."""

import os
import subprocess
import sys
from pathlib import Path
from typing import List

from adw_modules.utils import get_project_root


def get_adws_dir() -> str:
    """Get the adws/ directory path."""
    return os.path.join(get_project_root(), "adws")


def run_phase(script_name: str, args: List[str]) -> int:
    """Run an ADW phase script via uv run.

    Args:
        script_name: Script filename (e.g., "adw_plan.py")
        args: Arguments to pass to the script

    Returns:
        Exit code from the subprocess
    """
    script_path = os.path.join(get_adws_dir(), script_name)
    cmd = ["uv", "run", script_path] + args

    print(f"\n{'='*60}")
    print(f"Running phase: {script_name} {' '.join(args)}")
    print(f"{'='*60}\n")

    result = subprocess.run(cmd, cwd=get_project_root())
    return result.returncode


def run_pipeline(phases: List[str], issue_number: str, adw_id: str) -> None:
    """Run a sequence of phase scripts, stopping on first failure.

    The first phase receives (issue_number, adw_id).
    Subsequent phases receive (adw_id) only — they load state from disk.

    Args:
        phases: List of script filenames to run in order
        issue_number: GitHub issue number (for the first phase)
        adw_id: ADW workflow ID
    """
    for i, phase_script in enumerate(phases):
        if i == 0:
            # First phase (plan) takes issue_number + adw_id
            exit_code = run_phase(phase_script, [issue_number, adw_id])
        else:
            # Subsequent phases take adw_id only
            exit_code = run_phase(phase_script, [adw_id])

        if exit_code != 0:
            print(f"\nPipeline failed at phase: {phase_script} (exit code {exit_code})")
            sys.exit(exit_code)

    print(f"\nPipeline completed successfully!")
