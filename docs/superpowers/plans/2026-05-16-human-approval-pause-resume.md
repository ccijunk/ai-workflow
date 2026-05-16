# Human Approval Pause/Resume Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement pause/resume mechanism for human approval nodes with CLI flags and status command.

**Architecture:** Minimal changes to runner.py for pause detection and resume flow. Add log_pause to logger, add --approve/--reject flags and status command to CLI.

**Tech Stack:** Python, Click CLI, pytest

---

## File Structure

| File | Responsibility | Change Type |
|------|---------------|-------------|
| `src/flowctl/logger.py` | Add log_pause method | Modify |
| `src/flowctl/runner.py` | Pause detection, resume flow for human nodes | Modify |
| `src/flowctl/cli.py` | Add --approve/--reject flags, add status command | Modify |
| `tests/test_runner.py` | Test pause/resume flow | Modify |
| `tests/test_cli.py` | Test CLI flags and status command | Modify |

---

### Task 1: Add log_pause method to logger

**Files:**
- Modify: `src/flowctl/logger.py:171`
- Test: `tests/test_logger.py`

- [ ] **Step 1: Write the failing test**

```python
def test_log_pause(tmp_path):
    from flowctl.logger import WorkflowLogger
    
    logger = WorkflowLogger("test-run", tmp_path, "INFO", "json")
    logger.log_pause("human_confirm_clarify")
    
    log_content = (tmp_path / "execution.log").read_text()
    assert "pause" in log_content
    assert "human_confirm_clarify" in log_content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_logger.py::test_log_pause -v`
Expected: FAIL with "AttributeError: 'WorkflowLogger' object has no attribute 'log_pause'"

- [ ] **Step 3: Write minimal implementation**

Add to `src/flowctl/logger.py` after `log_error` method (around line 171):

```python
def log_pause(self, node_id: str, inputs: dict = None):
    entry = LogEntry(
        timestamp=self._timestamp(),
        level="INFO",
        run_id=self.run_id,
        event="pause",
        node=node_id,
        inputs=inputs,
    )
    self._write(entry)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_logger.py::test_log_pause -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/flowctl/logger.py tests/test_logger.py
git commit -m "feat: add log_pause method to WorkflowLogger"
```

---

### Task 2: Fix pause detection in runner.py

**Files:**
- Modify: `src/flowctl/runner.py:113-123`
- Test: `tests/test_runner.py`

- [ ] **Step 1: Write the failing test**

```python
def test_workflow_pauses_at_human_node(tmp_path):
    wf = WorkflowDef(
        nodes={
            "step1": Node(role="dev", prompt="p1.md", inputs={}, outputs={"output1": "out1.md"}),
            "human_approval": Node(role="human", prompt="p2.md", executor="human", inputs={}, outputs={"approved": "approved.txt"}),
            "step2": Node(role="dev", prompt="p3.md", inputs={}, outputs={"output2": "out2.md"}),
        },
        transitions=[
            Transition(from_="__start__", to="step1"),
            Transition(from_="step1", to="human_approval"),
            Transition(from_="human_approval", to="step2", when="approved == 'yes'"),
            Transition(from_="step2", to="__end__"),
        ],
    )
    
    from flowctl.state import load_state, WorkflowStatus
    
    result = run_workflow(wf, tmp_path, dry_run=False)
    
    state = load_state(tmp_path)
    assert state is not None
    assert state.status == WorkflowStatus.PAUSED
    assert state.current_node == "human_approval"
    assert state.pending_approval_for == "approved"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_runner.py::test_workflow_pauses_at_human_node -v`
Expected: FAIL - either runs through without pause, or AttributeError for log_pause

- [ ] **Step 3: Fix pause detection logic**

Replace lines 113-123 in `src/flowctl/runner.py`:

```python
if executor_name == "human" and not dry_run:
    approval_key = list(node_def.outputs.keys())[0] if node_def.outputs else None
    prev_node = current
    save_state(
        run_dir, next_node, context, iterations,
        status=WorkflowStatus.PAUSED,
        pending_approval_for=approval_key,
        pending_transition_from=prev_node,
    )
    inputs_display = {k: v for k, v in node_def.inputs.items()} if node_def.inputs else {}
    logger.log_pause(next_node, inputs_display)
    click.echo(f"Workflow paused at '{next_node}'. Approve: flowctl run --resume --approve | Reject: flowctl run --resume --reject")
    return context
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_runner.py::test_workflow_pauses_at_human_node -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/flowctl/runner.py tests/test_runner.py
git commit -m "fix: implement pause detection for human executor nodes"
```

---

### Task 3: Add --approve/--reject flags to CLI

**Files:**
- Modify: `src/flowctl/cli.py:30-40`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write the failing test**

```python
def test_cli_approve_reject_flags():
    from click.testing import CliRunner
    from flowctl.cli import main
    
    runner = CliRunner()
    
    # Test approve flag validation
    result = runner.invoke(main, ["run", ".flows/workflows/default.yaml", "--approve"])
    assert result.exit_code != 0
    assert "must use --resume" in result.output.lower()
    
    # Test both flags error
    result = runner.invoke(main, ["run", ".flows/workflows/default.yaml", "--resume", "--approve", "--reject"])
    assert result.exit_code != 0
    assert "cannot use both" in result.output.lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py::test_cli_approve_reject_flags -v`
Expected: FAIL with "no such option: --approve"

- [ ] **Step 3: Add flags and validation**

Modify `src/flowctl/cli.py` run command (add after `--resume` option around line 38):

```python
@click.option("--approve", is_flag=True, help="Approve pending human node")
@click.option("--reject", is_flag=True, help="Reject pending human node")
@click.argument("workflow", default=".flows/workflows/default.yaml")
def run(dry_run, executor, model, agent, workflow, run_id, issue, log_level, log_format, resume, approve, reject):
```

Add validation in run function body (after workflow validation around line 51):

```python
    if (approve or reject) and not resume:
        click.echo("Error: Must use --resume with --approve/--reject", err=True)
        raise click.Abort()
    
    if approve and reject:
        click.echo("Error: Cannot use both --approve and --reject", err=True)
        raise click.Abort()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_cli.py::test_cli_approve_reject_flags -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/flowctl/cli.py tests/test_cli.py
git commit -m "feat: add --approve/--reject flags with validation"
```

---

### Task 4: Implement resume flow for human nodes

**Files:**
- Modify: `src/flowctl/runner.py:79-85` (resume section)
- Modify: `src/flowctl/cli.py:77-88` (pass flags to runner)
- Test: `tests/test_runner.py`

- [ ] **Step 1: Write the failing test**

```python
def test_workflow_resume_with_approve(tmp_path):
    wf = WorkflowDef(
        nodes={
            "step1": Node(role="dev", prompt="p1.md", inputs={}, outputs={"output1": "out1.md"}),
            "human_approval": Node(role="human", prompt="p2.md", executor="human", inputs={}, outputs={"approved": "approved.txt"}),
            "step2": Node(role="dev", prompt="p3.md", inputs={}, outputs={"output2": "out2.md"}),
        },
        transitions=[
            Transition(from_="__start__", to="step1"),
            Transition(from_="step1", to="human_approval"),
            Transition(from_="human_approval", to="step2", when="approved == 'yes'"),
            Transition(from_="human_approval", to="__end__", when="approved == 'no'"),
            Transition(from_="step2", to="__end__"),
        ],
    )
    
    from flowctl.state import save_state, WorkflowStatus
    
    # Simulate paused state
    save_state(tmp_path, "human_approval", {"output1": "existing"}, 1, 
               status=WorkflowStatus.PAUSED, pending_approval_for="approved", pending_transition_from="step1")
    
    # Resume with approve
    result = run_workflow(wf, tmp_path, dry_run=False, resume=True, approval_decision="yes")
    
    assert "approved" in result
    assert result["approved"] == "yes"
    assert "output2" in result
    assert not (tmp_path / "state.json").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_runner.py::test_workflow_resume_with_approve -v`
Expected: FAIL with "unexpected keyword argument 'approval_decision'" or wrong behavior

- [ ] **Step 3: Add approval_decision parameter and resume logic**

Modify `run_workflow` function signature in `src/flowctl/runner.py` (line 51):

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
    log_level: str = "INFO",
    log_format: str = "json",
    resume: bool = False,
    approval_decision: str | None = None,
) -> dict[str, str]:
```

Add resume logic after loading state (around line 85):

```python
    if resume and has_state(run_dir):
        state = load_state(run_dir)
        if state:
            if state.status == WorkflowStatus.PAUSED:
                if not approval_decision:
                    click.echo(f"Error: Workflow paused at '{state.current_node}'. Use --approve or --reject", err=True)
                    raise click.Abort()
                
                node_def = workflow.nodes.get(state.current_node)
                if not node_def:
                    raise RuntimeError(f"Node '{state.current_node}' not found")
                
                approval_key = state.pending_approval_for
                output_path = node_def.outputs.get(approval_key) if approval_key else None
                
                if approval_key and output_path:
                    artifact_path = run_dir / output_path
                    artifact_path.parent.mkdir(parents=True, exist_ok=True)
                    artifact_path.write_text(approval_decision)
                    context[approval_key] = artifact_path.read_text()
                    click.echo(f"Resuming from '{state.current_node}' with decision: {approval_decision}")
                
                current = state.current_node
                context = state.context
                iterations = state.iterations
            else:
                current = state.current_node
                context = state.context
                iterations = state.iterations
```

Modify node execution to skip human nodes after approval (around line 106):

```python
        node_def = workflow.nodes.get(next_node)
        if not node_def:
            logger.log_error(RuntimeError(f"Node '{next_node}' not found"))
            raise RuntimeError(f"Node '{next_node}' not found in workflow definition")

        executor_name = resolve_executor(node_def, default_executor, config)
        
        # Skip human node if we just resumed with approval
        if executor_name == "human" and approval_decision and current == next_node:
            current = next_node
            if not dry_run:
                save_state(run_dir, current, context, iterations, status=WorkflowStatus.RUNNING)
            continue
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_runner.py::test_workflow_resume_with_approve -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/flowctl/runner.py tests/test_runner.py
git commit -m "feat: implement resume flow with approval decision injection"
```

---

### Task 5: Pass approval_decision from CLI to runner

**Files:**
- Modify: `src/flowctl/cli.py:77-88`

- [ ] **Step 1: Update CLI to pass approval_decision**

Modify the `run_workflow` call in `src/flowctl/cli.py` (around line 77):

```python
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
```

- [ ] **Step 2: Test the full CLI flow**

Create a simple workflow file for testing:

```bash
cat > .flows/workflows/test-human.yaml << 'EOF'
version: "1"
nodes:
  step1:
    role: dev
    prompt: prompts/test.md
    inputs: {}
    outputs: {output1: out1.md}
  human_approval:
    role: human
    prompt: prompts/test.md
    executor: human
    inputs: {}
    outputs: {approved: approved.txt}
  step2:
    role: dev
    prompt: prompts/test.md
    inputs: {}
    outputs: {output2: out2.md}
transitions:
  - from: __start__
    to: step1
  - from: step1
    to: human_approval
  - from: human_approval
    to: step2
    when: approved == 'yes'
  - from: step2
    to: __end__
EOF
```

Run dry-run to test:

```bash
uv run flowctl run .flows/workflows/test-human.yaml --dry-run --run-id test-human
```

Expected: Should pause at human_approval node and print pause message

- [ ] **Step 3: Commit**

```bash
git add src/flowctl/cli.py .flows/workflows/test-human.yaml
git commit -m "feat: pass approval_decision from CLI flags to runner"
```

---

### Task 6: Add status command

**Files:**
- Modify: `src/flowctl/cli.py:20-28`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write the failing test**

```python
def test_cli_status_command(tmp_path):
    from click.testing import CliRunner
    from flowctl.cli import main
    from flowctl.state import save_state, WorkflowStatus
    
    # Create a paused state
    run_dir = tmp_path / ".flows" / "runs" / "test-run"
    run_dir.mkdir(parents=True)
    save_state(run_dir, "human_approval", {"input": "test.md"}, 1,
               status=WorkflowStatus.PAUSED, pending_approval_for="approved", pending_transition_from="step1")
    
    runner = CliRunner()
    result = runner.invoke(main, ["status", "--run-id", "test-run"], cwd=str(tmp_path))
    
    assert result.exit_code == 0
    assert "PAUSED" in result.output
    assert "human_approval" in result.output
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py::test_cli_status_command -v`
Expected: FAIL with "no such command: status"

- [ ] **Step 3: Add status command**

Add to `src/flowctl/cli.py` after the upgrade command (around line 28):

```python
@main.command()
@click.option("--run-id", default=None)
@click.option("--target", default=None)
def status(run_id, target):
    """Show workflow run status."""
    from pathlib import Path
    from .state import load_state, WorkflowStatus
    
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
    
    if state.status == WorkflowStatus.PAUSED:
        if state.pending_approval_for:
            click.echo(f"Pending approval: {state.pending_approval_for}")
        click.echo(f"Approve: flowctl run --resume --approve --run-id {run_dir.name}")
        click.echo(f"Reject: flowctl run --resume --reject --run-id {run_dir.name}")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_cli.py::test_cli_status_command -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/flowctl/cli.py tests/test_cli.py
git commit -m "feat: add status command to show workflow run status"
```

---

### Task 7: Run all tests and verify end-to-end flow

**Files:**
- All test files

- [ ] **Step 1: Run full test suite**

```bash
uv run pytest tests/ -v
```

Expected: All tests pass

- [ ] **Step 2: Manual end-to-end test with spec-to-code workflow**

```bash
uv run flowctl run .flows/workflows/spec-to-code.yaml --dry-run --run-id e2e-test
```

Expected workflow pauses at `human_confirm_clarify` node, prints pause message.

```bash
uv run flowctl status --run-id e2e-test
```

Expected: Shows PAUSED status with approve/reject commands.

```bash
uv run flowctl run .flows/workflows/spec-to-code.yaml --resume --approve --run-id e2e-test --dry-run
```

Expected: Resumes, injects "yes", proceeds to next node.

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "feat: complete human approval pause/resume implementation"
```

---

## Summary

This plan implements the pause/resume mechanism for human approval nodes with minimal changes:
- 4 files modified (logger, runner, cli, tests)
- 7 tasks with TDD approach
- Each task produces working, testable code
- Clear commit boundaries for each feature