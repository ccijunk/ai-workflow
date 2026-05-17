from pathlib import Path
from .models import FlowctlConfig


def resolve_paths(
    config_path: str,
    run_dir_override: str | None,
    workflow_dir_override: str | None,
) -> tuple[Path, Path]:
    """Resolve run_dir and workflow_dir from config + CLI overrides.
    
    Precedence: CLI > config > defaults
    Relative paths resolved from current working directory.
    """
    config = _load_config(config_path)
    
    run_dir = run_dir_override or config.run_dir or ".flows/runs"
    workflow_dir = workflow_dir_override or config.workflow_dir or ".flows"
    
    run_dir_path = Path(run_dir)
    workflow_dir_path = Path(workflow_dir)
    
    if not run_dir_path.is_absolute():
        run_dir_path = Path.cwd() / run_dir_path
    if not workflow_dir_path.is_absolute():
        workflow_dir_path = Path.cwd() / workflow_dir_path
    
    return run_dir_path, workflow_dir_path


def _load_config(config_path: str) -> FlowctlConfig:
    """Load config from file, return defaults if not found."""
    path = Path(config_path)
    if path.exists():
        import yaml
        with open(path) as f:
            data = yaml.safe_load(f) or {}
        return FlowctlConfig(**data)
    return FlowctlConfig()