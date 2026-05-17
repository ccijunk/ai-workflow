import tempfile
from pathlib import Path
from flowctl.models import WorkflowDef, Node, Transition, FlowctlConfig
from flowctl.runner import run_workflow, resolve_executor, load_flowctl_config
from flowctl.executors import ExecutorRegistry, create_default_registry
from flowctl.executors.base import ExecutorInput, ExecutorResult, ExecutorAdapter


class MockAdapter(ExecutorAdapter):
    def __init__(self, name: str = "mock"):
        self.name = name
    
    def execute(self, inp: ExecutorInput) -> ExecutorResult:
        for key, path_str in inp.outputs.items():
            artifact_path = inp.run_dir / path_str
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text(f"{self.name}: {key}")
        return ExecutorResult(outputs={}, returncode=0, stdout="", stderr="")


def test_registry_register_and_get():
    registry = ExecutorRegistry()
    registry.register("mock", lambda **kw: MockAdapter(**kw))
    
    adapter = registry.get("mock")
    assert isinstance(adapter, MockAdapter)
    assert adapter.name == "mock"


def test_registry_get_with_kwargs():
    registry = ExecutorRegistry()
    registry.register("mock", lambda **kw: MockAdapter(**kw))
    
    adapter = registry.get("mock", name="custom")
    assert adapter.name == "custom"


def test_registry_unknown_raises():
    registry = ExecutorRegistry()
    
    try:
        registry.get("unknown")
        assert False, "Should have raised"
    except ValueError as e:
        assert "Unknown executor" in str(e)


def test_registry_list_available():
    registry = ExecutorRegistry()
    assert registry.list_available() == []
    
    registry.register("echo", lambda **kw: MockAdapter())
    registry.register("opencode", lambda **kw: MockAdapter())
    
    available = registry.list_available()
    assert "echo" in available
    assert "opencode" in available


def test_create_default_registry():
    registry = create_default_registry()
    
    available = registry.list_available()
    assert "echo" in available
    assert "opencode" in available
    
    echo_adapter = registry.get("echo")
    assert echo_adapter.__class__.__name__ == "EchoAdapter"
    
    opencode_adapter = registry.get("opencode", model="test-model")
    assert opencode_adapter.model == "test-model"


def test_resolve_executor_node_takes_precedence():
    node = Node(role="test", prompt="test.md", executor="custom")
    config = FlowctlConfig(preferred_executor="config-exec")
    
    result = resolve_executor(node, "default-exec", config)
    assert result == "custom"


def test_resolve_executor_default_used():
    node = Node(role="test", prompt="test.md")
    config = FlowctlConfig(preferred_executor="config-exec")
    
    result = resolve_executor(node, "default-exec", config)
    assert result == "default-exec"


def test_resolve_executor_config_used():
    node = Node(role="test", prompt="test.md")
    config = FlowctlConfig(preferred_executor="config-exec")
    
    result = resolve_executor(node, "", config)
    assert result == "config-exec"


def test_resolve_executor_echo_fallback():
    node = Node(role="test", prompt="test.md")
    
    result = resolve_executor(node, "", None)
    assert result == "echo"


def test_mixed_executor_workflow():
    registry = ExecutorRegistry()
    registry.register("mock-a", lambda **kw: MockAdapter(name="mock-a"))
    registry.register("mock-b", lambda **kw: MockAdapter(name="mock-b"))
    
    wf = WorkflowDef(
        nodes={
            "node_a": Node(role="test", prompt="a.md", executor="mock-a", outputs={"out1": "out1.txt"}),
            "node_b": Node(role="test", prompt="b.md", executor="mock-b", inputs={"in1": "out1.txt"}, outputs={"out2": "out2.txt"}),
            "node_c": Node(role="test", prompt="c.md", outputs={"out3": "out3.txt"}),
        },
        transitions=[
            Transition(from_="__start__", to="node_a"),
            Transition(from_="node_a", to="node_b"),
            Transition(from_="node_b", to="node_c"),
            Transition(from_="node_c", to="__end__"),
        ],
    )
    
    with tempfile.TemporaryDirectory() as tmp:
        run_dir = Path(tmp)
        result = run_workflow(
            wf, run_dir,
            registry=registry,
            default_executor="mock-a",
            dry_run=False,
        )
        
        out1 = run_dir / "out1.txt"
        out2 = run_dir / "out2.txt"
        out3 = run_dir / "out3.txt"
        
        assert out1.exists()
        assert "mock-a" in out1.read_text()
        
        assert out2.exists()
        assert "mock-b" in out2.read_text()
        
        assert out3.exists()
        assert "mock-a" in out3.read_text()


def test_backward_compatibility_adapter_param():
    mock_adapter = MockAdapter(name="legacy")
    
    wf = WorkflowDef(
        nodes={
            "node1": Node(role="test", prompt="test.md", executor="other", outputs={"out": "out.txt"}),
        },
        transitions=[
            Transition(from_="__start__", to="node1"),
            Transition(from_="node1", to="__end__"),
        ],
    )
    
    with tempfile.TemporaryDirectory() as tmp:
        run_dir = Path(tmp)
        result = run_workflow(wf, run_dir, adapter=mock_adapter, dry_run=False)
        
        out = run_dir / "out.txt"
        assert out.exists()
        assert "legacy" in out.read_text()


def test_executor_config_passed():
    registry = create_default_registry()
    
    wf = WorkflowDef(
        nodes={
            "node1": Node(role="test", prompt="test.md", executor="opencode", outputs={"out": "out.txt"}),
        },
        transitions=[
            Transition(from_="__start__", to="node1"),
            Transition(from_="node1", to="__end__"),
        ],
    )
    
    with tempfile.TemporaryDirectory() as tmp:
        run_dir = Path(tmp)
        result = run_workflow(
            wf, run_dir,
            registry=registry,
            default_executor="opencode",
            executor_config={"opencode": {"model": "test-model", "agent": "test-agent"}},
            dry_run=True,
        )


def test_load_flowctl_config():
    with tempfile.TemporaryDirectory() as tmp:
        workflow_dir = Path(tmp)
        workflow_dir.mkdir(parents=True, exist_ok=True)
        
        config_file = workflow_dir / "config.yaml"
        config_file.write_text("preferred_executor: opencode\nframework_version: 0.1.0\n")
        
        config = load_flowctl_config(workflow_dir)
        assert config is not None
        assert config.preferred_executor == "opencode"


def test_load_flowctl_config_missing():
    with tempfile.TemporaryDirectory() as tmp:
        workflow_dir = Path(tmp)
        
        config = load_flowctl_config(workflow_dir)
        assert config is not None
        assert config.preferred_executor == "echo"  # default value