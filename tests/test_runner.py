import tempfile
from pathlib import Path
from flowctl.models import WorkflowDef, Node, Transition
from flowctl.runner import run_workflow, _mock_execution
from flowctl.executors.base import ExecutorResult, ExecutorInput


SAMPLE_WORKFLOW = WorkflowDef(
    nodes={
        "planner": Node(
            role="planner",
            prompt="prompts/planner.md",
            inputs={},
            outputs={"spec": "spec.md"},
        ),
    },
    transitions=[
        Transition(from_="__start__", to="planner"),
        Transition(from_="planner", to="__end__"),
    ],
)


def test_run_workflow_dry_run():
    with tempfile.TemporaryDirectory() as tmp:
        run_dir = Path(tmp)
        result = run_workflow(SAMPLE_WORKFLOW, run_dir, dry_run=True)
        assert "spec" in result


def test_workflow_loops():
    wf = WorkflowDef(
        nodes={
            "planner": Node(role="planner", prompt="p.md", inputs={}, outputs={}),
            "critic": Node(role="critic", prompt="c.md", inputs={}, outputs={"ok": "ok.md"}),
        },
        transitions=[
            Transition(from_="__start__", to="planner"),
            Transition(from_="planner", to="critic"),
            Transition(from_="critic", to="planner", when='ok == "redo"'),
            Transition(from_="critic", to="__end__", when='ok == "pass"'),
        ],
    )
    with tempfile.TemporaryDirectory() as tmp:
        run_dir = Path(tmp)
        result = run_workflow(wf, run_dir, dry_run=True)
        assert isinstance(result, dict)