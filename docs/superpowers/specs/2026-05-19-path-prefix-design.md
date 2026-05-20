# Path Prefix for Input/Output File Resolution Design

## Problem

Currently, input/output file paths in workflow YAML don't indicate which directory they should be resolved from:

```yaml
inputs:
  clarify: clarify.md                    # Which directory?
  memory_architect: memory/architect.md  # Which directory?
  repo_root: repo-root.txt               # Which directory?
```

PromptProcessor generates ambiguous prompts:
```markdown
## Input

- clarify: Read from clarify.md
- memory_architect: Read from memory/architect.md
```

Agent doesn't know if `clarify.md` is in `run_dir`, `workflow_dir`, or `repo_dir`.

Additionally, outputs always write to `run_dir`, preventing nodes from writing to memory files or target repo.

## Solution

Add path prefix (`run:`, `workflow:`, `repo:`) to input/output file paths in YAML. PromptProcessor resolves paths and generates prompts with absolute path annotations.

**Key decisions:**
- Prefixes: `run:`, `workflow:`, `repo:`
- Backward compatible: no prefix defaults to `run:`
- `repo_dir` configured via CLI (`--repo-dir`) + config file
- Outputs use same prefixes (symmetric design)
- No file copying — prompt shows absolute paths, agent reads/writes directly
- Prompt format: relative filename + absolute path annotation

## Prefix Definitions

| Prefix | Directory | Source | Example YAML | Example Path |
|--------|-----------|--------|--------------|--------------|
| `run:` | `.flows/runs/<run-id>` | Runner creates | `run:clarify.md` | `/home/user/.flows/runs/issue-26/clarify.md` |
| `workflow:` | `.flows/` (or custom) | CLI `--workflow-dir` or config | `workflow:memory/architect.md` | `/home/user/.flows/memory/architect.md` |
| `repo:` | Target repo root | CLI `--repo-dir` or config `repo_dir` | `repo:ARCHITECTURE.md` | `/home/user/code/my-project/ARCHITECTURE.md` |

**Default behavior:** No prefix → `run:` (backward compatible)

**YAML examples:**

```yaml
inputs:
  clarify: clarify.md                    # Implicit: run:clarify.md
  memory_ba: workflow:memory/ba.md       # Explicit: workflow_dir
  repo_root: repo:repo-root.txt          # Explicit: repo_dir
  architecture: repo:ARCHITECTURE.md     # Explicit: repo_dir

outputs:
  design_md: design.md                   # Implicit: run:design.md
  memory_update: workflow:memory/ba.md   # Explicit: write to workflow_dir
```

## Architecture Changes

### ExecutorInput Enhancement

**Current:**

```python
@dataclass
class ExecutorInput:
    role: str
    prompt: str
    run_dir: Path
    workflow_dir: Optional[Path] = None
    inputs: dict[str, str] = field(default_factory=dict)
    outputs: dict[str, str] = field(default_factory=dict)
```

**Enhanced:**

```python
@dataclass
class ExecutorInput:
    role: str
    prompt: str
    run_dir: Path
    workflow_dir: Optional[Path] = None
    repo_dir: Optional[Path] = None  # NEW
    inputs: dict[str, str] = field(default_factory=dict)
    outputs: dict[str, str] = field(default_factory=dict)
```

### PromptProcessor Path Resolution

**New methods:**

```python
def _parse_prefix(self, filename: str) -> tuple[str, str]:
    """Extract prefix and relative path from filename.
    
    Returns: (prefix, relative_path)
    """
    if filename.startswith("workflow:"):
        return "workflow", filename[9:]
    elif filename.startswith("repo:"):
        return "repo", filename[5:]
    elif filename.startswith("run:"):
        return "run", filename[4:]
    else:
        return "run", filename  # Default: backward compatible

def _resolve_path(self, prefix: str, rel_path: str, context: dict) -> Path:
    """Resolve relative path to absolute path based on prefix."""
    if prefix == "workflow":
        base_dir = context.get("workflow_dir")
    elif prefix == "repo":
        base_dir = context.get("repo_dir")
    else:  # run
        base_dir = context.get("run_dir")
    
    if base_dir:
        return base_dir / rel_path
    return Path(rel_path)

def _generate_input_section(self, inputs: dict[str, str], context: dict) -> str:
    """Generate Input section with absolute paths."""
    if not inputs:
        return ""
    
    lines = ["## Input", ""]
    for key, filename in inputs.items():
        prefix, rel_path = self._parse_prefix(filename)
        abs_path = self._resolve_path(prefix, rel_path, context)
        lines.append(f"- {key}: Read from {rel_path} ({prefix}_dir: {abs_path})")
    
    return "\n".join(lines)

def _generate_output_section(self, outputs: dict[str, str], context: dict) -> str:
    """Generate Output section with absolute paths."""
    if not outputs:
        return ""
    
    lines = ["## Output", ""]
    for key, filename in outputs.items():
        prefix, rel_path = self._parse_prefix(filename)
        abs_path = self._resolve_path(prefix, rel_path, context)
        lines.append(f"- {key}: Write to {rel_path} ({prefix}_dir: {abs_path})")
    
    return "\n".join(lines)
```

**Generated prompt example:**

```markdown
## Input

- clarify: Read from clarify.md (run_dir: /home/user/.flows/runs/issue-26)
- memory_ba: Read from memory/ba.md (workflow_dir: /home/user/.flows)
- architecture: Read from ARCHITECTURE.md (repo_dir: /home/user/code/my-project)

## Output

- design_md: Write to design.md (run_dir: /home/user/.flows/runs/issue-26)
- memory_update: Write to memory/ba.md (workflow_dir: /home/user/.flows)
```

### CLI and Config Changes

**Config model:**

```python
class FlowctlConfig(BaseModel):
    preferred_executor: str = "echo"
    framework_version: str = "0.1.0"
    run_dir: str = ".flows/runs"
    workflow_dir: str = ".flows"
    repo_dir: Optional[str] = None  # NEW
```

**CLI argument:**

```python
@click.option('--repo-dir', type=click.Path(), help='Target repo directory')
def run(workflow, repo_dir, ...):
    # Resolve: CLI > config > None
    if repo_dir:
        resolved_repo_dir = Path(repo_dir)
    elif config and config.repo_dir:
        resolved_repo_dir = Path(config.repo_dir)
    else:
        resolved_repo_dir = None
    
    result = run_workflow(wf, run_dir, repo_dir=resolved_repo_dir, ...)
```

**Runner integration:**

```python
def run_workflow(
    workflow: WorkflowDef,
    run_dir: Path,
    repo_dir: Optional[Path] = None,  # NEW
    ...
):
    process_context = {
        "node": node_def,
        "run_dir": run_dir,
        "workflow_dir": workflow_dir,
        "repo_dir": repo_dir,  # NEW
    }
    processed_prompt = processor.process(prompt_content, process_context)
    
    inp = ExecutorInput(
        run_dir=run_dir,
        workflow_dir=workflow_dir,
        repo_dir=repo_dir,  # NEW
        inputs=node_def.inputs,
        outputs=node_def.outputs,
    )
```

**Usage examples:**

```bash
# CLI override
flowctl run workflow.yaml --repo-dir /home/user/code/my-project

# Config file (.flows/config.yaml)
repo_dir: /home/user/code/my-project

# Both (CLI wins)
flowctl run workflow.yaml --repo-dir /other/project
# Uses /other/project
```

### Executor Changes

**OpencodeAdapter output resolution:**

```python
def _resolve_output_path(self, filename: str, inp: ExecutorInput) -> Path:
    """Resolve output file path based on prefix."""
    prefix, rel_path = self._parse_prefix(filename)
    
    if prefix == "workflow":
        base_dir = inp.workflow_dir
    elif prefix == "repo":
        base_dir = inp.repo_dir
    else:
        base_dir = inp.run_dir
    
    return base_dir / rel_path if base_dir else Path(rel_path)

def execute(self, inp: ExecutorInput) -> ExecutorResult:
    outputs = {}
    for key, filename in inp.outputs.items():
        artifact_path = self._resolve_output_path(filename, inp)
        if artifact_path.exists():
            outputs[key] = artifact_path.read_text()
```

**EchoAdapter dry-run visibility:**

```python
def execute(self, inp: ExecutorInput) -> ExecutorResult:
    stdout_lines = ["PROCESSED PROMPT", inp.prompt]
    
    stdout_lines.append("\n=== Resolved Paths ===")
    for key, filename in inp.inputs.items():
        prefix, rel_path = self._parse_prefix(filename)
        resolved = self._resolve_path(prefix, rel_path, inp)
        stdout_lines.append(f"Input {key}: {rel_path} → {resolved}")
    
    for key, filename in inp.outputs.items():
        prefix, rel_path = self._parse_prefix(filename)
        resolved = self._resolve_path(prefix, rel_path, inp)
        stdout_lines.append(f"Output {key}: {rel_path} → {resolved}")
```

### Artifact Validation

Validator must resolve paths before checking existence:

```python
# src/flowctl/artifact_validator.py

def validate_artifacts(outputs: dict[str, str], run_dir: Path, 
                       workflow_dir: Path = None, repo_dir: Path = None) -> list[str]:
    """Validate output artifacts exist at resolved paths."""
    errors = []
    for key, filename in outputs.items():
        prefix, rel_path = parse_prefix(filename)
        resolved_path = resolve_path(prefix, rel_path, run_dir, workflow_dir, repo_dir)
        
        if not resolved_path.exists():
            errors.append(f"Missing output: {key} expected at {resolved_path}")
    
    return errors
```

## Testing

### Unit Tests (Processor)

```python
def test_parse_prefix_run():
    processor = PromptProcessor()
    prefix, path = processor._parse_prefix("run:clarify.md")
    assert prefix == "run"
    assert path == "clarify.md"

def test_parse_prefix_workflow():
    processor = PromptProcessor()
    prefix, path = processor._parse_prefix("workflow:memory/architect.md")
    assert prefix == "workflow"
    assert path == "memory/architect.md"

def test_parse_prefix_repo():
    processor = PromptProcessor()
    prefix, path = processor._parse_prefix("repo:ARCHITECTURE.md")
    assert prefix == "repo"
    assert path == "ARCHITECTURE.md"

def test_parse_prefix_default():
    processor = PromptProcessor()
    prefix, path = processor._parse_prefix("clarify.md")
    assert prefix == "run"
    assert path == "clarify.md"

def test_generate_input_with_prefix():
    processor = PromptProcessor()
    node = Node(role="dev", inputs={"arch": "workflow:memory/architect.md"})
    context = {
        "node": node,
        "workflow_dir": Path("/flows"),
        "run_dir": Path("/runs/test"),
    }
    result = processor.process("# Task", context)
    assert "Read from memory/architect.md (workflow_dir: /flows/memory/architect.md)" in result
```

### Integration Tests (Runner + Executor)

```python
def test_runner_passes_repo_dir():
    wf = WorkflowDef(...)
    run_dir = tmp_path / "run"
    repo_dir = tmp_path / "repo"
    
    result = run_workflow(wf, run_dir, repo_dir=repo_dir, dry_run=True)
    
    # Verify repo_dir in prompt
    assert "repo_dir:" in result.stdout

def test_output_writes_to_workflow_dir():
    wf = WorkflowDef(
        nodes={
            "node": Node(
                outputs={"memory_update": "workflow:memory/ba.md"}
            )
        }
    )
    
    workflow_dir = tmp_path / "flows"
    (workflow_dir / "memory").mkdir()
    
    # Run workflow, check output written to workflow_dir/memory/ba.md
```

### SDET Dry-Run Workflow

```yaml
# tests/sdet/workflows/path-prefix-test.yaml

nodes:
  test_run_prefix:
    role: dev
    inputs: {file: run:test.md}
    outputs: {result: run:result.md}
  
  test_workflow_prefix:
    role: dev
    inputs: {memory: workflow:memory/test.md}
    outputs: {update: workflow:memory/test.md}
  
  test_repo_prefix:
    role: dev
    inputs: {arch: repo:ARCHITECTURE.md}
    outputs: {change: repo:src/test.py}
  
  test_default_prefix:
    role: dev
    inputs: {file: test.md}  # No prefix
    outputs: {result: result.md}
```

**Test command:**

```bash
flowctl run --dry-run \
  --workflow-dir tests/sdet \
  --repo-dir /tmp/test-repo \
  tests/sdet/workflows/path-prefix-test.yaml
```

## Files to Modify

1. `src/flowctl/models.py` — Add `repo_dir` to `FlowctlConfig`
2. `src/flowctl/executors/base.py` — Add `repo_dir` to `ExecutorInput`
3. `src/flowctl/processor.py` — Add `_parse_prefix`, `_resolve_path`, update section generators
4. `src/flowctl/runner.py` — Receive `repo_dir`, pass to process_context and ExecutorInput
5. `src/flowctl/cli.py` — Add `--repo-dir` argument
6. `src/flowctl/executors/opencode.py` — Resolve output paths
7. `src/flowctl/executors/echo.py` — Show resolved paths in dry-run
8. `src/flowctl/artifact_validator.py` — Resolve paths before validation
9. `tests/test_processor.py` — Add prefix parsing/resolution tests
10. `tests/test_runner.py` — Add repo_dir integration tests

## Benefits

1. **Explicit intent:** YAML shows where files come from/go to
2. **Agent clarity:** Prompt includes absolute paths, no ambiguity
3. **Backward compatible:** No prefix defaults to current behavior
4. **Cross-repo support:** `repo:` enables workflows against external repos
5. **Memory persistence:** `workflow:` outputs write to memory files
6. **Testable:** Dry-run shows resolved paths for SDET verification

## Related

- Issue: https://github.com/ccijunk/ai-workflow/issues/29
- SDET architecture: docs/sdet/TEST-ARCHITECTURE.md
- Current processor: src/flowctl/processor.py