import tempfile
from pathlib import Path
from flowctl.executors import EchoAdapter
from flowctl.executors.base import ExecutorInput


def test_echo_adapter_returns_outputs():
    adapter = EchoAdapter()
    with tempfile.TemporaryDirectory() as tmp:
        run_dir = Path(tmp)
        inp = ExecutorInput(
            role="test",
            prompt_path="prompts/test.md",
            skill_paths=[],
            inputs={},
            outputs={"spec": "spec.md"},
            run_dir=run_dir,
        )
        result = adapter.execute(inp)
        assert result.returncode == 0
        assert "Role: test" in result.stdout
        assert "Prompt: prompts/test.md" in result.stdout
        assert (run_dir / "spec.md").exists()