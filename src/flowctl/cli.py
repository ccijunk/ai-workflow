import click
from pathlib import Path
from .init_cmd import run_init
from .loader import load_workflow, validate_workflow
from .runner import run_workflow
from .executors import create_default_registry


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
@click.option("--log-level", default="INFO", help="Log level: DEBUG, INFO, WARNING, ERROR")
@click.option("--log-format", default="json", help="Log format: json, text")
@click.option("--resume", is_flag=True, help="Resume from saved state in run directory")
@click.option("--approve", is_flag=True, help="Approve pending human node")
@click.option("--reject", is_flag=True, help="Reject pending human node")
@click.argument("workflow", default=".flows/workflows/default.yaml")
def run(dry_run, executor, model, agent, workflow, run_id, issue, log_level, log_format, resume, approve, reject):
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
    
    if (approve or reject) and not resume:
        click.echo("Error: Must use --resume with --approve/--reject", err=True)
        raise click.Abort()
    
    if approve and reject:
        click.echo("Error: Cannot use both --approve and --reject", err=True)
        raise click.Abort()

    run_dir = Path(".flows/runs") / (run_id or "latest")
    run_dir.mkdir(parents=True, exist_ok=True)

    registry = create_default_registry()
    
    if executor not in registry.list_available():
        click.echo(f"Unknown executor: {executor}", err=True)
        click.echo(f"Available: {', '.join(registry.list_available())}", err=True)
        raise click.Abort()

    executor_config = {}
    if model or agent:
        executor_config["opencode"] = {}
        if model:
            executor_config["opencode"]["model"] = model
        if agent:
            executor_config["opencode"]["agent"] = agent

    initial_context = {}
    if issue:
        initial_context["issue_url"] = issue
        issue_file = run_dir / "issue-url.txt"
        issue_file.write_text(issue)

    result = run_workflow(
        wf, run_dir,
        registry=registry,
        default_executor=executor,
        executor_config=executor_config,
        dry_run=dry_run,
        initial_context=initial_context,
        workflow_dir=wf_path.parent.parent,
        log_level=log_level,
        log_format=log_format,
        resume=resume,
    )
    click.echo(f"Run complete. Context: {result}")