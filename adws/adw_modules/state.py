"""ADW State Management - Persistent state between SDLC phases.

State is persisted as JSON at agents/{adw_id}/adw_state.json.
"""

import json
import os
from datetime import datetime
from typing import Optional

from adw_modules.data_types import ADWPhase, ADWStateData, ADWWorkflow
from adw_modules.utils import get_project_root


def get_state_path(adw_id: str) -> str:
    """Get the file path for ADW state JSON."""
    project_root = get_project_root()
    return os.path.join(project_root, "agents", adw_id, "adw_state.json")


def load_state(adw_id: str) -> Optional[ADWStateData]:
    """Load ADW state from disk. Returns None if not found."""
    state_path = get_state_path(adw_id)
    if not os.path.exists(state_path):
        return None

    with open(state_path, "r") as f:
        data = json.load(f)

    return ADWStateData(**data)


def save_state(state: ADWStateData) -> str:
    """Save ADW state to disk. Returns the file path."""
    state_path = get_state_path(state.adw_id)
    os.makedirs(os.path.dirname(state_path), exist_ok=True)

    state.updated_at = datetime.now().isoformat()

    with open(state_path, "w") as f:
        json.dump(state.model_dump(mode="json"), f, indent=2)

    return state_path


def create_state(
    adw_id: str,
    issue_number: str,
    workflow: ADWWorkflow = ADWWorkflow.PLAN_BUILD,
) -> ADWStateData:
    """Create a new ADW state and persist it."""
    state = ADWStateData(
        adw_id=adw_id,
        issue_number=issue_number,
        workflow=workflow,
    )
    save_state(state)
    return state


def advance_phase(state: ADWStateData, next_phase: ADWPhase) -> ADWStateData:
    """Mark the current phase as completed and move to the next phase."""
    if state.current_phase not in state.completed_phases:
        state.completed_phases.append(state.current_phase)
    state.current_phase = next_phase
    save_state(state)
    return state


def mark_error(state: ADWStateData, error: str) -> ADWStateData:
    """Record an error in the state."""
    state.error = error
    save_state(state)
    return state
