import pytest
from pathlib import Path
from flowctl.artifact_validator import validate_artifacts


def test_validate_workflow_prefix(tmp_path):
    """Output with workflow: prefix should resolve to workflow_dir."""
    workflow_dir = tmp_path / "flows"
    workflow_dir.mkdir()
    memory_dir = workflow_dir / "memory"
    memory_dir.mkdir()
    
    output_file = memory_dir / "ba.md"
    output_file.write_text("test content")
    
    errors = validate_artifacts(
        {"memory_update": "workflow:memory/ba.md"},
        run_dir=tmp_path / "runs/test",
        workflow_dir=workflow_dir,
        repo_dir=None,
    )
    
    assert len(errors) == 0


def test_validate_repo_prefix(tmp_path):
    """Output with repo: prefix should resolve to repo_dir."""
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    
    output_file = repo_dir / "ARCHITECTURE.md"
    output_file.write_text("test content")
    
    errors = validate_artifacts(
        {"arch": "repo:ARCHITECTURE.md"},
        run_dir=tmp_path / "runs/test",
        workflow_dir=tmp_path / "flows",
        repo_dir=repo_dir,
    )
    
    assert len(errors) == 0