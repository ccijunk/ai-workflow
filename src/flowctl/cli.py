import click
from .init_cmd import run_init


@click.group()
def main():
    pass


@main.command()
@click.option("--target", default=None, help="Target directory")
def init(target):
    """Bootstrap .flows/ directory in the target project."""
    run_init(target)


@main.command()
@click.option("--dry-run", is_flag=True)
@click.option("--executor", default="echo")
@click.option("--run-id", default=None)
def run(dry_run, executor, run_id):
    click.echo(f"flowctl run — dry_run={dry_run}, executor={executor}, run_id={run_id}")