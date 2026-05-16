import click
from pathlib import Path
from .init_cmd import run_init
from .loader import load_workflow, validate_workflow
from .runner import run_workflow
from .executors import EchoAdapter


@click.group()
def main():
    pass


@main.command()
@click.option("--target", default=None, help="Target directory")
def init(target):
    """Bootstrap .flows/ directory in the target project."""
    run_init(target)


@main.command()
@click.option("--target", default=None)
def upgrade(target):
    """Reconcile .flows/config.yaml schema for new framework versions."""
    from .upgrade_cmd import run_upgrade
    run_upgrade(target)


@main.command()
@click.option("--dry-run", is_flag=True)
@click.option("--executor", default="echo")
@click.option("--run-id", default=None)
@click.argument("workflow", default=".flows/workflows/default.yaml")
def run(dry_run, executor, workflow, run_id):
    wf_path = Path(workflow)
    if not wf_path.exists():
        click.echo(f"Workflow not found: {wf_path}", err=True)
        raise click.Abort()

    wf = load_workflow(wf_path)
    errors = validate_workflow(wf)
    if errors:
        for e in errors:
            click.echo(f"Validation error: {e}", err=True)
        raise click.Abort()

    run_dir = Path(".flows/runs") / (run_id or "latest")
    run_dir.mkdir(parents=True, exist_ok=True)

    if executor != "echo":
        click.echo(f"Executor '{executor}' not yet supported (v1 only supports 'echo')", err=True)
        raise click.Abort()

    adapter = EchoAdapter()
    result = run_workflow(wf, run_dir, adapter=adapter, dry_run=dry_run)
    click.echo(f"Run complete. Context: {result}")