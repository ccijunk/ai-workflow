from click.testing import CliRunner
from flowctl.cli import main
import tempfile
from pathlib import Path


def test_init_command():
    runner = CliRunner()
    result = runner.invoke(main, ["init"])
    assert result.exit_code == 0
    assert "Initialized .flows/" in result.output


def test_run_command():
    runner = CliRunner()
    with runner.isolated_filesystem():
        flows_dir = Path(".flows/workflows")
        flows_dir.mkdir(parents=True)
        workflow_file = flows_dir / "default.yaml"
        workflow_file.write_text(
            "version: '1'\n"
            "nodes:\n"
            "  planner:\n"
            "    role: planner\n"
            "    prompt: prompts/plan.md\n"
            "    inputs: {}\n"
            "    outputs: {spec: spec.md}\n"
            "transitions:\n"
            "  - from: __start__\n"
            "    to: planner\n"
            "  - from: planner\n"
            "    to: __end__\n"
        )
        result = runner.invoke(main, ["run", "--dry-run"])
        assert result.exit_code == 0
        assert "Run complete" in result.output


def test_cli_approve_reject_flags():
    runner = CliRunner()
    with runner.isolated_filesystem():
        flows_dir = Path(".flows/workflows")
        flows_dir.mkdir(parents=True)
        workflow_file = flows_dir / "default.yaml"
        workflow_file.write_text(
            "version: '1'\n"
            "nodes:\n"
            "  planner:\n"
            "    role: planner\n"
            "    prompt: prompts/plan.md\n"
            "    inputs: {}\n"
            "    outputs: {spec: spec.md}\n"
            "transitions:\n"
            "  - from: __start__\n"
            "    to: planner\n"
            "  - from: planner\n"
            "    to: __end__\n"
        )
        
        # Test approve flag validation - must use --resume
        result = runner.invoke(main, ["run", ".flows/workflows/default.yaml", "--approve"])
        assert result.exit_code != 0
        assert "must use --resume" in result.output.lower()
        
        # Test both flags error
        result = runner.invoke(main, ["run", ".flows/workflows/default.yaml", "--resume", "--approve", "--reject"])
        assert result.exit_code != 0
        assert "cannot use both" in result.output.lower()


def test_cli_status_command():
    from flowctl.state import save_state, WorkflowStatus
    
    runner = CliRunner()
    with runner.isolated_filesystem():
        run_dir = Path(".flows/runs/test-run")
        run_dir.mkdir(parents=True)
        save_state(run_dir, "human_approval", {"input": "test.md"}, 1,
                   status=WorkflowStatus.PAUSED, pending_approval_for="approved", pending_transition_from="step1")
        
        result = runner.invoke(main, ["status", "--run-id", "test-run"])
        
        assert result.exit_code == 0
        assert "PAUSED" in result.output
        assert "human_approval" in result.output


def test_cli_reject_reason_required():
    runner = CliRunner()
    with runner.isolated_filesystem():
        flows_dir = Path(".flows/workflows")
        flows_dir.mkdir(parents=True)
        workflow_file = flows_dir / "default.yaml"
        workflow_file.write_text(
            "version: '1'\n"
            "nodes:\n"
            "  planner:\n"
            "    role: planner\n"
            "    prompt: prompts/plan.md\n"
            "    inputs: {}\n"
            "    outputs: {spec: spec.md}\n"
            "transitions:\n"
            "  - from: __start__\n"
            "    to: planner\n"
            "  - from: planner\n"
            "    to: __end__\n"
        )
        
        # Test reject without reason - must require reason
        result = runner.invoke(main, ["run", ".flows/workflows/default.yaml", "--resume", "--reject"])
        assert result.exit_code != 0
        assert "reject-reason" in result.output.lower()


def test_cli_reject_reason_with_value():
    runner = CliRunner()
    with runner.isolated_filesystem():
        flows_dir = Path(".flows/workflows")
        flows_dir.mkdir(parents=True)
        workflow_file = flows_dir / "default.yaml"
        workflow_file.write_text(
            "version: '1'\n"
            "nodes:\n"
            "  planner:\n"
            "    role: planner\n"
            "    prompt: prompts/plan.md\n"
            "    inputs: {}\n"
            "    outputs: {spec: spec.md}\n"
            "transitions:\n"
            "  - from: __start__\n"
            "    to: planner\n"
            "  - from: planner\n"
            "    to: __end__\n"
        )
        
        # Test reject with reason - valid
        result = runner.invoke(main, ["run", ".flows/workflows/default.yaml", "--resume", "--reject", "--reject-reason", "Missing details"])
        # May still fail due to no state, but CLI validation should pass
        assert "--reject-reason is required" not in result.output