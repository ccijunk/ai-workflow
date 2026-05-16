import tempfile
from pathlib import Path
import click
from flowctl.upgrade_cmd import run_upgrade


def test_upgrade_no_config():
    with tempfile.TemporaryDirectory() as tmp:
        try:
            run_upgrade(tmp)
            assert False, "Should have raised"
        except click.exceptions.Abort:
            pass  # click.Abort()


def test_upgrade_idempotent():
    with tempfile.TemporaryDirectory() as tmp:
        config_dir = Path(tmp) / ".flows"
        config_dir.mkdir(parents=True)
        config_path = config_dir / "config.yaml"
        config_path.write_text("framework_version: '0.1.0'\npreferred_executor: echo\n")
        run_upgrade(tmp)
        # Should print "Already at version" but not error