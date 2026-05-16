# Human Approval Node Pause/Resume Design

## Problem

Issue #11: Human approval nodes with `executor: human` don't pause - they run directly. The workflow needs to pause at human nodes and wait for user approval/rejection before continuing.

## Solution Overview

Minimal implementation that fixes existing runner.py pause logic, adds CLI flags for approve/reject, and provides a status command for inspecting paused workflows.

## Design

### Data Model

No changes needed. Existing state model already supports pause:

- `WorkflowStatus` enum: RUNNING, PAUSED, COMPLETED, FAILED
- `WorkflowState` fields: `pending_approval_for`, `pending_transition_from`
- Workflow YAML: human nodes already have `executor: human`

### Pause Mechanism

When workflow reaches a node with `executor: human`:

1. Detect `executor_name == "human"` in runner.py loop
2. Set `current_node` to the human node (e.g., `human_confirm_clarify`)
3. Save state with:
   - `status = PAUSED`
   - `pending_approval_for` = first output key (e.g., `"clarify_approved"`)
   - `pending_transition_from` = previous node name (for context display)
4. Log pause event to execution.log
5. Print CLI message with approve/reject instructions
6. Exit runner

### Resume Mechanism

When user runs `flowctl run --resume --approve` or `--reject`:

1. Load state from `state.json`
2. Validate: status must be PAUSED, approve/reject flag required
3. Print resume message with node name and inputs
4. Write approval file: `(run_dir / output_path).write_text("yes" or "no")`
5. Read file into context: `context[output_key] = file.read_text()`
6. Clear pending fields, save state with status=RUNNING
7. Continue runner loop: skip node execution, evaluate transitions
8. Conditional transitions route based on approval value

**Approve vs Reject behavior**:
- Approve (`"yes"`): matches `when: output_key == "yes"` → proceeds forward
- Reject (`"no"`): matches `when: output_key == "no"` → loops back (e.g., to `clarify` node)

### CLI Changes

**New flags for `flowctl run`**:
- `--approve`: Approve pending human node
- `--reject`: Reject pending human node

**Validation rules**:
- Both flags: error
- Flag without `--resume`: error
- `--resume` on non-paused state: error

**New command `flowctl status`**:
- Shows run status, paused node, inputs
- Displays approve/reject commands

## Files Changed

| File | Change |
|------|--------|
| `src/flowctl/runner.py` | Complete pause logic, add resume flow for human nodes |
| `src/flowctl/logger.py` | Add `log_pause()` method |
| `src/flowctl/cli.py` | Add `--approve/--reject` flags, add `status` command |
| `tests/test_runner.py` | Add tests for pause/resume flow |

## Implementation Approach

Minimal changes to existing code:

1. Fix missing `log_pause` in logger.py
2. Complete pause detection in runner.py (already partially implemented at lines 113-123)
3. Add resume logic: detect PAUSED state, validate flags, write/read file, inject to context
4. Add CLI flags and status command
5. Add tests

No new abstractions or executors. Pause logic stays in runner, resume logic adds a few conditionals.