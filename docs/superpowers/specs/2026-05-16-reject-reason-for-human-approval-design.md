# Reject Reason for Human Approval Nodes - Design Document

**Date:** 2026-05-16
**Issue:** https://github.com/ccijunk/ai-workflow/issues/16

## Problem

When a human rejects at an approval node, the workflow loops back but there's no mechanism for the human to provide a reason/feedback for the rejection. The current reject flow is problematic:

- `human_confirm_clarify` → `clarify` (loses previous work)
- `human_confirm_design` → `clarify` (loses all design and test-design work)

This makes iterations inefficient because:
1. The next iteration doesn't know what was wrong
2. Previous valid work is discarded
3. No feedback loop for improvement

## Solution

Add `--reject-reason` CLI flag that allows humans to provide feedback when rejecting. Workflow transitions to revision nodes (`reclarify`, `redesign`) that address specific feedback, then returns to the same approval node for another cycle.

## Architecture

### New Flow

```
clarify → human_confirm_clarify → (reject with reason) → reclarify → human_confirm_clarify
                                        ↓
                                    (approve) → design → test_design → human_confirm_design → (reject with reason) → redesign → human_confirm_design
                                                                              ↓
                                                                          (approve) → explore → ...
```

### Components

| Component | Purpose |
|-----------|---------|
| `--reject-reason` CLI flag | Required text when using `--reject` |
| `reject_counts` in state | Dict tracking reject count per approval node |
| `reclarify` node | BA role, takes clarify.md + reject_reason, outputs updated clarify.md |
| `redesign` node | Architect role, takes design.md + test-design.md + reject_reason, outputs updated versions |
| `reject-reason.txt` artifact | Written on reject, auto-loaded and validated, injected into revision node context |

### Separation of Concerns

- Initial clarification: `clarify` node (unchanged)
- Revision clarification: `reclarify` node (new, different prompt, handles feedback)
- Initial design: `design` + `test_design` nodes (unchanged)
- Revision design: `redesign` node (new, handles both design and test-design feedback)

## Data Flow

### Reject Flow (human_confirm_clarify)

```
human_confirm_clarify (paused)
    ↓
--reject --reject-reason "Missing API constraints"
    ↓
1. Write reject-reason.txt to run dir with content
2. Auto-load reject-reason.txt, validate non-empty content
   → If empty/missing: Error "reject reason required"
3. Write "no" to clarify-approved.txt
4. Load state, increment reject_counts["human_confirm_clarify"]
5. Check: count <= 5? If > 5, fail workflow
6. Resume with approval_decision="no"
    ↓
Transition evaluates: clarify_approved == "no" → reclarify
    ↓
reclarify node executes:
  inputs: {clarify: clarify.md, reject_reason: reject-reason.txt}
  outputs: {clarify_md: clarify.md}  (overwrites)
    ↓
Transition: reclarify → human_confirm_clarify (unconditional)
    ↓
human_confirm_clarify pauses again (new approval cycle)
```

### Same pattern for human_confirm_design → redesign → human_confirm_design

## State Model

```yaml
# .flows/runs/latest/state.yaml
current_node: human_confirm_clarify
status: PAUSED
context: {...}
iterations: 12
pending_approval_for: clarify_approved
pending_transition_from: clarify
reject_counts:
  human_confirm_clarify: 2
  human_confirm_design: 0
```

## CLI Usage

```bash
# Valid
flowctl run --resume --reject --reject-reason "Missing details" --run-id latest

# Error: missing reason
flowctl run --resume --reject --run-id latest
# → Error: --reject-reason is required when using --reject

# Error: exceeds limit
flowctl run --resume --reject --reject-reason "..." --run-id latest
# → Error: Reject count exceeded (6/5) for node 'human_confirm_clarify'. Workflow failed.
```

## Workflow YAML

### New Nodes

```yaml
reclarify:
  role: ba
  prompt: prompts/reclarify.md
  executor: opencode
  inputs: {clarify: clarify.md, reject_reason: reject-reason.txt}
  outputs: {clarify_md: clarify.md}

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

### New Transitions

```yaml
- from: human_confirm_clarify
  to: reclarify
  when: clarify_approved == "no"

- from: reclarify
  to: human_confirm_clarify

- from: human_confirm_design
  to: redesign
  when: design_approved == "no"

- from: redesign
  to: human_confirm_design
```

### Removed Transitions

```yaml
# REMOVE: old reject paths
- from: human_confirm_clarify
  to: clarify
  when: clarify_approved == "no"

- from: human_confirm_design
  to: clarify
  when: design_approved == "no"
```

## Implementation Details

### CLI Changes (cli.py)

- Add `--reject-reason` option
- Validate: required when `--reject` is used
- Pass to runner as `reject_reason` parameter

### Runner Changes (runner.py)

- Add `reject_reason` parameter to `run_workflow()`
- Add `MAX_REJECTS = 5` constant
- On resume with reject:
  1. Write `reject-reason.txt`
  2. Auto-load and validate content
  3. Increment reject_counts for approval node
  4. Check against MAX_REJECTS, fail if exceeded
  5. Pass reject_counts to state

### State Changes (state.py)

- Add `reject_counts: dict[str, int] | None = None` to WorkflowState

### Constants

```python
MAX_REJECTS = 5  # Maximum reject attempts per approval node
```

## Prompt Templates

### prompts/reclarify.md

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

### prompts/redesign.md

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

## Constraints

1. `--reject-reason` is REQUIRED when using `--reject`
2. Reject reason must have non-empty content (validated by auto-load)
3. Output files overwrite previous versions (single source of truth)
4. Maximum 5 reject attempts per approval node
5. On exceeding limit, workflow fails with error

## Test Cases

1. Reject with reason flows to reclarify → human_confirm_clarify
2. Approve after reclarify goes to design
3. Multiple reject/approve cycles (tracking iterations)
4. Reject without reason fails validation
5. Reject exceeds 5 limit fails workflow
6. Same patterns for design rejection (redesign)
7. Empty reject-reason.txt fails validation
8. Reject-reason.txt content preserved in context

## Edge Cases

- Very long reject reason text (no truncation, allow)
- Reject reason with special characters/formatting
- Multiple approval nodes in sequence (separate counts)
- Resume after workflow failure due to limit