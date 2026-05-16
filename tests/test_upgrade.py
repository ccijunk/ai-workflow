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
        content = "framework_version: '0.1.0'\npreferred_executor: echo\n"
        config_path.write_text(content)
        run_upgrade(tmp)
        assert config_path.read_text() == content


def test_upgrade_from_old_version():
    with tempfile.TemporaryDirectory() as tmp:
        config_dir = Path(tmp) / ".flows"
        config_dir.mkdir(parents=True)
        config_path = config_dir / "config.yaml"
        config_path.write_text("framework_version: '0.0.0'\npreferred_executor: echo\n")
        run_upgrade(tmp)
        content = config_path.read_text()
        assert "0.1.0" in content
        assert "0.0.0" not in content