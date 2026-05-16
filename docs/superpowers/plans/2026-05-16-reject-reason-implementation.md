# Reject Reason for Human Approval Nodes - Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add reject reason functionality to human approval nodes, enabling feedback-driven revision cycles with iteration tracking.

**Architecture:** New CLI flag `--reject-reason` (required with `--reject`), auto-load validation of reject-reason.txt, revision nodes (reclarify, redesign) that address feedback and loop back to approval nodes, reject count tracking in state with 5-attempt limit per node.

**Tech Stack:** Python, Click CLI, Pydantic models, YAML workflow definitions

---

## File Structure

| File | Purpose |
|------|---------|
| `src/flowctl/state.py` | Add `reject_counts` field to WorkflowState, update save/load |
| `src/flowctl/cli.py` | Add `--reject-reason` CLI flag with validation |
| `src/flowctl/runner.py` | Add MAX_REJECTS constant, reject_reason handling, count tracking |
| `.flows/workflows/spec-to-code.yaml` | Add reclarify and redesign nodes, update transitions |
| `.flows/prompts/reclarify.md` | Prompt for revising clarify.md based on feedback |
| `.flows/prompts/redesign.md` | Prompt for revising design.md and test-design.md based on feedback |
| `tests/test_cli.py` | Tests for --reject-reason validation |
| `tests/test_runner.py` | Tests for reject count tracking and revision flow |

---

### Task 1: Add reject_counts to WorkflowState

**Files:**
- Modify: `src/flowctl/state.py:17-23`
- Modify: `src/flowctl/state.py:26-53`
- Modify: `src/flowctl/state.py:56-75`

- [ ] **Step 1: Add reject_counts field to WorkflowState dataclass**

```python
@dataclass
class WorkflowState:
    current_node: str
    context: dict[str, str]
    iterations: int
    timestamp: str
    status: WorkflowStatus = WorkflowStatus.RUNNING
    pending_approval_for: Optional[str] = None
    pending_transition_from: Optional[str] = None
    reject_counts: Optional[dict[str, int]] = None  # NEW
```

- [ ] **Step 2: Update save_state to serialize reject_counts**

Add `reject_counts` parameter and include in JSON output:

```python
def save_state(
    run_dir: Path,
    current: str,
    context: dict[str, str],
    iterations: int,
    status: WorkflowStatus = WorkflowStatus.RUNNING,
    pending_approval_for: Optional[str] = None,
    pending_transition_from: Optional[str] = None,
    reject_counts: Optional[dict[str, int]] = None,  # NEW
) -> None:
    state_file = run_dir / "state.json"
    state = WorkflowState(
        current_node=current,
        context=context,
        iterations=iterations,
        timestamp=_timestamp(),
        status=status,
        pending_approval_for=pending_approval_for,
        pending_transition_from=pending_transition_from,
        reject_counts=reject_counts,  # NEW
    )
    state_file.write_text(json.dumps({
        "current_node": state.current_node,
        "context": state.context,
        "iterations": state.iterations,
        "timestamp": state.timestamp,
        "status": state.status.value if isinstance(state.status, WorkflowStatus) else state.status,
        "pending_approval_for": state.pending_approval_for,
        "pending_transition_from": state.pending_transition_from,
        "reject_counts": state.reject_counts,  # NEW
    }, indent=2))
```

- [ ] **Step 3: Update load_state to deserialize reject_counts**

Add `reject_counts` to WorkflowState construction:

```python
def load_state(run_dir: Path) -> Optional[WorkflowState]:
    state_file = run_dir / "state.json"
    if not state_file.exists():
        return None
    
    try:
        data = json.loads(state_file.read_text())
        status_val = data.get("status", "running")
        status = WorkflowStatus(status_val) if status_val in [s.value for s in WorkflowStatus] else WorkflowStatus.RUNNING
        return WorkflowState(
            current_node=data["current_node"],
            context=data["context"],
            iterations=data["iterations"],
            timestamp=data["timestamp"],
            status=status,
            pending_approval_for=data.get("pending_approval_for"),
            pending_transition_from=data.get("pending_transition_from"),
            reject_counts=data.get("reject_counts"),  # NEW
        )
    except (json.JSONDecodeError, KeyError):
        return None
```

- [ ] **Step 4: Run existing tests to verify no breakage**

Run: `pytest tests/test_runner.py -v`
Expected: All existing tests pass

- [ ] **Step 5: Commit**

```bash
git add src/flowctl/state.py
git commit -m "feat: add reject_counts to WorkflowState"
```

---

### Task 2: Add MAX_REJECTS constant to runner.py

**Files:**
- Modify: `src/flowctl/runner.py:11`

- [ ] **Step 1: Add MAX_REJECTS constant**

Add after MAX_ITERATIONS:

```python
MAX_ITERATIONS = 100
MAX_REJECTS = 5  # Maximum reject attempts per approval node
```

- [ ] **Step 2: Run tests to verify**

Run: `pytest tests/test_runner.py -v`
Expected: All tests pass

- [ ] **Step 3: Commit**

```bash
git add src/flowctl/runner.py
git commit -m "feat: add MAX_REJECTS constant for reject count limit"
```

---

### Task 3: Add --reject-reason CLI flag

**Files:**
- Modify: `src/flowctl/cli.py:73`
- Modify: `src/flowctl/cli.py:86-92`
- Modify: `src/flowctl/cli.py:118-136`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write failing test for --reject-reason required validation**

Add test to `tests/test_cli.py`:

```python
def test_cli_reject_reason_required():
    runner = CliRunner()
    with runner.isolated_filesystem():
        flows_dir = Path(".flows/workflows")
        flows_dir.mkdir(parents=True)
        workflow_file = flows_dir / "default.yaml"
        workflow_file.write_text(
            "version: '1'\n"
            "nodes:\n"
            "  planner:\n"
            "    role: planner\n"
            "    prompt: prompts/plan.md\n"
            "    inputs: {}\n"
            "    outputs: {spec: spec.md}\n"
            "transitions:\n"
            "  - from: __start__\n"
            "    to: planner\n"
            "  - from: planner\n"
            "    to: __end__\n"
        )
        
        # Test reject without reason - must require reason
        result = runner.invoke(main, ["run", ".flows/workflows/default.yaml", "--resume", "--reject"])
        assert result.exit_code != 0
        assert "reject-reason" in result.output.lower()


def test_cli_reject_reason_with_value():
    runner = CliRunner()
    with runner.isolated_filesystem():
        flows_dir = Path(".flows/workflows")
        flows_dir.mkdir(parents=True)
        workflow_file = flows_dir / "default.yaml"
        workflow_file.write_text(
            "version: '1'\n"
            "nodes:\n"
            "  planner:\n"
            "    role: planner\n"
            "    prompt: prompts/plan.md\n"
            "    inputs: {}\n"
            "    outputs: {spec: spec.md}\n"
            "transitions:\n"
            "  - from: __start__\n"
            "    to: planner\n"
            "  - from: planner\n"
            "    to: __end__\n"
        )
        
        # Test reject with reason - valid
        result = runner.invoke(main, ["run", ".flows/workflows/default.yaml", "--resume", "--reject", "--reject-reason", "Missing details"])
        # May still fail due to no state, but CLI validation should pass
        assert "--reject-reason is required" not in result.output
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli.py::test_cli_reject_reason_required -v`
Expected: FAIL with "reject-reason not found"

- [ ] **Step 3: Add --reject-reason option to run command**

Add after `--reject` option:

```python
@click.option("--reject-reason", default=None, help="Reason for rejection (required with --reject)")
@click.argument("workflow", default=".flows/workflows/default.yaml")
def run(dry_run, executor, model, agent, workflow, run_id, issue, log_level, log_format, resume, approve, reject, reject_reason):
```

- [ ] **Step 4: Add validation for reject-reason required**

Add after existing flag validations:

```python
    if reject and not reject_reason:
        click.echo("Error: --reject-reason is required when using --reject", err=True)
        raise click.Abort()
```

- [ ] **Step 5: Pass reject_reason to run_workflow**

Update run_workflow call:

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
        reject_reason=reject_reason,  # NEW
    )
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `pytest tests/test_cli.py::test_cli_reject_reason_required tests/test_cli.py::test_cli_reject_reason_with_value -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add src/flowctl/cli.py tests/test_cli.py
git commit -m "feat: add --reject-reason CLI flag with required validation"
```

---

### Task 4: Update runner to handle reject_reason and track counts

**Files:**
- Modify: `src/flowctl/runner.py:52-66`
- Modify: `src/flowctl/runner.py:81-110`
- Modify: `src/flowctl/runner.py:161-169`
- Test: `tests/test_runner.py`

- [ ] **Step 1: Write failing test for reject_reason handling**

Add test to `tests/test_runner.py`:

```python
def test_workflow_resume_with_reject_reason(tmp_path):
    wf = WorkflowDef(
        nodes={
            "step1": Node(role="dev", prompt="p1.md", inputs={}, outputs={"output1": "out1.md"}),
            "human_approval": Node(role="human", prompt="p2.md", executor="human", inputs={}, outputs={"approved": "approved.txt"}),
        },
        transitions=[
            Transition(from_="__start__", to="step1"),
            Transition(from_="step1", to="human_approval"),
            Transition(from_="human_approval", to="__end__", when="approved == 'no'"),
        ],
    )
    
    from flowctl.state import save_state, WorkflowStatus
    
    save_state(tmp_path, "human_approval", {"output1": "existing"}, 1, 
               status=WorkflowStatus.PAUSED, pending_approval_for="approved", pending_transition_from="step1",
               reject_counts={"human_approval": 0})
    
    # Resume with reject and reason
    result = run_workflow(wf, tmp_path, dry_run=False, resume=True, approval_decision="no", reject_reason="Missing details")
    
    assert "approved" in result
    assert result["approved"] == "no"
    
    # Check reject-reason.txt was written
    reject_reason_file = tmp_path / "reject-reason.txt"
    assert reject_reason_file.exists()
    assert reject_reason_file.read_text() == "Missing details"


def test_workflow_reject_reason_validation_empty(tmp_path):
    wf = WorkflowDef(
        nodes={
            "step1": Node(role="dev", prompt="p1.md", inputs={}, outputs={"output1": "out1.md"}),
            "human_approval": Node(role="human", prompt="p2.md", executor="human", inputs={}, outputs={"approved": "approved.txt"}),
        },
        transitions=[
            Transition(from_="__start__", to="step1"),
            Transition(from_="step1", to="human_approval"),
            Transition(from_="human_approval", to="__end__"),
        ],
    )
    
    from flowctl.state import save_state, WorkflowStatus
    
    save_state(tmp_path, "human_approval", {"output1": "existing"}, 1, 
               status=WorkflowStatus.PAUSED, pending_approval_for="approved", pending_transition_from="step1")
    
    # Resume with empty reject reason should fail
    with pytest.raises(click.exceptions.Abort):
        run_workflow(wf, tmp_path, dry_run=False, resume=True, approval_decision="no", reject_reason="")


def test_workflow_reject_count_exceeds_limit(tmp_path):
    wf = WorkflowDef(
        nodes={
            "step1": Node(role="dev", prompt="p1.md", inputs={}, outputs={"output1": "out1.md"}),
            "human_approval": Node(role="human", prompt="p2.md", executor="human", inputs={}, outputs={"approved": "approved.txt"}),
        },
        transitions=[
            Transition(from_="__start__", to="step1"),
            Transition(from_="step1", to="human_approval"),
            Transition(from_="human_approval", to="__end__", when="approved == 'no'"),
        ],
    )
    
    from flowctl.state import save_state, WorkflowStatus
    
    # Save state with reject count at limit (5)
    save_state(tmp_path, "human_approval", {"output1": "existing"}, 1, 
               status=WorkflowStatus.PAUSED, pending_approval_for="approved", pending_transition_from="step1",
               reject_counts={"human_approval": 5})
    
    # Resume with reject should fail (exceeds 5)
    with pytest.raises(click.exceptions.Abort):
        run_workflow(wf, tmp_path, dry_run=False, resume=True, approval_decision="no", reject_reason="Another rejection")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_runner.py::test_workflow_resume_with_reject_reason tests/test_runner.py::test_workflow_reject_reason_validation_empty tests/test_runner.py::test_workflow_reject_count_exceeds_limit -v`
Expected: FAIL

- [ ] **Step 3: Add reject_reason parameter to run_workflow**

Update function signature:

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
    reject_reason: str | None = None,  # NEW
) -> dict[str, str]:
```

- [ ] **Step 4: Add reject_reason handling in resume flow**

Update the resume block to handle reject_reason:

```python
    if resume and has_state(run_dir):
        state = load_state(run_dir)
        if state:
            if state.status == WorkflowStatus.PAUSED:
                if not approval_decision:
                    click.echo(f"Error: Workflow paused at '{state.current_node}'. Use --approve or --reject", err=True)
                    raise click.Abort()
                
                # Handle reject with reason
                if approval_decision == "no" and reject_reason:
                    reject_reason_path = run_dir / "reject-reason.txt"
                    reject_reason_path.write_text(reject_reason)
                    
                    # Auto-load and validate
                    content = reject_reason_path.read_text().strip()
                    if not content:
                        click.echo("Error: reject-reason.txt is empty", err=True)
                        raise click.Abort()
                    
                    # Increment reject count
                    reject_counts = state.reject_counts or {}
                    approval_node = state.current_node
                    count = reject_counts.get(approval_node, 0) + 1
                    
                    # Check limit
                    if count > MAX_REJECTS:
                        click.echo(f"Error: Reject count exceeded ({count}/{MAX_REJECTS}) for node '{approval_node}'", err=True)
                        raise click.Abort()
                    
                    reject_counts[approval_node] = count
                    context["reject_counts"] = str(reject_counts)  # Store as string for context
                
                node_def = workflow.nodes.get(state.current_node)
                if not node_def:
                    raise RuntimeError(f"Node '{state.current_node}' not found")
                
                approval_key = state.pending_approval_for
                output_path = node_def.outputs.get(approval_key) if approval_key else None
                
                context = state.context
                if approval_key and output_path:
                    artifact_path = run_dir / output_path
                    artifact_path.parent.mkdir(parents=True, exist_ok=True)
                    artifact_path.write_text(approval_decision)
                    context[approval_key] = artifact_path.read_text()
                    click.echo(f"Resuming from '{state.current_node}' with decision: {approval_decision}")
                
                # Set current to the human node, will skip in the loop
                current = state.current_node
                iterations = state.iterations
                
                # Pass reject_counts to state save later
                if approval_decision == "no":
                    context["__reject_counts__"] = reject_counts if "reject_counts" not in context else eval(context["reject_counts"])
```

- [ ] **Step 5: Update save_state calls to include reject_counts**

Update state saves to pass reject_counts:

```python
        if executor_name == "human" and not dry_run:
            approval_key = list(node_def.outputs.keys())[0] if node_def.outputs else None
            prev_node = current
            reject_counts_dict = context.get("__reject_counts__") or {}
            save_state(
                run_dir, next_node, context, iterations,
                status=WorkflowStatus.PAUSED,
                pending_approval_for=approval_key,
                pending_transition_from=prev_node,
                reject_counts=reject_counts_dict,
            )
```

And at line 196:

```python
        current = next_node
        
        if not dry_run:
            reject_counts_dict = context.get("__reject_counts__") or {}
            save_state(run_dir, current, context, iterations, reject_counts=reject_counts_dict)
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `pytest tests/test_runner.py::test_workflow_resume_with_reject_reason tests/test_runner.py::test_workflow_reject_reason_validation_empty tests/test_runner.py::test_workflow_reject_count_exceeds_limit -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add src/flowctl/runner.py tests/test_runner.py
git commit -m "feat: add reject_reason handling and reject count tracking in runner"
```

---

### Task 5: Add reclarify node to workflow

**Files:**
- Modify: `.flows/workflows/spec-to-code.yaml`
- Create: `.flows/prompts/reclarify.md`

- [ ] **Step 1: Add reclarify node to spec-to-code.yaml**

Add after human_confirm_clarify node:

```yaml
  reclarify:
    role: ba
    prompt: prompts/reclarify.md
    executor: opencode
    inputs: {clarify: clarify.md, reject_reason: reject-reason.txt}
    outputs: {clarify_md: clarify.md}
```

- [ ] **Step 2: Update human_confirm_clarify reject transition**

Replace old reject transition:

```yaml
  # REMOVE this transition:
  # - from: human_confirm_clarify
  #   to: clarify
  #   when: clarify_approved == "no"
  
  # ADD this transition:
  - from: human_confirm_clarify
    to: reclarify
    when: clarify_approved == "no"
```

- [ ] **Step 3: Add reclarify to human_confirm_clarify transition**

Add unconditional transition after reclarify:

```yaml
  - from: reclarify
    to: human_confirm_clarify
```

- [ ] **Step 4: Create prompts/reclarify.md**

```markdown
# Role
Business Analyst revising clarification document based on human feedback.

# Inputs
- Previous clarification: `{clarify}`
- Reject reason: `{reject_reason}`

# Task
The human reviewer rejected the previous clarification with this feedback:

> {reject_reason}

Review the previous clarification and address the specific concerns raised. Update the document to:

1. Address each point mentioned in the reject reason
2. Add missing details or constraints identified
3. Improve clarity where feedback indicated confusion
4. Keep the core structure intact, revise incrementally

# Output
Write updated clarification to `clarify.md` (overwrites previous version).
```

- [ ] **Step 5: Run tests to verify workflow validation**

Run: `pytest tests/test_loader.py -v` (if exists) or `flowctl run --dry-run .flows/workflows/spec-to-code.yaml`
Expected: PASS / no validation errors

- [ ] **Step 6: Commit**

```bash
git add .flows/workflows/spec-to-code.yaml .flows/prompts/reclarify.md
git commit -m "feat: add reclarify node and transitions for reject feedback loop"
```

---

### Task 6: Add redesign node to workflow

**Files:**
- Modify: `.flows/workflows/spec-to-code.yaml`
- Create: `.flows/prompts/redesign.md`

- [ ] **Step 1: Add redesign node to spec-to-code.yaml**

Add after human_confirm_design node:

```yaml
  redesign:
    role: architect
    prompt: prompts/redesign.md
    executor: opencode
    inputs:
      design: docs/design.md
      test_design: docs/test-design.md
      reject_reason: reject-reason.txt
    outputs:
      design_md: docs/design.md
      test_design_md: docs/test-design.md
```

- [ ] **Step 2: Update human_confirm_design reject transition**

Replace old reject transition:

```yaml
  # REMOVE this transition:
  # - from: human_confirm_design
  #   to: clarify
  #   when: design_approved == "no"
  
  # ADD this transition:
  - from: human_confirm_design
    to: redesign
    when: design_approved == "no"
```

- [ ] **Step 3: Add redesign to human_confirm_design transition**

Add unconditional transition after redesign:

```yaml
  - from: redesign
    to: human_confirm_design
```

- [ ] **Step 4: Create prompts/redesign.md**

```markdown
# Role
Architect revising design and test-design documents based on human feedback.

# Inputs
- Previous design: `{design}`
- Previous test design: `{test_design}`
- Reject reason: `{reject_reason}`

# Task
The human reviewer rejected the previous design with this feedback:

> {reject_reason}

Review both documents and address the specific concerns raised. Update to:

1. Address each point in the reject reason
2. Fix architecture issues identified
3. Update test design to match revised design
4. Keep valid parts intact, revise problem areas

# Output
Write updated design to `docs/design.md` and test design to `docs/test-design.md`.
```

- [ ] **Step 5: Run tests to verify workflow validation**

Run: `pytest tests/ -v`
Expected: All tests pass

- [ ] **Step 6: Commit**

```bash
git add .flows/workflows/spec-to-code.yaml .flows/prompts/redesign.md
git commit -m "feat: add redesign node and transitions for reject feedback loop"
```

---

### Task 7: Add integration test for full reject-reason flow

**Files:**
- Test: `tests/test_runner.py`

- [ ] **Step 1: Write integration test for reclarify flow**

Add test to `tests/test_runner.py`:

```python
def test_workflow_reject_flows_to_reclarify(tmp_path):
    wf = WorkflowDef(
        nodes={
            "step1": Node(role="dev", prompt="p1.md", inputs={}, outputs={"output1": "out1.md"}),
            "human_approval": Node(role="human", prompt="p2.md", executor="human", inputs={}, outputs={"approved": "approved.txt"}),
            "revision": Node(role="dev", prompt="p3.md", inputs={"reject_reason": "reject-reason.txt"}, outputs={"output2": "out2.md"}),
        },
        transitions=[
            Transition(from_="__start__", to="step1"),
            Transition(from_="step1", to="human_approval"),
            Transition(from_="human_approval", to="__end__", when="approved == 'yes'"),
            Transition(from_="human_approval", to="revision", when="approved == 'no'"),
            Transition(from_="revision", to="human_approval"),
        ],
    )
    
    from flowctl.state import save_state, WorkflowStatus
    
    save_state(tmp_path, "human_approval", {"output1": "existing"}, 1, 
               status=WorkflowStatus.PAUSED, pending_approval_for="approved", pending_transition_from="step1",
               reject_counts={"human_approval": 0})
    
    # Resume with reject
    result = run_workflow(wf, tmp_path, dry_run=False, resume=True, approval_decision="no", reject_reason="Needs revision")
    
    # Should pause again at human_approval after revision
    state = load_state(tmp_path)
    assert state is not None
    assert state.status == WorkflowStatus.PAUSED
    assert state.current_node == "human_approval"
    assert state.reject_counts == {"human_approval": 1}


def test_workflow_multiple_reject_cycles(tmp_path):
    wf = WorkflowDef(
        nodes={
            "step1": Node(role="dev", prompt="p1.md", inputs={}, outputs={"output1": "out1.md"}),
            "human_approval": Node(role="human", prompt="p2.md", executor="human", inputs={}, outputs={"approved": "approved.txt"}),
            "revision": Node(role="dev", prompt="p3.md", inputs={}, outputs={"output2": "out2.md"}),
        },
        transitions=[
            Transition(from_="__start__", to="step1"),
            Transition(from_="step1", to="human_approval"),
            Transition(from_="human_approval", to="__end__", when="approved == 'yes'"),
            Transition(from_="human_approval", to="revision", when="approved == 'no'"),
            Transition(from_="revision", to="human_approval"),
        ],
    )
    
    from flowctl.state import save_state, WorkflowStatus
    
    # First reject cycle
    save_state(tmp_path, "human_approval", {"output1": "v1"}, 1, 
               status=WorkflowStatus.PAUSED, pending_approval_for="approved", pending_transition_from="step1",
               reject_counts={"human_approval": 0})
    
    run_workflow(wf, tmp_path, dry_run=False, resume=True, approval_decision="no", reject_reason="First issue")
    
    state = load_state(tmp_path)
    assert state.reject_counts == {"human_approval": 1}
    
    # Second reject cycle
    run_workflow(wf, tmp_path, dry_run=False, resume=True, approval_decision="no", reject_reason="Second issue")
    
    state = load_state(tmp_path)
    assert state.reject_counts == {"human_approval": 2}
    
    # Third reject cycle then approve
    run_workflow(wf, tmp_path, dry_run=False, resume=True, approval_decision="yes")
    
    assert not has_state(tmp_path)
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `pytest tests/test_runner.py::test_workflow_reject_flows_to_reclarify tests/test_runner.py::test_workflow_multiple_reject_cycles -v`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add tests/test_runner.py
git commit -m "test: add integration tests for reject-reason flow with revision nodes"
```

---

### Task 8: Update status command to show reject count

**Files:**
- Modify: `src/flowctl/cli.py:32-58`

- [ ] **Step 1: Update status command to display reject_counts**

Update status command output:

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
    
    if state.reject_counts:
        for node, count in state.reject_counts.items():
            click.echo(f"Reject count ({node}): {count}/{MAX_REJECTS}")
    
    if state.status == WorkflowStatus.PAUSED:
        if state.pending_approval_for:
            click.echo(f"Pending approval: {state.pending_approval_for}")
        click.echo(f"Approve: flowctl run --resume --approve --run-id {run_dir.name}")
        click.echo(f"Reject: flowctl run --resume --reject --reject-reason \"<reason>\" --run-id {run_dir.name}")
```

Add import for MAX_REJECTS:

```python
from .runner import MAX_REJECTS
```

- [ ] **Step 2: Run tests to verify**

Run: `pytest tests/test_cli.py::test_cli_status_command -v`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add src/flowctl/cli.py
git commit -m "feat: update status command to show reject counts and updated reject instructions"
```

---

## Self-Review

**1. Spec coverage check:**

| Spec Requirement | Task Coverage |
|------------------|---------------|
| `--reject-reason` CLI flag required with `--reject` | Task 3 |
| Auto-load reject-reason.txt and validate | Task 4 |
| reject_counts in state | Task 1 |
| MAX_REJECTS = 5 constant | Task 2 |
| Fail workflow on exceed | Task 4 |
| reclarify node | Task 5 |
| redesign node | Task 6 |
| Updated transitions | Task 5, Task 6 |
| Prompt templates | Task 5, Task 6 |
| Tests for all flows | Task 3, Task 4, Task 7 |
| Status command shows counts | Task 8 |

All spec requirements covered.

**2. Placeholder scan:**

No TBDs, TODOs, or placeholders found. All steps have complete code.

**3. Type consistency:**

- `reject_counts: Optional[dict[str, int]]` used consistently in state.py, runner.py
- `reject_reason: str | None` used consistently in cli.py, runner.py
- MAX_REJECTS = 5 constant defined in runner.py, imported in cli.py for status

---

**Plan complete.** Ready for execution via subagent-driven-development or executing-plans.