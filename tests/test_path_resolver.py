import pytest
from pathlib import Path
from flowctl.path_resolver import resolve_paths


def test_resolve_paths_defaults():
    """When no overrides and config missing, use hardcoded defaults."""
    run_dir, workflow_dir = resolve_paths(
        config_path=".flows/config.yaml",
        run_dir_override=None,
        workflow_dir_override=None,
    )
    
    assert run_dir == Path.cwd() / ".flows" / "runs"
    assert workflow_dir == Path.cwd() / ".flows"


def test_resolve_paths_cli_overrides_defaults():
    """CLI options override default paths."""
    run_dir, workflow_dir = resolve_paths(
        config_path=".flows/config.yaml",
        run_dir_override="/tmp/custom-runs",
        workflow_dir_override="/shared/workflows",
    )
    
    assert run_dir == Path("/tmp/custom-runs")
    assert workflow_dir == Path("/shared/workflows")


def test_resolve_paths_cli_overrides_config():
    """CLI options override config values."""
    import tempfile
    import yaml
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump({
            'preferred_executor': 'echo',
            'run_dir': '/config/runs',
            'workflow_dir': '/config/workflows',
        }, f)
        config_path = f.name
    
    try:
        run_dir, workflow_dir = resolve_paths(
            config_path=config_path,
            run_dir_override="/cli/runs",
            workflow_dir_override=None,
        )
        
        assert run_dir == Path("/cli/runs")
        assert workflow_dir == Path("/config/workflows")
    finally:
        Path(config_path).unlink()


def test_resolve_paths_from_config():
    """Config values override defaults."""
    import tempfile
    import yaml
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump({
            'preferred_executor': 'echo',
            'run_dir': '/config/runs',
            'workflow_dir': '/config/workflows',
        }, f)
        config_path = f.name
    
    try:
        run_dir, workflow_dir = resolve_paths(
            config_path=config_path,
            run_dir_override=None,
            workflow_dir_override=None,
        )
        
        assert run_dir == Path("/config/runs")
        assert workflow_dir == Path("/config/workflows")
    finally:
        Path(config_path).unlink()


def test_resolve_paths_relative_from_cwd():
    """Relative paths resolved from current working directory."""
    import tempfile
    import yaml
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump({
            'preferred_executor': 'echo',
            'run_dir': 'my-runs',
            'workflow_dir': 'my-workflows',
        }, f)
        config_path = f.name
    
    try:
        run_dir, workflow_dir = resolve_paths(
            config_path=config_path,
            run_dir_override=None,
            workflow_dir_override=None,
        )
        
        assert run_dir == Path.cwd() / "my-runs"
        assert workflow_dir == Path.cwd() / "my-workflows"
    finally:
        Path(config_path).unlink()