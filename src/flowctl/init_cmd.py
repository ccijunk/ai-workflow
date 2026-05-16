import os
from pathlib import Path
import click


def run_init(target_dir: str | None = None) -> str:
    base = Path(target_dir) if target_dir else Path.cwd()
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

    config_path = flows_dir / "config.yaml"
    if not config_path.exists():
        config_path.write_text(
            "preferred_executor: echo\nframework_version: '0.1.0'\n"
        )

    gitignore_path = flows_dir / ".gitignore"
    if not gitignore_path.exists():
        gitignore_path.write_text("memory/local/\nruns/\n")

    click.echo(f"Initialized .flows/ in {base}")
    return str(base)