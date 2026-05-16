import pytest
from pathlib import Path
import json
from flowctl.state import save_state, load_state, has_state, clear_state, WorkflowState


def test_save_and_load_state():
    run_dir = Path("/tmp/test-state-save")
    run_dir.mkdir(parents=True, exist_ok=True)
    
    context = {"key1": "value1", "key2": "value2"}
    save_state(run_dir, "node1", context, 5)
    
    assert has_state(run_dir)
    
    state = load_state(run_dir)
    assert state is not None
    assert state.current_node == "node1"
    assert state.context == context
    assert state.iterations == 5
    assert state.timestamp is not None
    
    state_file = run_dir / "state.json"
    state_file.unlink()
    run_dir.rmdir()


def test_load_state_no_file():
    run_dir = Path("/tmp/test-state-no-file")
    run_dir.mkdir(parents=True, exist_ok=True)
    
    state = load_state(run_dir)
    assert state is None
    
    run_dir.rmdir()


def test_clear_state():
    run_dir = Path("/tmp/test-state-clear")
    run_dir.mkdir(parents=True, exist_ok=True)
    
    save_state(run_dir, "node1", {"key": "value"}, 1)
    assert has_state(run_dir)
    
    clear_state(run_dir)
    assert not has_state(run_dir)
    
    run_dir.rmdir()


def test_clear_state_no_file():
    run_dir = Path("/tmp/test-state-clear-no-file")
    run_dir.mkdir(parents=True, exist_ok=True)
    
    clear_state(run_dir)
    assert not has_state(run_dir)
    
    run_dir.rmdir()


def test_state_json_format():
    run_dir = Path("/tmp/test-state-json")
    run_dir.mkdir(parents=True, exist_ok=True)
    
    save_state(run_dir, "node2", {"output": "result"}, 10)
    
    state_file = run_dir / "state.json"
    content = state_file.read_text()
    
    data = json.loads(content)
    assert data["current_node"] == "node2"
    assert data["context"] == {"output": "result"}
    assert data["iterations"] == 10
    assert "timestamp" in data
    
    state_file.unlink()
    run_dir.rmdir()


def test_load_state_corrupted_json():
    run_dir = Path("/tmp/test-state-corrupted")
    run_dir.mkdir(parents=True, exist_ok=True)
    
    state_file = run_dir / "state.json"
    state_file.write_text("not valid json")
    
    state = load_state(run_dir)
    assert state is None
    
    state_file.unlink()
    run_dir.rmdir()


def test_load_state_missing_fields():
    run_dir = Path("/tmp/test-state-missing")
    run_dir.mkdir(parents=True, exist_ok=True)
    
    state_file = run_dir / "state.json"
    state_file.write_text(json.dumps({"current_node": "node1"}))
    
    state = load_state(run_dir)
    assert state is None
    
    state_file.unlink()
    run_dir.rmdir()