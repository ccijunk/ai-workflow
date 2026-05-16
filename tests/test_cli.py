from click.testing import CliRunner
from flowctl.cli import main


def test_init_command():
    runner = CliRunner()
    result = runner.invoke(main, ["init"])
    assert result.exit_code == 0
    assert "flowctl init" in result.output


def test_run_command():
    runner = CliRunner()
    result = runner.invoke(main, ["run", "--dry-run"])
    assert result.exit_code == 0
    assert "flowctl run" in result.output