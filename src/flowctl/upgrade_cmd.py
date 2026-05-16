from pathlib import Path
import yaml
import click


CURRENT_VERSION = "0.1.0"


def run_upgrade(target_dir: str | None = None) -> str:
    base = Path(target_dir) if target_dir else Path.cwd()
    config_path = base / ".flows" / "config.yaml"

    if not config_path.exists():
        click.echo("No .flows/config.yaml found. Run 'flowctl init' first.", err=True)
        raise click.Abort()

    raw = yaml.safe_load(config_path.read_text())
    current = raw.get("framework_version", "0.0.0")
    if current == CURRENT_VERSION:
        click.echo(f"Already at version {CURRENT_VERSION}")
        return str(base)

    # Future: migrate config schema here
    raw["framework_version"] = CURRENT_VERSION
    config_path.write_text(yaml.dump(raw, default_flow_style=False))
    click.echo(f"Upgraded from {current} to {CURRENT_VERSION}")
    return str(base)