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