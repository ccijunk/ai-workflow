import tempfile
from pathlib import Path
from unittest.mock import patch
from flowctl.executors import EchoAdapter, OpencodeAdapter
from flowctl.executors.base import ExecutorInput
from flowctl.models import Node


def test_echo_adapter_returns_outputs():
    adapter = EchoAdapter()
    with tempfile.TemporaryDirectory() as tmp:
        run_dir = Path(tmp)
        inp = ExecutorInput(
            role="test",
            prompt="Test prompt content",
            prompt_path="prompts/test.md",
            skill_paths=[],
            inputs={},
            outputs={"spec": "spec.md"},
            run_dir=run_dir,
        )
        result = adapter.execute(inp)
        assert result.returncode == 0
        assert "Role: test" in result.stdout
        assert "Prompt Path: prompts/test.md" in result.stdout
        assert (run_dir / "spec.md").exists()


def test_opencode_adapter_builds_prompt():
    adapter = OpencodeAdapter()
    with tempfile.TemporaryDirectory() as tmp:
        run_dir = Path(tmp)
        inp = ExecutorInput(
            role="developer",
            prompt="Write code to implement the feature",
            prompt_path="prompts/code.md",
            skill_paths=["skills/tdd.md"],
            inputs={"spec": "spec.md"},
            outputs={"code": "output/code.py"},
            run_dir=run_dir,
        )
        prompt = adapter._load_prompt(inp)
        assert "Write code to implement the feature" in prompt


def test_opencode_adapter_with_model():
    adapter = OpencodeAdapter(model="alibaba-cn/glm-5", agent="coder")
    assert adapter.model == "alibaba-cn/glm-5"
    assert adapter.agent == "coder"


def test_opencode_adapter_uses_processed_prompt():
    adapter = OpencodeAdapter()
    
    node = Node(
        role="developer",
        prompt="prompts/test.md",
        inputs={"requirement": "requirement.md"},
        outputs={"implementation": "implementation.md"},
        executor="opencode"
    )
    
    processed_prompt = "# Processed Prompt\n\n## Input\n\nrequirement: Read from requirement.md\n\n## Output\n\nimplementation: Write to implementation.md"
    
    inp = ExecutorInput(
        role="developer",
        prompt=processed_prompt,
        prompt_path="prompts/implement.md",
        skill_paths=[],
        inputs={"requirement": "requirement.md"},
        outputs={"implementation": "implementation.md"},
        run_dir=Path("/tmp/test"),
        workflow_dir=None,
        node=node
    )
    
    result = adapter._load_prompt(inp)
    
    assert result == processed_prompt
    assert "## Input" in result
    assert "requirement: Read from requirement.md" in result
    assert "## Output" in result
    assert "implementation: Write to implementation.md" in result