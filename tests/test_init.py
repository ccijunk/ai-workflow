import tempfile
from pathlib import Path
from flowctl.init_cmd import run_init


def test_init_creates_flows_directory():
    with tempfile.TemporaryDirectory() as tmp:
        run_init(tmp)
        flows = Path(tmp) / ".flows"
        assert (flows / "config.yaml").exists()
        assert (flows / "workflows").is_dir()
        assert (flows / "memory").is_dir()
        assert (flows / "memory" / "local").is_dir()
        assert (flows / "runs").is_dir()
        assert (flows / ".gitignore").exists()


def test_init_is_idempotent():
    with tempfile.TemporaryDirectory() as tmp:
        run_init(tmp)
        run_init(tmp)
        assert True


def test_init_config_content():
    with tempfile.TemporaryDirectory() as tmp:
        run_init(tmp)
        content = (Path(tmp) / ".flows" / "config.yaml").read_text()
        assert "echo" in content
        assert "0.1.0" in content