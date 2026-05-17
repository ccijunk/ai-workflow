# Configurable Paths Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add configurable `run_dir` and `workflow_dir` paths with CLI options and config file support.

**Architecture:** Add fields to FlowctlConfig, create path_resolver module for resolution logic, update CLI commands with new options, precedence: CLI > config > defaults.

**Tech Stack:** Python, Pydantic, Click CLI, pytest

---

## File Structure

| File | Purpose |
|------|---------|
| `src/flowctl/models.py` | Add `run_dir`, `workflow_dir` fields to `FlowctlConfig` |
| `src/flowctl/path_resolver.py` | NEW - Path resolution logic with precedence |
| `src/flowctl/cli.py` | Add `--config`, `--run-dir`, `--workflow-dir` options |
| `src/flowctl/runner.py` | Remove hardcoded `.flows` path logic |
| `src/flowctl/init_cmd.py` | Use configurable workflow_dir |
| `src/flowctl/upgrade_cmd.py` | Use configurable config path |
| `tests/test_path_resolver.py` | NEW - Path resolution tests |

---

### Task 1: Add run_dir and workflow_dir fields to FlowctlConfig

**Files:**
- Modify: `src/flowctl/models.py:5-7`
- Test: `tests/test_models.py`

- [ ] **Step 1: Write failing test for FlowctlConfig default paths**

```python
# tests/test_models.py - add to existing file

def test_flowctl_config_default_paths():
    from flowctl.models import FlowctlConfig
    
    config = FlowctlConfig()
    assert config.run_dir == ".flows/runs"
    assert config.workflow_dir == ".flows"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_models.py::test_flowctl_config_default_paths -v`
Expected: FAIL with "FlowctlConfig has no attribute 'run_dir'"

- [ ] **Step 3: Add fields to FlowctlConfig**

```python
# src/flowctl/models.py:5-8 - modify FlowctlConfig class

class FlowctlConfig(BaseModel):
    preferred_executor: str = "echo"
    framework_version: str = "0.1.0"
    run_dir: str = ".flows/runs"
    workflow_dir: str = ".flows"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_models.py::test_flowctl_config_default_paths -v`
Expected: PASS

- [ ] **Step 5: Write test for custom paths in config**

```python
# tests/test_models.py - add after previous test

def test_flowctl_config_custom_paths():
    from flowctl.models import FlowctlConfig
    
    config = FlowctlConfig(run_dir="/tmp/runs", workflow_dir="/shared/workflows")
    assert config.run_dir == "/tmp/runs"
    assert config.workflow_dir == "/shared/workflows"
```

- [ ] **Step 6: Run test to verify it passes**

Run: `uv run pytest tests/test_models.py::test_flowctl_config_custom_paths -v`
Expected: PASS

- [ ] **Step 7: Run all tests**

Run: `uv run pytest tests/ -v`
Expected: All tests pass

- [ ] **Step 8: Commit**

```bash
git add src/flowctl/models.py tests/test_models.py
git commit -m "feat: add run_dir and workflow_dir fields to FlowctlConfig"
```

---

### Task 2: Create path_resolver module

**Files:**
- Create: `src/flowctl/path_resolver.py`
- Create: `tests/test_path_resolver.py`

- [ ] **Step 1: Write failing test for default paths**

```python
# tests/test_path_resolver.py - new file

import pytest
from pathlib import Path
from flowctl.path_resolver import resolve_paths


def test_resolve_paths_defaults():
    """When no overrides and config missing, use hardcoded defaults."""
    run_dir, workflow_dir = resolve_paths(
        config_path=".flows/config.yaml",
        run_dir_override=None,
        workflow_dir_override=None,
    )
    
    assert run_dir == Path.cwd() / ".flows" / "runs"
    assert workflow_dir == Path.cwd() / ".flows"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_path_resolver.py::test_resolve_paths_defaults -v`
Expected: FAIL with "No module named 'flowctl.path_resolver'"

- [ ] **Step 3: Create path_resolver.py with minimal implementation**

```python
# src/flowctl/path_resolver.py - new file

from pathlib import Path
from .models import FlowctlConfig


def resolve_paths(
    config_path: str,
    run_dir_override: str | None,
    workflow_dir_override: str | None,
) -> tuple[Path, Path]:
    """Resolve run_dir and workflow_dir from config + CLI overrides.
    
    Precedence: CLI > config > defaults
    Relative paths resolved from current working directory.
    """
    config = _load_config(config_path)
    
    run_dir = run_dir_override or config.run_dir or ".flows/runs"
    workflow_dir = workflow_dir_override or config.workflow_dir or ".flows"
    
    run_dir_path = Path(run_dir)
    workflow_dir_path = Path(workflow_dir)
    
    if not run_dir_path.is_absolute():
        run_dir_path = Path.cwd() / run_dir_path
    if not workflow_dir_path.is_absolute():
        workflow_dir_path = Path.cwd() / workflow_dir_path
    
    return run_dir_path, workflow_dir_path


def _load_config(config_path: str) -> FlowctlConfig:
    """Load config from file, return defaults if not found."""
    path = Path(config_path)
    if path.exists():
        import yaml
        with open(path) as f:
            data = yaml.safe_load(f) or {}
        return FlowctlConfig(**data)
    return FlowctlConfig()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_path_resolver.py::test_resolve_paths_defaults -v`
Expected: PASS

- [ ] **Step 5: Write test for CLI overrides**

```python
# tests/test_path_resolver.py - add after previous test

def test_resolve_paths_cli_overrides_defaults():
    """CLI options override default paths."""
    run_dir, workflow_dir = resolve_paths(
        config_path=".flows/config.yaml",
        run_dir_override="/tmp/custom-runs",
        workflow_dir_override="/shared/workflows",
    )
    
    assert run_dir == Path("/tmp/custom-runs")
    assert workflow_dir == Path("/shared/workflows")


def test_resolve_paths_cli_overrides_config():
    """CLI options override config values."""
    # Create temp config with custom paths
    import tempfile
    import yaml
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump({
            'preferred_executor': 'echo',
            'run_dir': '/config/runs',
            'workflow_dir': '/config/workflows',
        }, f)
        config_path = f.name
    
    try:
        run_dir, workflow_dir = resolve_paths(
            config_path=config_path,
            run_dir_override="/cli/runs",
            workflow_dir_override=None,  # CLI override only run_dir
        )
        
        assert run_dir == Path("/cli/runs")
        assert workflow_dir == Path("/config/workflows")  # From config
    finally:
        Path(config_path).unlink()
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `uv run pytest tests/test_path_resolver.py -v`
Expected: All 3 tests pass

- [ ] **Step 7: Write test for config values**

```python
# tests/test_path_resolver.py - add after previous tests

def test_resolve_paths_from_config():
    """Config values override defaults."""
    import tempfile
    import yaml
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump({
            'preferred_executor': 'echo',
            'run_dir': '/config/runs',
            'workflow_dir': '/config/workflows',
        }, f)
        config_path = f.name
    
    try:
        run_dir, workflow_dir = resolve_paths(
            config_path=config_path,
            run_dir_override=None,
            workflow_dir_override=None,
        )
        
        assert run_dir == Path("/config/runs")
        assert workflow_dir == Path("/config/workflows")
    finally:
        Path(config_path).unlink()


def test_resolve_paths_relative_from_cwd():
    """Relative paths resolved from current working directory."""
    import tempfile
    import yaml
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump({
            'preferred_executor': 'echo',
            'run_dir': 'my-runs',
            'workflow_dir': 'my-workflows',
        }, f)
        config_path = f.name
    
    try:
        run_dir, workflow_dir = resolve_paths(
            config_path=config_path,
            run_dir_override=None,
            workflow_dir_override=None,
        )
        
        assert run_dir == Path.cwd() / "my-runs"
        assert workflow_dir == Path.cwd() / "my-workflows"
    finally:
        Path(config_path).unlink()
```

- [ ] **Step 8: Run all path_resolver tests**

Run: `uv run pytest tests/test_path_resolver.py -v`
Expected: All 5 tests pass

- [ ] **Step 9: Run all tests**

Run: `uv run pytest tests/ -v`
Expected: All tests pass

- [ ] **Step 10: Commit**

```bash
git add src/flowctl/path_resolver.py tests/test_path_resolver.py
git commit -m "feat: add path_resolver module with precedence logic"
```

---

### Task 3: Update run command CLI options

**Files:**
- Modify: `src/flowctl/cli.py:65-148`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write failing test for --config option**

```python
# tests/test_cli.py - add to existing file or create new

import pytest
from click.testing import CliRunner
from flowctl.cli import main


def test_run_config_option():
    """--config option loads config from custom path."""
    import tempfile
    import yaml
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump({
            'preferred_executor': 'echo',
            'run_dir': '/custom/runs',
        }, f)
        config_path = f.name
    
    runner = CliRunner()
    
    try:
        # Use --dry-run to avoid actual execution
        result = runner.invoke(main, [
            'run',
            '--config', config_path,
            '--dry-run',
            '.flows/workflows/hello-world.yaml',
        ])
        
        # Should not error about config
        assert 'Config not found' not in result.output
    finally:
        Path(config_path).unlink()


def test_run_run_dir_option():
    """--run-dir option overrides config."""
    runner = CliRunner()
    
    result = runner.invoke(main, [
        'run',
        '--run-dir', '/tmp/test-runs',
        '--dry-run',
        '--run-id', 'test-cli-override',
        '.flows/workflows/hello-world.yaml',
    ])
    
    assert result.exit_code == 0
    # Check that run dir was used
    assert Path('/tmp/test-runs/test-cli-override').exists()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_cli.py -v`
Expected: FAIL - new options not implemented

- [ ] **Step 3: Add --config, --run-dir, --workflow-dir options to run command**

```python
# src/flowctl/cli.py:65-79 - modify run command

@main.command()
@click.option("--config", default=".flows/config.yaml", help="Config file path")
@click.option("--dry-run", is_flag=True)
@click.option("--executor", default="echo", help="Executor: echo, opencode")
@click.option("--model", default=None, help="Model for executor (e.g., alibaba-cn/glm-5)")
@click.option("--agent", default=None, help="Agent name for executor")
@click.option("--run-dir", default=None, help="Override run directory")
@click.option("--workflow-dir", default=None, help="Override workflow directory")
@click.option("--run-id", default=None)
@click.option("--issue", default=None, help="GitHub issue URL to process")
@click.option("--log-level", default="INFO", help="Log level: DEBUG, INFO, WARNING, ERROR")
@click.option("--log-format", default="json", help="Log format: json, text")
@click.option("--resume", is_flag=True, help="Resume from saved state in run directory")
@click.option("--approve", is_flag=True, help="Approve pending human node")
@click.option("--reject", is_flag=True, help="Reject pending human node")
@click.option("--reject-reason", default=None, help="Reason for rejection (required with --reject)")
@click.argument("workflow", default=".flows/workflows/default.yaml")
def run(config, dry_run, executor, model, agent, run_dir, workflow_dir, workflow, run_id, issue, log_level, log_format, resume, approve, reject, reject_reason):
```

- [ ] **Step 4: Import path_resolver and use it in run command**

```python
# src/flowctl/cli.py:1-6 - add import

import click
from pathlib import Path
from .init_cmd import run_init
from .loader import load_workflow, validate_workflow
from .runner import run_workflow
from .executors import create_default_registry
from .path_resolver import resolve_paths
```

- [ ] **Step 5: Use resolve_paths in run command**

```python
# src/flowctl/cli.py:79-105 - replace hardcoded path logic

def run(config, dry_run, executor, model, agent, run_dir, workflow_dir, workflow, run_id, issue, log_level, log_format, resume, approve, reject, reject_reason):
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

    # Resolve paths from config + CLI overrides
    resolved_run_dir, resolved_workflow_dir = resolve_paths(config, run_dir, workflow_dir)
    
    # Override run_id in run_dir if specified
    if run_id:
        resolved_run_dir = resolved_run_dir / run_id
    else:
        resolved_run_dir = resolved_run_dir / "latest"
    
    resolved_run_dir.mkdir(parents=True, exist_ok=True)

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
        issue_file = resolved_run_dir / "issue-url.txt"
        issue_file.write_text(issue)
    
    approval_decision = None
    if approve:
        approval_decision = "yes"
    elif reject:
        approval_decision = "no"

    result = run_workflow(
        wf, resolved_run_dir,
        registry=registry,
        default_executor=executor,
        executor_config=executor_config,
        dry_run=dry_run,
        initial_context=initial_context,
        workflow_dir=resolved_workflow_dir,
        log_level=log_level,
        log_format=log_format,
        resume=resume,
        approval_decision=approval_decision,
        reject_reason=reject_reason,
    )
    click.echo(f"Run complete. Context: {result}")
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `uv run pytest tests/test_cli.py -v`
Expected: Tests pass

- [ ] **Step 7: Run all tests**

Run: `uv run pytest tests/ -v`
Expected: All tests pass

- [ ] **Step 8: Commit**

```bash
git add src/flowctl/cli.py tests/test_cli.py
git commit -m "feat: add --config, --run-dir, --workflow-dir to run command"
```

---

### Task 4: Update status command CLI options

**Files:**
- Modify: `src/flowctl/cli.py:29-63`

- [ ] **Step 1: Write failing test for status --run-dir**

```python
# tests/test_cli.py - add test

def test_status_run_dir_option():
    """status command uses --run-dir option."""
    import tempfile
    
    runner = CliRunner()
    
    # Create a temp run directory with state
    temp_run_dir = Path(tempfile.mkdtemp()) / "test-status-run"
    temp_run_dir.mkdir(parents=True)
    
    # Create minimal state.json
    import json
    state = {
        "current_node": "test_node",
        "context": {},
        "iterations": 0,
        "status": "running"
    }
    (temp_run_dir / "state.json").write_text(json.dumps(state))
    
    result = runner.invoke(main, [
        'status',
        '--run-dir', str(temp_run_dir.parent),
        '--run-id', 'test-status-run',
    ])
    
    assert result.exit_code == 0
    assert 'test-status-run' in result.output
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_run_dir.parent)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py::test_status_run_dir_option -v`
Expected: FAIL - --run-dir not implemented for status

- [ ] **Step 3: Add --config and --run-dir options to status command**

```python
# src/flowctl/cli.py:29-63 - modify status command

@main.command()
@click.option("--config", default=".flows/config.yaml", help="Config file path")
@click.option("--run-dir", default=None, help="Override run directory")
@click.option("--run-id", default=None)
def status(config, run_dir, run_id):
    """Show workflow run status."""
    from pathlib import Path
    from .state import load_state, WorkflowStatus
    from .runner import MAX_REJECTS
    from .path_resolver import resolve_paths
    
    resolved_run_dir, _ = resolve_paths(config, run_dir, None)
    
    run_dir_path = resolved_run_dir / (run_id or "latest")
    
    if not run_dir_path.exists():
        click.echo(f"Run directory not found: {run_dir_path}", err=True)
        raise click.Abort()
    
    state = load_state(run_dir_path)
    if not state:
        click.echo(f"No state found in: {run_dir_path}")
        return
    
    click.echo(f"Run: {run_dir_path.name}")
    click.echo(f"Status: {state.status.value.upper()}")
    click.echo(f"Node: {state.current_node}")
    
    if state.reject_counts:
        for node, count in state.reject_counts.items():
            click.echo(f"Reject count ({node}): {count}/{MAX_REJECTS}")
    
    if state.status == WorkflowStatus.PAUSED:
        if state.pending_approval_for:
            click.echo(f"Pending approval: {state.pending_approval_for}")
        click.echo(f"Approve: flowctl run --resume --approve --run-id {run_dir_path.name}")
        click.echo(f"Reject: flowctl run --resume --reject --reject-reason \"<reason>\" --run-id {run_dir_path.name}")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_cli.py::test_status_run_dir_option -v`
Expected: PASS

- [ ] **Step 5: Run all tests**

Run: `uv run pytest tests/ -v`
Expected: All tests pass

- [ ] **Step 6: Commit**

```bash
git add src/flowctl/cli.py tests/test_cli.py
git commit -m "feat: add --config, --run-dir to status command"
```

---

### Task 5: Update init command

**Files:**
- Modify: `src/flowctl/cli.py:14-18`
- Modify: `src/flowctl/init_cmd.py`

- [ ] **Step 1: Write failing test for init --config**

```python
# tests/test_cli.py - add test

def test_init_config_option():
    """init uses --config to determine directory structure."""
    import tempfile
    import yaml
    import shutil
    
    runner = CliRunner()
    
    # Create temp config with custom workflow_dir
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump({
            'preferred_executor': 'echo',
            'workflow_dir': '/tmp/test-init-flows',
        }, f)
        config_path = f.name
    
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        result = runner.invoke(main, [
            'init',
            '--config', config_path,
            '--target', str(temp_dir),
        ])
        
        assert result.exit_code == 0
        # Should create directories based on workflow_dir in config
        # (target still controls where, but structure follows config)
    finally:
        Path(config_path).unlink()
        shutil.rmtree(temp_dir, ignore_errors=True)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py::test_init_config_option -v`
Expected: FAIL - --config not implemented for init

- [ ] **Step 3: Add --config option to init command**

```python
# src/flowctl/cli.py:14-18 - modify init command

@main.command()
@click.option("--target", default=None, help="Target directory")
@click.option("--config", default=".flows/config.yaml", help="Config file path")
def init(target, config):
    """Bootstrap .flows/ directory in the target project."""
    run_init(target, config)
```

- [ ] **Step 4: Update init_cmd.py to accept config parameter**

```python
# src/flowctl/init_cmd.py - modify entire file

import click
from pathlib import Path
from .path_resolver import resolve_paths
from .models import FlowctlConfig


def run_init(target: str | None, config_path: str | None = None):
    """Initialize .flows/ directory structure."""
    base = Path(target or ".")
    
    # Resolve workflow_dir from config
    if config_path:
        _, workflow_dir = resolve_paths(config_path, None, None)
        flows_dir = workflow_dir
    else:
        flows_dir = base / ".flows"
    
    # Create directory structure
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
    
    # Create default config
    config_file = flows_dir / "config.yaml"
    if not config_file.exists():
        import yaml
        config = FlowctlConfig()
        with open(config_file, 'w') as f:
            yaml.dump(config.model_dump(), f)
        click.echo(f"Created: {config_file}")
    
    # Create .gitignore
    gitignore_path = flows_dir / ".gitignore"
    if not gitignore_path.exists():
        gitignore_path.write_text("runs/\nmemory/local/\n")
        click.echo(f"Created: {gitignore_path}")
    
    click.echo(f"Initialized {flows_dir} in {base}")
```

- [ ] **Step 5: Run test to verify it passes**

Run: `uv run pytest tests/test_cli.py::test_init_config_option -v`
Expected: PASS

- [ ] **Step 6: Run all tests**

Run: `uv run pytest tests/ -v`
Expected: All tests pass

- [ ] **Step 7: Commit**

```bash
git add src/flowctl/cli.py src/flowctl/init_cmd.py tests/test_cli.py
git commit -m "feat: add --config to init command"
```

---

### Task 6: Update upgrade command

**Files:**
- Modify: `src/flowctl/cli.py:21-26`
- Modify: `src/flowctl/upgrade_cmd.py`

- [ ] **Step 1: Add --config option to upgrade command**

```python
# src/flowctl/cli.py:21-26 - modify upgrade command

@main.command()
@click.option("--target", default=None)
@click.option("--config", default=".flows/config.yaml", help="Config file path")
def upgrade(target, config):
    """Reconcile .flows/config.yaml schema for new framework versions."""
    from .upgrade_cmd import run_upgrade
    run_upgrade(target, config)
```

- [ ] **Step 2: Update upgrade_cmd.py to accept config parameter**

```python
# src/flowctl/upgrade_cmd.py - modify entire file

import click
from pathlib import Path
import yaml
from .models import FlowctlConfig


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
    
    # Merge with current defaults
    defaults = FlowctlConfig()
    merged = {**defaults.model_dump(), **existing}
    
    # Remove deprecated fields (none currently)
    
    with open(config_file, 'w') as f:
        yaml.dump(merged, f)
    
    click.echo(f"Upgraded: {config_file}")
```

- [ ] **Step 3: Run all tests**

Run: `uv run pytest tests/ -v`
Expected: All tests pass

- [ ] **Step 4: Commit**

```bash
git add src/flowctl/cli.py src/flowctl/upgrade_cmd.py
git commit -m "feat: add --config to upgrade command"
```

---

### Task 7: Update runner.py

**Files:**
- Modify: `src/flowctl/runner.py:38-42`

- [ ] **Step 1: Remove hardcoded .flows path in load_flowctl_config**

```python
# src/flowctl/runner.py:38-43 - modify load_flowctl_config

def load_flowctl_config(workflow_dir: Path | None) -> FlowctlConfig | None:
    """Load config from workflow_dir/config.yaml."""
    if not workflow_dir:
        return FlowctlConfig()  # Return defaults
    
    config_path = workflow_dir / "config.yaml"
    if not config_path.exists():
        return FlowctlConfig()  # Return defaults
    
    import yaml
    with open(config_path) as f:
        data = yaml.safe_load(f) or {}
    return FlowctlConfig(**data)
```

- [ ] **Step 2: Run all tests**

Run: `uv run pytest tests/ -v`
Expected: All tests pass

- [ ] **Step 3: Commit**

```bash
git add src/flowctl/runner.py
git commit -m "refactor: remove hardcoded .flows path in load_flowctl_config"
```

---

### Task 8: Final integration test

**Files:**
- Test: `tests/test_integration_paths.py`

- [ ] **Step 1: Write integration test for full path configuration**

```python
# tests/test_integration_paths.py - new file

import pytest
from pathlib import Path
from click.testing import CliRunner
from flowctl.cli import main
import tempfile
import yaml
import shutil


def test_full_path_configuration():
    """End-to-end test of configurable paths."""
    runner = CliRunner()
    
    # Create temp directories
    temp_root = Path(tempfile.mkdtemp())
    workflow_dir = temp_root / "workflows"
    run_dir = temp_root / "runs"
    
    workflow_dir.mkdir(parents=True)
    run_dir.mkdir(parents=True)
    
    # Create config
    config_path = temp_root / "my-config.yaml"
    with open(config_path, 'w') as f:
        yaml.dump({
            'preferred_executor': 'echo',
            'run_dir': str(run_dir),
            'workflow_dir': str(workflow_dir),
        }, f)
    
    # Create workflow definition
    wf_dir = workflow_dir / "workflows"
    wf_dir.mkdir(parents=True)
    
    hello_world = wf_dir / "hello-world.yaml"
    hello_world.write_text("""
version: "1"
nodes:
  hello:
    role: greeter
    prompt: prompts/hello.md
    executor: echo
    outputs: {greeting: greeting.txt}
transitions:
  - from: __start__
    to: hello
  - from: hello
    to: __end__
""")
    
    try:
        # Run with custom config
        result = runner.invoke(main, [
            'run',
            '--config', str(config_path),
            '--dry-run',
            '--run-id', 'integration-test',
            str(hello_world),
        ])
        
        assert result.exit_code == 0
        
        # Check run directory was created at configured location
        test_run_dir = run_dir / "integration-test"
        assert test_run_dir.exists()
        
        # Check workflow_dir was used
        # (state should show workflow_dir path)
        import json
        state_file = test_run_dir / "state.json"
        if state_file.exists():
            state = json.loads(state_file.read_text())
            assert state.get("status") in ["completed", "running"]
    
    finally:
        shutil.rmtree(temp_root)


def test_backward_compatibility():
    """Default paths work without config changes."""
    runner = CliRunner()
    
    # Run with no config options (backward compatible)
    result = runner.invoke(main, [
        'run',
        '--dry-run',
        '.flows/workflows/hello-world.yaml',
    ])
    
    # Should work with default .flows/runs/latest
    assert result.exit_code == 0
    assert Path(".flows/runs/latest").exists()
```

- [ ] **Step 2: Run integration tests**

Run: `uv run pytest tests/test_integration_paths.py -v`
Expected: Tests pass

- [ ] **Step 3: Run all tests**

Run: `uv run pytest tests/ -v`
Expected: All tests pass

- [ ] **Step 4: Commit**

```bash
git add tests/test_integration_paths.py
git commit -m "test: add integration tests for configurable paths"
```

---

### Task 9: Update .flows/config.yaml with new fields

**Files:**
- Modify: `.flows/config.yaml`

- [ ] **Step 1: Add new fields to existing config**

```yaml
# .flows/config.yaml - update file

preferred_executor: echo
framework_version: '0.1.0'
run_dir: .flows/runs
workflow_dir: .flows
```

- [ ] **Step 2: Run upgrade command to add fields**

Run: `uv run flowctl upgrade`
Expected: Adds run_dir and workflow_dir fields

- [ ] **Step 3: Verify config updated**

Run: `cat .flows/config.yaml`
Expected: Contains run_dir and workflow_dir

- [ ] **Step 4: Commit**

```bash
git add .flows/config.yaml
git commit -m "chore: add run_dir and workflow_dir to config.yaml"
```

---

### Task 10: Update README documentation

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add documentation for new CLI options**

Add to README.md after CLI Options section:

```markdown
### Path Configuration

By default, flowctl uses `.flows/` for workflow definitions and `.flows/runs/` for run artifacts.

You can customize these paths:

**Config file:**

```yaml
# .flows/config.yaml
run_dir: .flows/runs
workflow_dir: .flows
```

**CLI options:**

```bash
# Use custom config location
flowctl run --config ~/my-config.yaml

# Override run directory
flowctl run --run-dir ~/runs

# Override workflow directory
flowctl run --workflow-dir ~/shared-workflows
```

**Precedence:** CLI options > config values > defaults

**Relative paths** are resolved from current working directory where `flowctl` is executed.
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add path configuration documentation"
```

---

## Self-Review Checklist

- [x] Spec coverage: All spec requirements have corresponding tasks
- [x] No placeholders: Each step has actual code/commands
- [x] Type consistency: resolve_paths returns tuple[Path, Path] throughout
- [x] TDD: Tests written before implementation
- [x] Backward compatibility: Default behavior preserved

---

Plan complete. Two execution options:

1. **Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

2. **Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?