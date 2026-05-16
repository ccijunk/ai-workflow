import tempfile
import pytest
import click
from pathlib import Path
import json
from flowctl.models import WorkflowDef, Node, Transition
from flowctl.runner import run_workflow, _mock_execution
from flowctl.executors.base import ExecutorResult, ExecutorInput
from flowctl.state import save_state, load_state, has_state


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


def test_workflow_conditional_transition():
    wf = WorkflowDef(
        nodes={
            "planner": Node(role="planner", prompt="p.md", inputs={}, outputs={}),
            "critic": Node(role="critic", prompt="c.md", inputs={}, outputs={"ok": "ok.md"}),
        },
        transitions=[
            Transition(from_="__start__", to="planner"),
            Transition(from_="planner", to="critic"),
            Transition(from_="critic", to="__end__"),
        ],
    )
    with tempfile.TemporaryDirectory() as tmp:
        run_dir = Path(tmp)
        result = run_workflow(wf, run_dir, dry_run=True)
        assert isinstance(result, dict)


def test_workflow_no_matching_transition_raises():
    wf = WorkflowDef(
        nodes={
            "planner": Node(role="planner", prompt="p.md", inputs={}, outputs={}),
            "critic": Node(role="critic", prompt="c.md", inputs={}, outputs={"status": "status.md"}),
        },
        transitions=[
            Transition(from_="__start__", to="planner"),
            Transition(from_="planner", to="critic"),
            Transition(from_="critic", to="planner", when='status == "redo"'),
            Transition(from_="critic", to="__end__", when='status == "done"'),
        ],
    )
    with tempfile.TemporaryDirectory() as tmp:
        run_dir = Path(tmp)
        # mock returns status="mock: status" which doesn't match either condition
        with pytest.raises(RuntimeError, match="No valid transitions"):
            run_workflow(wf, run_dir, dry_run=True)


def test_workflow_missing_node_raises():
    wf = WorkflowDef(
        nodes={
            "planner": Node(role="planner", prompt="p.md", inputs={}, outputs={}),
        },
        transitions=[
            Transition(from_="__start__", to="planner"),
            Transition(from_="planner", to="nonexistent"),
        ],
    )
    with tempfile.TemporaryDirectory() as tmp:
        run_dir = Path(tmp)
        with pytest.raises(RuntimeError, match="not found"):
            run_workflow(wf, run_dir, dry_run=True)


def test_workflow_resume_from_state():
    wf = WorkflowDef(
        nodes={
            "step1": Node(role="dev", prompt="p1.md", inputs={}, outputs={"output1": "out1.md"}),
            "step2": Node(role="dev", prompt="p2.md", inputs={}, outputs={"output2": "out2.md"}),
        },
        transitions=[
            Transition(from_="__start__", to="step1"),
            Transition(from_="step1", to="step2"),
            Transition(from_="step2", to="__end__"),
        ],
    )
    
    with tempfile.TemporaryDirectory() as tmp:
        run_dir = Path(tmp)
        
        # Save state at step1 (after step1 completed, before step2)
        save_state(run_dir, "step1", {"output1": "existing"}, 1)
        
        # Resume - should start from step1, execute step2
        result = run_workflow(wf, run_dir, dry_run=True, resume=True)
        
        # Should have executed step2
        assert "output2" in result
        # Should retain context from state
        assert result["output1"] == "existing"
        
        # State should be cleared after completion
        assert not has_state(run_dir)


def test_workflow_resume_no_state():
    wf = WorkflowDef(
        nodes={
            "step1": Node(role="dev", prompt="p1.md", inputs={}, outputs={"output1": "out1.md"}),
        },
        transitions=[
            Transition(from_="__start__", to="step1"),
            Transition(from_="step1", to="__end__"),
        ],
    )
    
    with tempfile.TemporaryDirectory() as tmp:
        run_dir = Path(tmp)
        
        # No state saved, resume should start fresh
        result = run_workflow(wf, run_dir, dry_run=True, resume=True)
        
        assert "output1" in result


def test_workflow_saves_state_after_node():
    wf = WorkflowDef(
        nodes={
            "step1": Node(role="dev", prompt="p1.md", inputs={}, outputs={"output1": "out1.md"}),
        },
        transitions=[
            Transition(from_="__start__", to="step1"),
            Transition(from_="step1", to="__end__"),
        ],
    )
    
    with tempfile.TemporaryDirectory() as tmp:
        run_dir = Path(tmp)
        
        # Run without dry_run would save state, but dry_run doesn't
        run_workflow(wf, run_dir, dry_run=True)
        
        # Dry run should not save state
        assert not has_state(run_dir)


def test_workflow_state_cleared_on_success():
    wf = WorkflowDef(
        nodes={
            "step1": Node(role="dev", prompt="p1.md", inputs={}, outputs={"output1": "out1.md"}),
        },
        transitions=[
            Transition(from_="__start__", to="step1"),
            Transition(from_="step1", to="__end__"),
        ],
    )
    
    with tempfile.TemporaryDirectory() as tmp:
        run_dir = Path(tmp)
        
        # Mock execution to simulate real run
        run_workflow(wf, run_dir, dry_run=False)
        
        # State should be cleared after successful completion
        assert not has_state(run_dir)


def test_workflow_pauses_at_human_node(tmp_path):
    from flowctl.state import WorkflowStatus
    
    wf = WorkflowDef(
        nodes={
            "step1": Node(role="dev", prompt="p1.md", inputs={}, outputs={"output1": "out1.md"}),
            "human_approval": Node(role="human", prompt="p2.md", executor="human", inputs={}, outputs={"approved": "approved.txt"}),
            "step2": Node(role="dev", prompt="p3.md", inputs={}, outputs={"output2": "out2.md"}),
        },
        transitions=[
            Transition(from_="__start__", to="step1"),
            Transition(from_="step1", to="human_approval"),
            Transition(from_="human_approval", to="step2", when="approved == 'yes'"),
            Transition(from_="step2", to="__end__"),
        ],
    )
    
    result = run_workflow(wf, tmp_path, dry_run=False)
    
    state = load_state(tmp_path)
    assert state is not None
    assert state.status == WorkflowStatus.PAUSED
    assert state.current_node == "human_approval"
    assert state.pending_approval_for == "approved"
    assert state.pending_transition_from == "step1"


def test_workflow_human_node_with_dry_run_does_not_pause(tmp_path):
    from flowctl.state import WorkflowStatus
    
    wf = WorkflowDef(
        nodes={
            "step1": Node(role="dev", prompt="p1.md", inputs={}, outputs={"output1": "out1.md"}),
            "human_approval": Node(role="human", prompt="p2.md", executor="human", inputs={}, outputs={"output2": "out2.md"}),
            "step2": Node(role="dev", prompt="p3.md", inputs={}, outputs={"output3": "out3.md"}),
        },
        transitions=[
            Transition(from_="__start__", to="step1"),
            Transition(from_="step1", to="human_approval"),
            Transition(from_="human_approval", to="step2"),
            Transition(from_="step2", to="__end__"),
        ],
    )
    
    result = run_workflow(wf, tmp_path, dry_run=True)
    
    assert "output2" in result
    assert "output3" in result
    assert not has_state(tmp_path)


def test_workflow_human_node_without_outputs(tmp_path):
    from flowctl.state import WorkflowStatus
    
    wf = WorkflowDef(
        nodes={
            "step1": Node(role="dev", prompt="p1.md", inputs={}, outputs={"output1": "out1.md"}),
            "human_approval": Node(role="human", prompt="p2.md", executor="human", inputs={}, outputs={}),
            "step2": Node(role="dev", prompt="p3.md", inputs={}, outputs={"output2": "out2.md"}),
        },
        transitions=[
            Transition(from_="__start__", to="step1"),
            Transition(from_="step1", to="human_approval"),
            Transition(from_="human_approval", to="step2"),
            Transition(from_="step2", to="__end__"),
        ],
    )
    
    result = run_workflow(wf, tmp_path, dry_run=False)
    
    state = load_state(tmp_path)
    assert state is not None
    assert state.status == WorkflowStatus.PAUSED
    assert state.current_node == "human_approval"
    assert state.pending_approval_for is None
    assert state.pending_transition_from == "step1"


def test_workflow_resume_with_approve(tmp_path):
    wf = WorkflowDef(
        nodes={
            "step1": Node(role="dev", prompt="p1.md", inputs={}, outputs={"output1": "out1.md"}),
            "human_approval": Node(role="human", prompt="p2.md", executor="human", inputs={}, outputs={"approved": "approved.txt"}),
            "step2": Node(role="dev", prompt="p3.md", inputs={}, outputs={"output2": "out2.md"}),
        },
        transitions=[
            Transition(from_="__start__", to="step1"),
            Transition(from_="step1", to="human_approval"),
            Transition(from_="human_approval", to="step2", when="approved == 'yes'"),
            Transition(from_="human_approval", to="__end__", when="approved == 'no'"),
            Transition(from_="step2", to="__end__"),
        ],
    )
    
    from flowctl.state import save_state, WorkflowStatus
    
    # Simulate paused state
    save_state(tmp_path, "human_approval", {"output1": "existing"}, 1, 
               status=WorkflowStatus.PAUSED, pending_approval_for="approved", pending_transition_from="step1")
    
    # Resume with approve
    result = run_workflow(wf, tmp_path, dry_run=False, resume=True, approval_decision="yes")
    
    assert "approved" in result
    assert result["approved"] == "yes"
    assert "output2" in result
    assert not has_state(tmp_path)


def test_workflow_resume_with_reject(tmp_path):
    wf = WorkflowDef(
        nodes={
            "step1": Node(role="dev", prompt="p1.md", inputs={}, outputs={"output1": "out1.md"}),
            "human_approval": Node(role="human", prompt="p2.md", executor="human", inputs={}, outputs={"approved": "approved.txt"}),
            "step2": Node(role="dev", prompt="p3.md", inputs={}, outputs={"output2": "out2.md"}),
        },
        transitions=[
            Transition(from_="__start__", to="step1"),
            Transition(from_="step1", to="human_approval"),
            Transition(from_="human_approval", to="step2", when="approved == 'yes'"),
            Transition(from_="human_approval", to="__end__", when="approved == 'no'"),
            Transition(from_="step2", to="__end__"),
        ],
    )
    
    from flowctl.state import save_state, WorkflowStatus
    
    # Simulate paused state
    save_state(tmp_path, "human_approval", {"output1": "existing"}, 1, 
               status=WorkflowStatus.PAUSED, pending_approval_for="approved", pending_transition_from="step1")
    
    # Resume with reject
    result = run_workflow(wf, tmp_path, dry_run=False, resume=True, approval_decision="no")
    
    assert "approved" in result
    assert result["approved"] == "no"
    # step2 should NOT execute when rejected
    assert "output2" not in result
    assert not has_state(tmp_path)


def test_workflow_resume_paused_without_approval_raises(tmp_path):
    wf = WorkflowDef(
        nodes={
            "step1": Node(role="dev", prompt="p1.md", inputs={}, outputs={"output1": "out1.md"}),
            "human_approval": Node(role="human", prompt="p2.md", executor="human", inputs={}, outputs={"approved": "approved.txt"}),
        },
        transitions=[
            Transition(from_="__start__", to="step1"),
            Transition(from_="step1", to="human_approval"),
            Transition(from_="human_approval", to="__end__"),
        ],
    )
    
    from flowctl.state import save_state, WorkflowStatus
    
    # Simulate paused state
    save_state(tmp_path, "human_approval", {"output1": "existing"}, 1, 
               status=WorkflowStatus.PAUSED, pending_approval_for="approved", pending_transition_from="step1")
    
    # Resume without approval should raise
    with pytest.raises(click.exceptions.Abort):
        run_workflow(wf, tmp_path, dry_run=False, resume=True)