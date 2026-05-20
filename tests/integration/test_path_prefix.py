import pytest
from pathlib import Path
from flowctl.models import WorkflowDef, Node, Transition
from flowctl.runner import run_workflow
from flowctl.executors import create_default_registry


def test_path_prefix_workflow_integration(tmp_path):
    """Test end-to-end path prefix resolution in workflow."""
    workflow_dir = tmp_path / "flows"
    workflow_dir.mkdir()
    run_dir = tmp_path / "runs" / "test"
    run_dir.mkdir(parents=True)
    
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    
    memory_dir = workflow_dir / "memory"
    memory_dir.mkdir()
    memory_file = memory_dir / "architect.md"
    memory_file.write_text("# Architect Memory")
    
    repo_file = repo_dir / "REPO.md"
    repo_file.write_text("# Repo Root")
    
    prompt_dir = workflow_dir / "prompts"
    prompt_dir.mkdir()
    prompt_file = prompt_dir / "test.md"
    prompt_file.write_text("# Test Task")
    
    workflow = WorkflowDef(
        version="1",
        nodes={
            "start": Node(
                role="dev",
                prompt="prompts/test.md",
                inputs={
                    "memory": "workflow:memory/architect.md",
                    "repo": "repo:REPO.md",
                    "local": "run:local.md",
                },
                outputs={
                    "memory_out": "workflow:memory/output.md",
                    "repo_out": "repo:OUTPUT.md",
                    "local_out": "run:local_out.md",
                },
            ),
        },
        transitions=[
            Transition(from_="__start__", to="start"),
            Transition(from_="start", to="__end__"),
        ],
    )
    
    registry = create_default_registry()
    
    result = run_workflow(
        workflow,
        run_dir,
        registry=registry,
        default_executor="echo",
        dry_run=True,
        workflow_dir=workflow_dir,
        repo_dir=repo_dir,
    )
    
    assert result is not None