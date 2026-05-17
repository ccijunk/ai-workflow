from flowctl.models import FlowctlConfig


def test_flowctl_config_default_paths():
    config = FlowctlConfig()
    assert config.run_dir == ".flows/runs"
    assert config.workflow_dir == ".flows"


def test_flowctl_config_custom_paths():
    config = FlowctlConfig(run_dir="/tmp/runs", workflow_dir="/shared/workflows")
    assert config.run_dir == "/tmp/runs"
    assert config.workflow_dir == "/shared/workflows"