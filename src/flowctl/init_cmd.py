import click
from pathlib import Path
from .path_resolver import resolve_paths
from .models import FlowctlConfig


def run_init(target: str | None, config_path: str | None = None):
    """Initialize .flows/ directory structure."""
    base = Path(target or ".")
    
    if config_path:
        _, workflow_dir, _ = resolve_paths(config_path, None, None)
        flows_dir = workflow_dir
    else:
        flows_dir = base / ".flows"
    
    dirs = [
        flows_dir,
        flows_dir / "workflows",
        flows_dir / "scripts",
        flows_dir / "memory",
        flows_dir / "memory" / "local",
        flows_dir / "runs",
    ]
    
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        click.echo(f"Created: {d}")
    
    config_file = flows_dir / "config.yaml"
    if not config_file.exists():
        import yaml
        config = FlowctlConfig()
        with open(config_file, 'w') as f:
            yaml.dump(config.model_dump(), f)
        click.echo(f"Created: {config_file}")
    
    gitignore_path = flows_dir / ".gitignore"
    if not gitignore_path.exists():
        gitignore_path.write_text("runs/\nmemory/local/\n")
        click.echo(f"Created: {gitignore_path}")
    
    click.echo(f"Initialized {flows_dir} in {base}")