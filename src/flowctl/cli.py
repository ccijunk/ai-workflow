import click
from pathlib import Path
from .init_cmd import run_init
from .loader import load_workflow, validate_workflow
from .runner import run_workflow
from .executors import EchoAdapter, OpencodeAdapter


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
@click.option("--executor", default="echo", help="Executor: echo, opencode")
@click.option("--model", default=None, help="Model for executor (e.g., alibaba-cn/glm-5)")
@click.option("--agent", default=None, help="Agent name for executor")
@click.option("--run-id", default=None)
@click.option("--issue", default=None, help="GitHub issue URL to process")
@click.argument("workflow", default=".flows/workflows/default.yaml")
def run(dry_run, executor, model, agent, workflow, run_id, issue):
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

    if executor == "echo":
        adapter = EchoAdapter()
    elif executor == "opencode":
        adapter = OpencodeAdapter(model=model, agent=agent)
    else:
        click.echo(f"Unknown executor: {executor}", err=True)
        click.echo("Available executors: echo, opencode", err=True)
        raise click.Abort()

    initial_context = {}
    if issue:
        initial_context["issue_url"] = issue
        issue_file = run_dir / "issue-url.txt"
        issue_file.write_text(issue)

    repo_root_file = run_dir / "repo-root.txt"
    repo_root_file.write_text(str(Path.cwd()))

    result = run_workflow(wf, run_dir, adapter=adapter, dry_run=dry_run, initial_context=initial_context)
    click.echo(f"Run complete. Context: {result}")