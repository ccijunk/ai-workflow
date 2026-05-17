import click
from pathlib import Path
import yaml
from .models import FlowctlConfig


CURRENT_VERSION = "0.1.0"


def run_upgrade(target: str | None, config_path: str | None = None):
    """Upgrade config.yaml to match current framework schema."""
    base = Path(target or ".")
    
    if config_path:
        config_file = Path(config_path)
    else:
        config_file = base / ".flows" / "config.yaml"
    
    if not config_file.exists():
        click.echo(f"No config found at {config_file}. Run 'flowctl init' first.", err=True)
        raise click.Abort()
    
    with open(config_file) as f:
        existing = yaml.safe_load(f) or {}
    
    current_version = existing.get("framework_version", "0.0.0")
    if current_version == CURRENT_VERSION:
        click.echo(f"Already at version {CURRENT_VERSION}")
        return
    
    # Merge with defaults, keeping existing values
    defaults = FlowctlConfig()
    merged = {**defaults.model_dump(), **existing}
    merged["framework_version"] = CURRENT_VERSION
    
    with open(config_file, 'w') as f:
        yaml.dump(merged, f)
    
    click.echo(f"Upgraded from {current_version} to {CURRENT_VERSION}")