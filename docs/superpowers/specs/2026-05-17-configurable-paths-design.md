# Design: Configurable run_dir and workflow_dir Paths

**Issue:** https://github.com/ccijunk/ai-workflow/issues/20
**Date:** 2026-05-17

## Problem

Currently `run_dir` (`.flows/runs/`) and `workflow_dir` (`.flows/`) are hardcoded paths. Users cannot customize these locations for different scenarios:
- Separate run storage outside project
- Shared workflow definitions across projects
- CI/CD environment flexibility
- Custom project structures

## Solution

Add configurable paths with precedence hierarchy: CLI options > config file > defaults.

## Design

### 1. Config Model Changes

Add two fields to `FlowctlConfig`:

```python
class FlowctlConfig(BaseModel):
    preferred_executor: str = "echo"
    framework_version: str = "0.1.0"
    run_dir: str = ".flows/runs"
    workflow_dir: str = ".flows"
```

**Config file example:**

```yaml
preferred_executor: echo
framework_version: '0.1.0'
run_dir: .flows/runs
workflow_dir: .flows
```

Default values match current behavior for backward compatibility.

### 2. CLI Changes

Add `--config` option to all commands. Add `--run-dir` and `--workflow-dir` to commands that need them.

**run command:**

```python
@click.option("--config", default=".flows/config.yaml", help="Config file path")
@click.option("--run-dir", default=None, help="Override run directory")
@click.option("--workflow-dir", default=None, help="Override workflow directory")
def run(config, run_dir, workflow_dir, ...):
```

**status command:**

```python
@click.option("--config", default=".flows/config.yaml", help="Config file path")
@click.option("--run-dir", default=None, help="Override run directory")
def status(config, run_dir, ...):
```

**init and upgrade commands:**

- Add `--config` option
- Keep existing `--target` option for project root

**Precedence logic:**

1. Load config from `--config` path (or default `.flows/config.yaml`)
2. CLI options override config values
3. Config values override hardcoded defaults

**Usage examples:**

```bash
# Default behavior (backward compatible)
flowctl run

# Custom config location
flowctl run --config ~/my-config.yaml

# Override run_dir only
flowctl run --run-dir ~/runs

# Override both from CLI
flowctl run --config ~/my-config.yaml --run-dir ~/runs --workflow-dir ~/shared
```

### 3. Path Resolution

**Resolution logic:**

```python
def resolve_paths(config_path: str, run_dir_override: str | None, workflow_dir_override: str | None) -> tuple[Path, Path]:
    """Resolve run_dir and workflow_dir from config + CLI overrides."""
    
    config = load_config(config_path)  # or defaults if not found
    
    run_dir = run_dir_override or config.run_dir or ".flows/runs"
    workflow_dir = workflow_dir_override or config.workflow_dir or ".flows"
    
    run_dir_path = Path(run_dir)
    workflow_dir_path = Path(workflow_dir)
    
    if not run_dir_path.is_absolute():
        run_dir_path = Path.cwd() / run_dir_path
    if not workflow_dir_path.is_absolute():
        workflow_dir_path = Path.cwd() / workflow_dir_path
    
    return run_dir_path, workflow_dir_path
```

**Files to modify:**

| File | Change |
|------|--------|
| `src/flowctl/cli.py` | Add `--config`, `--run-dir`, `--workflow-dir` options; resolve paths before passing to runner |
| `src/flowctl/models.py` | Add `run_dir`, `workflow_dir` fields to `FlowctlConfig` |
| `src/flowctl/runner.py` | Remove hardcoded path logic; receive resolved paths from CLI |
| `src/flowctl/init_cmd.py` | Use configurable workflow_dir for directory creation |
| `src/flowctl/upgrade_cmd.py` | Use configurable config path |

### 4. Backward Compatibility

- Default config path: `.flows/config.yaml` (unchanged)
- Default run_dir: `.flows/runs` (unchanged)
- Default workflow_dir: `.flows` (unchanged)
- If config file missing, defaults used (current behavior)
- Existing `--target` option for `init`/`upgrade` still works

### 5. Edge Cases

1. **Config file not found:**
   - Use hardcoded defaults, no error
   - Log warning: "Config not found at {path}, using defaults"

2. **Relative path resolution:**
   - Resolve from `$PWD` where `flowctl` executed
   - Example: config has `run_dir: runs`, executed from `/home/project/` → `/home/project/runs`

3. **Circular dependency (config inside workflow_dir):**
   - `--config` option breaks the circle
   - Default: `.flows/config.yaml` (inside default workflow_dir)
   - If user moves workflow_dir, they must also move config or use `--config`

4. **init command with custom paths:**
   - `flowctl init --config ~/my-config.yaml` creates directories at configured locations
   - Or `flowctl init --target ~/project` creates `.flows/` at target (existing behavior)

5. **status command without run_id:**
   - Uses `run_dir / "latest"` from resolved path

## Files Changed Summary

| File | Changes |
|------|---------|
| `src/flowctl/models.py` | Add `run_dir`, `workflow_dir` to `FlowctlConfig` |
| `src/flowctl/cli.py` | Add `--config`, `--run-dir`, `--workflow-dir`; resolve paths |
| `src/flowctl/runner.py` | Remove hardcoded path logic |
| `src/flowctl/init_cmd.py` | Use configurable workflow_dir |
| `src/flowctl/upgrade_cmd.py` | Use configurable config path |

## Test Cases

1. Default paths work (backward compatibility)
2. Config file paths work
3. CLI override paths work
4. CLI overrides config values
5. Absolute paths work
6. Relative paths resolved from $PWD
7. Config file not found uses defaults
8. init creates directories at configured locations
9. status finds runs at configured run_dir