import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class WorkflowState:
    current_node: str
    context: dict[str, str]
    iterations: int
    timestamp: str


def save_state(run_dir: Path, current: str, context: dict[str, str], iterations: int) -> None:
    state_file = run_dir / "state.json"
    state = WorkflowState(
        current_node=current,
        context=context,
        iterations=iterations,
        timestamp=_timestamp(),
    )
    state_file.write_text(json.dumps(state.__dict__, indent=2))


def load_state(run_dir: Path) -> Optional[WorkflowState]:
    state_file = run_dir / "state.json"
    if not state_file.exists():
        return None
    
    try:
        data = json.loads(state_file.read_text())
        return WorkflowState(
            current_node=data["current_node"],
            context=data["context"],
            iterations=data["iterations"],
            timestamp=data["timestamp"],
        )
    except (json.JSONDecodeError, KeyError):
        return None


def has_state(run_dir: Path) -> bool:
    state_file = run_dir / "state.json"
    return state_file.exists()


def clear_state(run_dir: Path) -> None:
    state_file = run_dir / "state.json"
    if state_file.exists():
        state_file.unlink()


def _timestamp() -> str:
    import time
    return time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())