import tempfile
from pathlib import Path
from flowctl.executors import EchoAdapter, OpencodeAdapter
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


def test_opencode_adapter_builds_prompt():
    adapter = OpencodeAdapter()
    with tempfile.TemporaryDirectory() as tmp:
        run_dir = Path(tmp)
        inp = ExecutorInput(
            role="developer",
            prompt_path="prompts/code.md",
            skill_paths=["skills/tdd.md"],
            inputs={"spec": "spec.md"},
            outputs={"code": "output/code.py"},
            run_dir=run_dir,
        )
        prompt = adapter._build_prompt(inp)
        assert "Role: developer" in prompt
        assert "code.md" in prompt
        assert "spec" in prompt
        assert "code" in prompt


def test_opencode_adapter_with_model():
    adapter = OpencodeAdapter(model="alibaba-cn/glm-5", agent="coder")
    assert adapter.model == "alibaba-cn/glm-5"
    assert adapter.agent == "coder"