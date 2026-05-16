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
@click.option("--run-id", default=None)
@click.option("--target", default=None)
def status(run_id, target):
    """Show workflow run status."""
    from pathlib import Path
    from .state import load_state, WorkflowStatus
    from .runner import MAX_REJECTS
    
    base_dir = Path(target or ".")
    run_dir = base_dir / ".flows" / "runs" / (run_id or "latest")
    
    if not run_dir.exists():
        click.echo(f"Run directory not found: {run_dir}", err=True)
        raise click.Abort()
    
    state = load_state(run_dir)
    if not state:
        click.echo(f"No state found in: {run_dir}")
        return
    
    click.echo(f"Run: {run_dir.name}")
    click.echo(f"Status: {state.status.value.upper()}")
    click.echo(f"Node: {state.current_node}")
    
    if state.reject_counts:
        for node, count in state.reject_counts.items():
            click.echo(f"Reject count ({node}): {count}/{MAX_REJECTS}")
    
    if state.status == WorkflowStatus.PAUSED:
        if state.pending_approval_for:
            click.echo(f"Pending approval: {state.pending_approval_for}")
        click.echo(f"Approve: flowctl run --resume --approve --run-id {run_dir.name}")
        click.echo(f"Reject: flowctl run --resume --reject --reject-reason \"<reason>\" --run-id {run_dir.name}")


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
@click.option("--reject-reason", default=None, help="Reason for rejection (required with --reject)")
@click.argument("workflow", default=".flows/workflows/default.yaml")
def run(dry_run, executor, model, agent, workflow, run_id, issue, log_level, log_format, resume, approve, reject, reject_reason):
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
    
    if reject and not reject_reason:
        click.echo("Error: --reject-reason is required when using --reject", err=True)
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
    
    approval_decision = None
    if approve:
        approval_decision = "yes"
    elif reject:
        approval_decision = "no"

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
        approval_decision=approval_decision,
    )
    click.echo(f"Run complete. Context: {result}")