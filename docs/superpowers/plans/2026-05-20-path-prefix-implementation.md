# Path Prefix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add path prefix support (`run:`, `workflow:`, `repo:`) for input/output file resolution in workflow YAML.

**Architecture:** Extend FlowctlConfig with `repo_dir`, add prefix parsing to PromptProcessor, update executors to resolve paths, and enhance CLI with `--repo-dir` option. All changes maintain backward compatibility.

**Tech Stack:** Python 3.12, Pydantic, Click, pathlib

---

## File Structure

**Create:**
- None (all changes to existing files)

**Modify:**
- `src/flowctl/models.py` — Add `repo_dir` field to `FlowctlConfig`
- `src/flowctl/executors/base.py` — Add `repo_dir` field to `ExecutorInput`
- `src/flowctl/processor.py` — Add `_parse_prefix()`, `_resolve_path()`, update section generators
- `src/flowctl/path_resolver.py` — Add `repo_dir` resolution
- `src/flowctl/cli.py` — Add `--repo-dir` option, pass to runner
- `src/flowctl/runner.py` — Pass `repo_dir` to process_context and ExecutorInput
- `src/flowctl/executors/opencode.py` — Resolve output paths with prefixes
- `src/flowctl/executors/echo.py` — Show resolved paths in dry-run output
- `src/flowctl/artifact_validator.py` — Resolve paths before validation
- `tests/test_processor.py` — Add prefix parsing/resolution tests
- `tests/test_path_resolver.py` — Add repo_dir resolution tests

---

### Task 1: Add repo_dir to FlowctlConfig

**Files:**
- Modify: `src/flowctl/models.py:5-10`

- [ ] **Step 1: Add repo_dir field to FlowctlConfig**

```python
class FlowctlConfig(BaseModel):
    preferred_executor: str = "echo"
    framework_version: str = "0.1.0"
    run_dir: str = ".flows/runs"
    workflow_dir: str = ".flows"
    repo_dir: Optional[str] = None
```

- [ ] **Step 2: Run tests to verify no regression**

Run: `pytest tests/test_models.py -v` (if exists) or `pytest tests/ -v -k "config"`
Expected: All existing tests pass

- [ ] **Step 3: Commit**

```bash
git add src/flowctl/models.py
git commit -m "feat: add repo_dir to FlowctlConfig"
```

---

### Task 2: Add repo_dir to ExecutorInput

**Files:**
- Modify: `src/flowctl/executors/base.py:9-19`

- [ ] **Step 1: Add repo_dir field to ExecutorInput**

```python
@dataclass
class ExecutorInput:
    role: str
    prompt: str
    run_dir: Path
    prompt_path: Optional[str] = None
    skill_paths: list[str] = field(default_factory=list)
    inputs: dict[str, str] = field(default_factory=dict)
    outputs: dict[str, str] = field(default_factory=dict)
    workflow_dir: Optional[Path] = None
    repo_dir: Optional[Path] = None
    node: Optional[Node] = None
```

- [ ] **Step 2: Run tests to verify no regression**

Run: `pytest tests/ -v`
Expected: All existing tests pass

- [ ] **Step 3: Commit**

```bash
git add src/flowctl/executors/base.py
git commit -m "feat: add repo_dir to ExecutorInput"
```

---

### Task 3: Add prefix parsing to PromptProcessor

**Files:**
- Modify: `src/flowctl/processor.py:25-92`

- [ ] **Step 1: Write failing tests for _parse_prefix and _resolve_path**

Add to `tests/test_processor.py`:

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

def test_resolve_path_workflow():
    processor = PromptProcessor()
    context = {
        "workflow_dir": Path("/home/user/.flows"),
        "run_dir": Path("/home/user/.flows/runs/test"),
    }
    abs_path = processor._resolve_path("workflow", "memory/ba.md", context)
    assert abs_path == Path("/home/user/.flows/memory/ba.md")

def test_resolve_path_repo():
    processor = PromptProcessor()
    context = {
        "repo_dir": Path("/home/user/code/my-project"),
        "run_dir": Path("/home/user/.flows/runs/test"),
    }
    abs_path = processor._resolve_path("repo", "ARCHITECTURE.md", context)
    assert abs_path == Path("/home/user/code/my-project/ARCHITECTURE.md")

def test_resolve_path_run():
    processor = PromptProcessor()
    context = {
        "run_dir": Path("/home/user/.flows/runs/test"),
    }
    abs_path = processor._resolve_path("run", "clarify.md", context)
    assert abs_path == Path("/home/user/.flows/runs/test/clarify.md")

def test_resolve_path_missing_dir():
    processor = PromptProcessor()
    context = {
        "run_dir": Path("/home/user/.flows/runs/test"),
    }
    abs_path = processor._resolve_path("workflow", "memory/ba.md", context)
    assert abs_path == Path("memory/ba.md")

def test_generate_input_with_prefix():
    processor = PromptProcessor()
    node = Node(
        role="dev",
        prompt="test.md",
        inputs={"arch": "workflow:memory/architect.md"},
        outputs={},
    )
    context = {
        "node": node,
        "workflow_dir": Path("/flows"),
        "run_dir": Path("/runs/test"),
    }
    result = processor.process("# Task", context)
    assert "Read from memory/architect.md (workflow_dir: /flows/memory/architect.md)" in result

def test_generate_output_with_prefix():
    processor = PromptProcessor()
    node = Node(
        role="dev",
        prompt="test.md",
        inputs={},
        outputs={"memory_update": "workflow:memory/ba.md"},
    )
    context = {
        "node": node,
        "workflow_dir": Path("/flows"),
        "run_dir": Path("/runs/test"),
    }
    result = processor.process("# Task", context)
    assert "Write to memory/ba.md (workflow_dir: /flows/memory/ba.md)" in result
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_processor.py::test_parse_prefix_run -v`
Expected: FAIL with "AttributeError: 'PromptProcessor' object has no attribute '_parse_prefix'"

- [ ] **Step 3: Implement _parse_prefix method**

Add to `src/flowctl/processor.py` after line 22:

```python
    def _parse_prefix(self, filename: str) -> tuple[str, str]:
        """Extract prefix and relative path from filename.
        
        Args:
            filename: Filename with optional prefix (e.g., "run:file.md", "workflow:mem/ba.md")
            
        Returns:
            Tuple of (prefix, relative_path)
            prefix is one of: "run", "workflow", "repo"
        """
        if filename.startswith("workflow:"):
            return "workflow", filename[9:]
        elif filename.startswith("repo:"):
            return "repo", filename[5:]
        elif filename.startswith("run:"):
            return "run", filename[4:]
        else:
            return "run", filename
```

- [ ] **Step 4: Implement _resolve_path method**

Add after `_parse_prefix`:

```python
    def _resolve_path(self, prefix: str, rel_path: str, context: dict) -> Path:
        """Resolve relative path to absolute path based on prefix.
        
        Args:
            prefix: One of "run", "workflow", "repo"
            rel_path: Relative path from the prefix directory
            context: Context dict with 'run_dir', 'workflow_dir', 'repo_dir'
            
        Returns:
            Resolved absolute Path, or relative Path if base dir not available
        """
        if prefix == "workflow":
            base_dir = context.get("workflow_dir")
        elif prefix == "repo":
            base_dir = context.get("repo_dir")
        else:
            base_dir = context.get("run_dir")
        
        if base_dir:
            return base_dir / rel_path
        return Path(rel_path)
```

- [ ] **Step 5: Update _generate_input_section to use prefix resolution**

Replace `_generate_input_section` method (lines 74-82):

```python
    def _generate_input_section(self, inputs: dict[str, str], context: dict) -> str:
        if not inputs:
            return ""
        
        lines = ["## Input", ""]
        for key, filename in inputs.items():
            prefix, rel_path = self._parse_prefix(filename)
            abs_path = self._resolve_path(prefix, rel_path, context)
            lines.append(f"- {key}: Read from {rel_path} ({prefix}_dir: {abs_path})")
        
        return "\n".join(lines)
```

- [ ] **Step 6: Update _generate_output_section to use prefix resolution**

Replace `_generate_output_section` method (lines 84-92):

```python
    def _generate_output_section(self, outputs: dict[str, str], context: dict) -> str:
        if not outputs:
            return ""
        
        lines = ["## Output", ""]
        for key, filename in outputs.items():
            prefix, rel_path = self._parse_prefix(filename)
            abs_path = self._resolve_path(prefix, rel_path, context)
            lines.append(f"- {key}: Write to {rel_path} ({prefix}_dir: {abs_path})")
        
        return "\n".join(lines)
```

- [ ] **Step 7: Update process method to pass context to section generators**

Update `process` method to pass context to generators. Replace lines 39-42:

```python
        try:
            cleaned = self._remove_existing_sections(content)
            input_section = self._generate_input_section(node.inputs, context)
            output_section = self._generate_output_section(node.outputs, context)
```

- [ ] **Step 8: Run tests to verify they pass**

Run: `pytest tests/test_processor.py -v`
Expected: All tests pass

- [ ] **Step 9: Commit**

```bash
git add src/flowctl/processor.py tests/test_processor.py
git commit -m "feat: add path prefix parsing to PromptProcessor"
```

---

### Task 4: Add repo_dir resolution to path_resolver

**Files:**
- Modify: `src/flowctl/path_resolver.py:1-39`

- [ ] **Step 1: Write failing test for repo_dir resolution**

Add to `tests/test_path_resolver.py` (create if doesn't exist):

```python
import pytest
from pathlib import Path
from flowctl.path_resolver import resolve_paths


def test_resolve_paths_with_repo_dir_cli():
    """CLI --repo-dir should override config."""
    run_dir, workflow_dir, repo_dir = resolve_paths(
        ".flows/config.yaml", None, None, repo_dir_override="/tmp/my-repo"
    )
    assert repo_dir == Path("/tmp/my-repo")


def test_resolve_paths_with_repo_dir_config(tmp_path):
    """Config repo_dir should be used if no CLI override."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("repo_dir: /tmp/config-repo")
    
    run_dir, workflow_dir, repo_dir = resolve_paths(
        str(config_file), None, None, repo_dir_override=None
    )
    assert repo_dir == Path("/tmp/config-repo")


def test_resolve_paths_repo_dir_none_without_config():
    """repo_dir should be None if not in config or CLI."""
    run_dir, workflow_dir, repo_dir = resolve_paths(
        ".flows/nonexistent.yaml", None, None, repo_dir_override=None
    )
    assert repo_dir is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_path_resolver.py::test_resolve_paths_with_repo_dir_cli -v`
Expected: FAIL with "ValueError: too many values to unpack"

- [ ] **Step 3: Update resolve_paths to return repo_dir**

Replace `resolve_paths` function in `src/flowctl/path_resolver.py`:

```python
from pathlib import Path
from .models import FlowctlConfig


def resolve_paths(
    config_path: str,
    run_dir_override: str | None,
    workflow_dir_override: str | None,
    repo_dir_override: str | None = None,
) -> tuple[Path, Path, Path | None]:
    """Resolve run_dir, workflow_dir, and repo_dir from config + CLI overrides.
    
    Precedence: CLI > config > defaults
    
    Returns:
        Tuple of (run_dir, workflow_dir, repo_dir or None)
    """
    config = _load_config(config_path)
    
    run_dir = run_dir_override or config.run_dir or ".flows/runs"
    workflow_dir = workflow_dir_override or config.workflow_dir or ".flows"
    repo_dir = repo_dir_override or config.repo_dir
    
    run_dir_path = Path(run_dir)
    workflow_dir_path = Path(workflow_dir)
    
    if not run_dir_path.is_absolute():
        run_dir_path = Path.cwd() / run_dir_path
    if not workflow_dir_path.is_absolute():
        workflow_dir_path = Path.cwd() / workflow_dir_path
    
    repo_dir_path = None
    if repo_dir:
        repo_dir_path = Path(repo_dir)
        if not repo_dir_path.is_absolute():
            repo_dir_path = Path.cwd() / repo_dir_path
    
    return run_dir_path, workflow_dir_path, repo_dir_path
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_path_resolver.py -v`
Expected: All tests pass

- [ ] **Step 5: Commit**

```bash
git add src/flowctl/path_resolver.py tests/test_path_resolver.py
git commit -m "feat: add repo_dir resolution to path_resolver"
```

---

### Task 5: Add --repo-dir CLI option

**Files:**
- Modify: `src/flowctl/cli.py:71-164`

- [ ] **Step 1: Add --repo-dir option to run command**

Add after line 78 in `src/flowctl/cli.py`:

```python
@click.option("--repo-dir", default=None, help="Target repository directory")
```

Add `repo_dir` parameter to function signature at line 88:

```python
def run(config, dry_run, executor, model, agent, run_dir, workflow_dir, repo_dir, workflow, run_id, issue, log_level, log_format, resume, approve, reject, reject_reason):
```

- [ ] **Step 2: Update resolve_paths call to pass repo_dir**

Replace line 114:

```python
    resolved_run_dir, resolved_workflow_dir, resolved_repo_dir = resolve_paths(config, run_dir, workflow_dir, repo_dir)
```

- [ ] **Step 3: Pass repo_dir to run_workflow**

Add `repo_dir=resolved_repo_dir` to run_workflow call at line 151:

```python
    result = run_workflow(
        wf, resolved_run_dir,
        registry=registry,
        default_executor=executor,
        executor_config=executor_config,
        dry_run=dry_run,
        initial_context=initial_context,
        workflow_dir=resolved_workflow_dir,
        repo_dir=resolved_repo_dir,
        log_level=log_level,
        log_format=log_format,
        resume=resume,
        approval_decision=approval_decision,
        reject_reason=reject_reason,
    )
```

- [ ] **Step 4: Run tests to verify no regression**

Run: `pytest tests/ -v`
Expected: All existing tests pass

- [ ] **Step 5: Commit**

```bash
git add src/flowctl/cli.py
git commit -m "feat: add --repo-dir CLI option"
```

---

### Task 6: Pass repo_dir through runner

**Files:**
- Modify: `src/flowctl/runner.py:72-215`

- [ ] **Step 1: Add repo_dir parameter to run_workflow signature**

Add `repo_dir: Path | None = None` parameter at line 81:

```python
def run_workflow(
    workflow: WorkflowDef,
    run_dir: Path,
    adapter: ExecutorAdapter | None = None,
    registry: ExecutorRegistry | None = None,
    default_executor: str = "echo",
    executor_config: dict[str, dict] | None = None,
    dry_run: bool = False,
    initial_context: dict[str, str] | None = None,
    workflow_dir: Path | None = None,
    repo_dir: Path | None = None,
    log_level: str = "INFO",
    log_format: str = "json",
    resume: bool = False,
    approval_decision: str | None = None,
    reject_reason: str | None = None,
) -> dict[str, str]:
```

- [ ] **Step 2: Add repo_dir to process_context**

Update process_context dict at line 198:

```python
        process_context = {
            "node": node_def,
            "run_dir": run_dir,
            "workflow_dir": workflow_dir,
            "repo_dir": repo_dir,
        }
```

- [ ] **Step 3: Add repo_dir to ExecutorInput**

Update ExecutorInput creation at line 205:

```python
        inp = ExecutorInput(
            role=node_def.role,
            prompt=processed_prompt,
            prompt_path=node_def.prompt,
            skill_paths=node_def.skills,
            inputs=node_def.inputs,
            outputs=node_def.outputs,
            run_dir=run_dir,
            workflow_dir=workflow_dir,
            repo_dir=repo_dir,
            node=node_def,
        )
```

- [ ] **Step 4: Run tests to verify no regression**

Run: `pytest tests/ -v`
Expected: All existing tests pass

- [ ] **Step 5: Commit**

```bash
git add src/flowctl/runner.py
git commit -m "feat: pass repo_dir through runner to ExecutorInput"
```

---

### Task 7: Update OpencodeAdapter to resolve output paths

**Files:**
- Modify: `src/flowctl/executors/opencode.py:1-92`

- [ ] **Step 1: Add _parse_prefix method to OpencodeAdapter**

Add after line 5:

```python
    def _parse_prefix(self, filename: str) -> tuple[str, str]:
        """Extract prefix and relative path from filename."""
        if filename.startswith("workflow:"):
            return "workflow", filename[9:]
        elif filename.startswith("repo:"):
            return "repo", filename[5:]
        elif filename.startswith("run:"):
            return "run", filename[4:]
        else:
            return "run", filename

    def _resolve_output_path(self, filename: str, inp: ExecutorInput) -> Path:
        """Resolve output file path based on prefix."""
        prefix, rel_path = self._parse_prefix(filename)
        
        if prefix == "workflow":
            base_dir = inp.workflow_dir
        elif prefix == "repo":
            base_dir = inp.repo_dir
        else:
            base_dir = inp.run_dir
        
        if base_dir:
            return base_dir / rel_path
        return inp.run_dir / rel_path
```

- [ ] **Step 2: Update output extraction in execute method**

Replace lines 49-53:

```python
        if proc.returncode == 0:
            session_id = self._extract_session_id(proc.stdout) or self._extract_session_id(proc.stderr)
            self._extract_and_write_outputs(proc.stdout, inp.outputs, inp.run_dir)
            for key, filename in inp.outputs.items():
                artifact_path = self._resolve_output_path(filename, inp)
                if artifact_path.exists():
                    outputs[key] = artifact_path.read_text()
```

- [ ] **Step 3: Run tests to verify no regression**

Run: `pytest tests/ -v`
Expected: All existing tests pass

- [ ] **Step 4: Commit**

```bash
git add src/flowctl/executors/opencode.py
git commit -m "feat: resolve output paths with prefixes in OpencodeAdapter"
```

---

### Task 8: Update EchoAdapter to show resolved paths

**Files:**
- Modify: `src/flowctl/executors/echo.py:1-32`

- [ ] **Step 1: Add _parse_prefix and _resolve_path methods to EchoAdapter**

Add after line 3:

```python
    def _parse_prefix(self, filename: str) -> tuple[str, str]:
        """Extract prefix and relative path from filename."""
        if filename.startswith("workflow:"):
            return "workflow", filename[9:]
        elif filename.startswith("repo:"):
            return "repo", filename[5:]
        elif filename.startswith("run:"):
            return "run", filename[4:]
        else:
            return "run", filename

    def _resolve_path(self, filename: str, inp: ExecutorInput) -> Path:
        """Resolve file path based on prefix."""
        prefix, rel_path = self._parse_prefix(filename)
        
        if prefix == "workflow":
            base_dir = inp.workflow_dir
        elif prefix == "repo":
            base_dir = inp.repo_dir
        else:
            base_dir = inp.run_dir
        
        if base_dir:
            return base_dir / rel_path
        return inp.run_dir / rel_path
```

- [ ] **Step 2: Update execute method to show resolved paths**

Replace `execute` method (lines 6-32):

```python
    def execute(self, inp: ExecutorInput) -> ExecutorResult:
        stdout_lines = [
            f"Role: {inp.role}",
            f"Prompt Path: {inp.prompt_path}",
            "",
            "=" * 60,
            "PROCESSED PROMPT",
            "=" * 60,
            inp.prompt,
            "=" * 60,
            "",
            "=" * 60,
            "RESOLVED PATHS",
            "=" * 60,
        ]
        
        if inp.inputs:
            stdout_lines.append("Inputs:")
            for key, filename in inp.inputs.items():
                resolved = self._resolve_path(filename, inp)
                stdout_lines.append(f"  {key}: {filename} -> {resolved}")
        
        if inp.outputs:
            stdout_lines.append("Outputs:")
            for key, filename in inp.outputs.items():
                resolved = self._resolve_path(filename, inp)
                stdout_lines.append(f"  {key}: {filename} -> {resolved}")
        
        stdout_lines.append("=" * 60)
        
        outputs = {}
        for key, filename in inp.inputs.items():
            resolved = self._resolve_path(filename, inp)
            if resolved.exists():
                outputs[key] = resolved.read_text()
        
        for key, filename in inp.outputs.items():
            resolved = self._resolve_path(filename, inp)
            resolved.parent.mkdir(parents=True, exist_ok=True)
            resolved.write_text(f"echo: mock artifact for {key}")
            outputs[key] = str(resolved)
        
        return ExecutorResult(
            outputs=outputs,
            returncode=0,
            stdout="\n".join(stdout_lines),
            stderr="",
        )
```

- [ ] **Step 3: Run tests to verify no regression**

Run: `pytest tests/ -v`
Expected: All existing tests pass

- [ ] **Step 4: Commit**

```bash
git add src/flowctl/executors/echo.py
git commit -m "feat: show resolved paths in EchoAdapter dry-run output"
```

---

### Task 9: Update artifact_validator to resolve paths

**Files:**
- Modify: `src/flowctl/artifact_validator.py:1-14`

- [ ] **Step 1: Write failing test for path resolution in validator**

Add to `tests/test_artifact_validator.py` (create if doesn't exist):

```python
import pytest
from pathlib import Path
from flowctl.artifact_validator import validate_artifacts


def test_validate_workflow_prefix(tmp_path):
    """Output with workflow: prefix should resolve to workflow_dir."""
    workflow_dir = tmp_path / "flows"
    workflow_dir.mkdir()
    memory_dir = workflow_dir / "memory"
    memory_dir.mkdir()
    
    output_file = memory_dir / "ba.md"
    output_file.write_text("test content")
    
    errors = validate_artifacts(
        {"memory_update": "workflow:memory/ba.md"},
        run_dir=tmp_path / "runs/test",
        workflow_dir=workflow_dir,
        repo_dir=None,
    )
    
    assert len(errors) == 0


def test_validate_repo_prefix(tmp_path):
    """Output with repo: prefix should resolve to repo_dir."""
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    
    output_file = repo_dir / "ARCHITECTURE.md"
    output_file.write_text("test content")
    
    errors = validate_artifacts(
        {"arch": "repo:ARCHITECTURE.md"},
        run_dir=tmp_path / "runs/test",
        workflow_dir=tmp_path / "flows",
        repo_dir=repo_dir,
    )
    
    assert len(errors) == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_artifact_validator.py::test_validate_workflow_prefix -v`
Expected: FAIL with "TypeError: validate_artifacts() got unexpected keyword argument 'workflow_dir'"

- [ ] **Step 3: Update validate_artifacts to resolve paths**

Replace entire `src/flowctl/artifact_validator.py`:

```python
from pathlib import Path


def _parse_prefix(filename: str) -> tuple[str, str]:
    """Extract prefix and relative path from filename."""
    if filename.startswith("workflow:"):
        return "workflow", filename[9:]
    elif filename.startswith("repo:"):
        return "repo", filename[5:]
    elif filename.startswith("run:"):
        return "run", filename[4:]
    else:
        return "run", filename


def _resolve_path(
    filename: str,
    run_dir: Path,
    workflow_dir: Path | None = None,
    repo_dir: Path | None = None,
) -> Path:
    """Resolve file path based on prefix."""
    prefix, rel_path = _parse_prefix(filename)
    
    if prefix == "workflow":
        base_dir = workflow_dir
    elif prefix == "repo":
        base_dir = repo_dir
    else:
        base_dir = run_dir
    
    if base_dir:
        return base_dir / rel_path
    return run_dir / rel_path


def validate_artifacts(
    outputs: dict[str, str],
    run_dir: Path,
    workflow_dir: Path | None = None,
    repo_dir: Path | None = None,
) -> list[str]:
    """Validate output artifacts exist at resolved paths."""
    errors: list[str] = []
    for key, filename in outputs.items():
        resolved_path = _resolve_path(filename, run_dir, workflow_dir, repo_dir)
        
        if not resolved_path.exists():
            errors.append(f"Output '{key}' missing: {resolved_path}")
        elif resolved_path.stat().st_size == 0:
            errors.append(f"Output '{key}' is empty: {resolved_path}")
    return errors
```

- [ ] **Step 4: Update runner.py to pass workflow_dir and repo_dir to validator**

Replace line 259:

```python
        errors = validate_artifacts(node_def.outputs, run_dir, workflow_dir, repo_dir)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_artifact_validator.py -v`
Expected: All tests pass

- [ ] **Step 6: Commit**

```bash
git add src/flowctl/artifact_validator.py tests/test_artifact_validator.py src/flowctl/runner.py
git commit -m "feat: resolve output paths with prefixes in artifact_validator"
```

---

### Task 10: Integration test for end-to-end path prefix

**Files:**
- Create: `tests/integration/test_path_prefix.py`

- [ ] **Step 1: Write integration test**

Create `tests/integration/test_path_prefix.py`:

```python
import pytest
from pathlib import Path
from flowctl.models import WorkflowDef, Node, Transition
from flowctl.runner import run_workflow
from flowctl.executors import create_default_registry


def test_path_prefix_workflow_integration(tmp_path):
    """Test end-to-end path prefix resolution in workflow."""
    workflow_dir = tmp_path / "flows"
    workflow_dir.mkdir()
    run_dir = tmp_path / "runs" / "test"
    run_dir.mkdir(parents=True)
    
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    
    memory_dir = workflow_dir / "memory"
    memory_dir.mkdir()
    memory_file = memory_dir / "architect.md"
    memory_file.write_text("# Architect Memory")
    
    repo_file = repo_dir / "REPO.md"
    repo_file.write_text("# Repo Root")
    
    prompt_dir = workflow_dir / "prompts"
    prompt_dir.mkdir()
    prompt_file = prompt_dir / "test.md"
    prompt_file.write_text("# Test Task")
    
    workflow = WorkflowDef(
        version="1",
        nodes={
            "start": Node(
                role="dev",
                prompt="prompts/test.md",
                inputs={
                    "memory": "workflow:memory/architect.md",
                    "repo": "repo:REPO.md",
                    "local": "run:local.md",
                },
                outputs={
                    "memory_out": "workflow:memory/output.md",
                    "repo_out": "repo:OUTPUT.md",
                    "local_out": "run:local_out.md",
                },
            ),
        },
        transitions=[
            Transition(from_="__start__", to="start"),
        ],
    )
    
    registry = create_default_registry()
    
    result = run_workflow(
        workflow,
        run_dir,
        registry=registry,
        default_executor="echo",
        dry_run=True,
        workflow_dir=workflow_dir,
        repo_dir=repo_dir,
    )
    
    assert result is not None
```

- [ ] **Step 2: Run integration test**

Run: `pytest tests/integration/test_path_prefix.py -v`
Expected: Test passes

- [ ] **Step 3: Commit**

```bash
git add tests/integration/test_path_prefix.py
git commit -m "test: add integration test for path prefix resolution"
```

---

### Task 11: Run full test suite and verify

- [ ] **Step 1: Run all tests**

Run: `pytest tests/ -v`
Expected: All 156+ tests pass

- [ ] **Step 2: Run linting/type checking (if configured)**

Run: `ruff check src/` or `mypy src/` (if available)
Expected: No errors

- [ ] **Step 3: Final commit with any fixes**

```bash
git add -A
git commit -m "chore: fix any remaining issues from test suite"
```

---

## Summary

This plan implements path prefix support for input/output file resolution:

1. **Config**: Added `repo_dir` to `FlowctlConfig` and CLI
2. **Data**: Added `repo_dir` to `ExecutorInput` 
3. **Parsing**: Added `_parse_prefix()` and `_resolve_path()` to `PromptProcessor`
4. **Processing**: Updated input/output section generators to show resolved paths
5. **Execution**: Updated executors to resolve output paths with prefixes
6. **Validation**: Updated artifact validator to resolve paths before checking
7. **Testing**: Comprehensive tests for all new functionality

All changes are backward compatible — no prefix defaults to `run:` which preserves current behavior.