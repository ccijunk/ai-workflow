import tempfile
from pathlib import Path
from flowctl.loader import load_workflow, validate_workflow
from flowctl.models import WorkflowDef, Node, Transition


def test_load_valid_yaml():
    yaml_content = """
nodes:
  planner:
    role: planner
    prompt: prompts/planner.md
    inputs: {}
    outputs: {spec: ".flows/runs/{{run_id}}/spec.md"}
transitions:
  - from: __start__
    to: planner
  - from: planner
    to: __end__
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        path = f.name

    wf = load_workflow(path)
    assert "planner" in wf.nodes
    assert len(wf.transitions) == 2
    Path(path).unlink()


def test_validate_missing_start():
    wf = WorkflowDef(
        nodes={},
        transitions=[Transition(from_="missing", to="__end__")]
    )
    errors = validate_workflow(wf)
    assert any("missing" in e for e in errors)
    assert any("__start__" in e for e in errors)


def test_validate_unknown_node():
    wf = WorkflowDef(
        nodes={},
        transitions=[Transition(from_="__start__", to="nonexistent")]
    )
    errors = validate_workflow(wf)
    assert any("nonexistent" in e for e in errors)