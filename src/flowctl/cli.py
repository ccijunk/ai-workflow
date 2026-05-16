import click


@click.group()
def main():
    pass


@main.command()
def init():
    click.echo("flowctl init — not implemented yet")


@main.command()
@click.option("--dry-run", is_flag=True)
@click.option("--executor", default="echo")
@click.option("--run-id", default=None)
def run(dry_run, executor, run_id):
    click.echo(f"flowctl run — dry_run={dry_run}, executor={executor}, run_id={run_id}")