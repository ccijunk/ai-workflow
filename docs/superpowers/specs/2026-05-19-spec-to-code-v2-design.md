# spec-to-code-v2 Workflow Design

## Problem

The existing `spec-to-code.yaml` workflow lacks adversarial gates at critical handoffs, leading to quality issues in downstream implementation. The spec describes a rigorous workflow with:
- Domain model verification before architect design
- Testability verification before test architect work
- Code review (DDD focus) and test review gates
- Knowledge base that persists learnings across runs

Current workflow uses human approval nodes for clarify and design gates, but lacks structured review criteria and retry loops with feedback propagation.

## Solution

Implement `spec-to-code-v2.yaml` with:
- Human gates at domain, testability, code review, and test review checkpoints
- Retry loops: gate BLOCKED → upstream node re-runs with review artifact + reject-reason
- Knowledge base in `.flows/memory/` updated by reflect node
- Sequential execution of parallel tracks (developer → test-developer)
- Implicit join: `final_review` waits for both tracks via input dependencies

**Key design decisions:**
- Prompt-heavy approach: YAML defines structure, prompts handle gate logic and retry instructions
- Reuse existing engine infrastructure: human nodes, MAX_REJECTS=5, PromptProcessor
- Optional inputs handled gracefully: first run skips missing retry inputs, retry includes them
- Memory files as outputs: reflect node outputs updated memory content

## Architecture

### Directory Structure

```
.flows/
├── roles/
│   ├── ba.yaml           # Config: model, executor
│   ├── architect.yaml
│   ├── test-arch.yaml
│   ├── developer.yaml
│   ├── test-developer.yaml
│   ├── reviewer.yaml
│   ├── meta.yaml
│   ├── human.yaml
│   └── github.yaml
├── prompts/
│   ├── clarity.md        # Node task prompt for ba node
│   ├── domain-review.md  # Gate prompt for human domain gate
│   ├── design.md         # Node task prompt for architect node
│   ├── testability-review.md  # Gate prompt for testability gate
│   ├── test-design.md    # Node task prompt for test_arch
│   ├── implement.md      # Developer task prompt
│   ├── test-develop.md   # Test-developer task + run tests
│   ├── code-review.md    # Gate prompt for code review
│   ├── test-review.md    # Gate prompt for test review
│   ├── final-review.md   # Final reviewer prompt
│   └── reflect.md        # Reflect node prompt
├── memory/
│   ├── ba.md             # BA role prompt + learned heuristics
│   ├── architect.md      # Architect role prompt + heuristics
│   ├── test-arch.md      # Test-architect role prompt + heuristics
│   ├── developer.md      # Developer role prompt + heuristics
│   ├── test-developer.md # Test-developer role prompt + heuristics
│   ├── reviewer.md       # Reviewer role prompt + heuristics
│   └── meta.md           # Meta role prompt + heuristics
└── workflows/
    └── spec-to-code-v2.yaml
```

**Knowledge base scope:**
- `.flows/prompts/` — node task-level knowledge (task instructions per node)
- `.flows/memory/` — role-level knowledge (role prompts + heuristics, updated by reflect)

### Workflow Nodes

**Total: 14 nodes**

1. `fetch_issue` — GitHub bash executor, fetches issue content
2. `create_branch` — GitHub bash executor, creates feature branch
3. `ba` — BA node, produces `clarify.md` from issue
4. `human_domain_gate` — Human gate, reviews domain model
5. `architect` — Architect node, produces `design.md`
6. `human_testability_gate` — Human gate, reviews testability
7. `test_arch` — Test-architect node, produces `test-design.md`
8. `developer` — Developer node (TDD), produces implementation
9. `human_code_review` — Human gate, reviews code (DDD focus)
10. `test_developer` — Test-developer node, produces tests + runs them → `test-results.md`
11. `human_test_review` — Human gate, reviews test results
12. `final_review` — Final reviewer node (implicit join)
13. `reflect` — Meta node, produces `reflect.md` + updates memory files
14. `create_pr` — GitHub bash executor, creates PR

### Workflow YAML

```yaml
version: "1"

nodes:
  # GitHub setup
  fetch_issue:
    role: github
    executor: bash
    command: scripts/fetch-issue.sh
    inputs: {issue_url: issue-url.txt}
    outputs: {requirement: requirement.md, repo_root: repo-root.txt}

  create_branch:
    role: github
    executor: bash
    command: scripts/create-branch.sh
    inputs: {requirement: requirement.md, repo_root: repo-root.txt, issue_url: issue-url.txt}
    outputs: {branch_name: branch-name.txt}

  # Domain track
  ba:
    role: ba
    prompt: prompts/clarity.md
    executor: opencode
    inputs:
      issue: issue.md
      requirement: requirement.md
      memory_ba: memory/ba.md
      domain_review: domain-review.md    # Optional on retry
      reject_reason: reject-reason.txt   # Optional on retry
    outputs: {clarify_md: clarify.md}

  human_domain_gate:
    role: human
    prompt: prompts/domain-review.md
    executor: human
    inputs: {clarify: clarify.md}
    outputs: {verdict: verdict.txt, domain_review: domain-review.md}

  architect:
    role: architect
    prompt: prompts/design.md
    executor: opencode
    inputs:
      clarify: clarify.md
      memory_architect: memory/architect.md
      testability_review: testability-review.md  # Optional on retry
      reject_reason: reject-reason.txt           # Optional on retry
    outputs: {design_md: design.md}

  human_testability_gate:
    role: human
    prompt: prompts/testability-review.md
    executor: human
    inputs: {design: design.md, clarify: clarify.md}
    outputs: {verdict: verdict.txt, testability_review: testability-review.md}

  test_arch:
    role: test-arch
    prompt: prompts/test-design.md
    executor: opencode
    inputs:
      design: design.md
      clarify: clarify.md
      memory_test_arch: memory/test-arch.md
    outputs: {test_design_md: test-design.md}

  # Developer track (sequential first)
  developer:
    role: developer
    prompt: prompts/implement.md
    executor: opencode
    inputs:
      design: design.md
      test_design: test-design.md
      repo_root: repo-root.txt
      memory_developer: memory/developer.md
      code_review: code-review.md       # Optional on retry
      reject_reason: reject-reason.txt  # Optional on retry
    outputs: {implementation_md: implementation.md}

  human_code_review:
    role: human
    prompt: prompts/code-review.md
    executor: human
    inputs: {implementation: implementation.md, design: design.md}
    outputs: {verdict: verdict.txt, code_review: code-review.md}

  # Test-developer track (sequential second)
  test_developer:
    role: test-developer
    prompt: prompts/test-develop.md
    executor: opencode
    inputs:
      test_design: test-design.md
      design: design.md
      memory_test_developer: memory/test-developer.md
      test_review: test-review.md        # Optional on retry
      reject_reason: reject-reason.txt   # Optional on retry
    outputs: {test_results_md: test-results.md}

  human_test_review:
    role: human
    prompt: prompts/test-review.md
    executor: human
    inputs: {test_results: test-results.md, test_design: test-design.md}
    outputs: {verdict: verdict.txt, test_review: test-review.md}

  # Final
  final_review:
    role: reviewer
    prompt: prompts/final-review.md
    executor: opencode
    inputs:
      implementation: implementation.md
      code_review: code-review.md
      test_results: test-results.md
      test_review: test-review.md
      clarify: clarify.md
      design: design.md
      memory_reviewer: memory/reviewer.md
    outputs: {final_review_md: final-review.md}

  reflect:
    role: meta
    prompt: prompts/reflect.md
    executor: opencode
    inputs:
      clarify: clarify.md
      design: design.md
      implementation: implementation.md
      test_results: test-results.md
      code_review: code-review.md
      test_review: test-review.md
      final_review: final-review.md
      memory_ba: memory/ba.md
      memory_architect: memory/architect.md
      memory_test_arch: memory/test-arch.md
      memory_developer: memory/developer.md
      memory_test_developer: memory/test-developer.md
    outputs:
      reflect_md: reflect.md
      memory_ba_updated: memory/ba.md
      memory_architect_updated: memory/architect.md
      memory_test_arch_updated: memory/test-arch.md
      memory_developer_updated: memory/developer.md
      memory_test_developer_updated: memory/test-developer.md
      memory_reviewer_updated: memory/reviewer.md

  # GitHub final
  create_pr:
    role: github
    executor: bash
    command: scripts/create-pr.sh
    inputs:
      requirement: requirement.md
      branch_name: branch-name.txt
      repo_root: repo-root.txt
      implementation: implementation.md
      review: final-review.md
      test_report: test-results.md
    outputs: {pr_url: pr-url.txt}

transitions:
  - from: __start__
    to: fetch_issue

  - from: fetch_issue
    to: create_branch

  - from: create_branch
    to: ba

  - from: ba
    to: human_domain_gate

  - from: human_domain_gate
    to: architect
    when: verdict == "APPROVED"

  - from: human_domain_gate
    to: ba
    when: verdict == "BLOCKED"

  - from: architect
    to: human_testability_gate

  - from: human_testability_gate
    to: test_arch
    when: verdict == "APPROVED"

  - from: human_testability_gate
    to: architect
    when: verdict == "BLOCKED"

  - from: test_arch
    to: developer

  - from: developer
    to: human_code_review

  - from: human_code_review
    to: test_developer
    when: verdict == "APPROVED"

  - from: human_code_review
    to: developer
    when: verdict == "BLOCKED"

  - from: test_developer
    to: human_test_review

  - from: human_test_review
    to: final_review
    when: verdict == "APPROVED"

  - from: human_test_review
    to: test_developer
    when: verdict == "BLOCKED"

  - from: final_review
    to: reflect

  - from: reflect
    to: create_pr

  - from: create_pr
    to: __end__
```

### Transitions

**Retry loops:**
- `human_domain_gate BLOCKED → ba` (with `domain-review.md` + `reject-reason.txt`)
- `human_testability_gate BLOCKED → architect` (with `testability-review.md` + `reject-reason.txt`)
- `human_code_review BLOCKED → developer` (with `code-review.md` + `reject-reason.txt`)
- `human_test_review BLOCKED → test_developer` (with `test-review.md` + `reject-reason.txt`)

**Sequential track execution:**
- `test_arch → developer → human_code_review → test_developer → human_test_review`
- Developer track executes first, test track second (sequential, not parallel)

**Implicit join:**
- `final_review` inputs include artifacts from both tracks
- Sequential execution ensures both exist before reaching `final_review`

### Prompt Templates

All prompts follow the same pattern:

```markdown
# <Role> — <Task>

## Role
Read your role prompt and learned heuristics from `memory/<role>.md`.

## Task
<Specific task instructions>

## Input
{Processed by PromptProcessor}

## Output
{Processed by PromptProcessor}

## Feedback (if retry)
If <review artifact> and `reject-reason.txt` are provided, address the specific issues raised.
```

**Gate prompts:**

```markdown
# Human — <Gate Name>

## Task
Review <artifact> for:
- <Criterion 1>
- <Criterion 2>
- <Criterion 3>

## Outputs
Write two files:

1. **<review-artifact>.md** — Your review notes documenting:
   - Issues found (if any)
   - What passed review
   - Specific feedback for upstream node

2. **verdict.txt** — First line must be exactly: `APPROVED` or `BLOCKED`

## Reject Reason
If BLOCKED, also use `--reject --reject-reason "<specific issues>"` CLI flag to provide immediate feedback.
```

### Memory Files

Each memory file has structure:

```markdown
# <Role> — Role Prompt & Memory

## Role prompt
Standing instructions for this role. What it must do, must not do, how it reasons.

## Heuristics learned
(Appended by reflect node after each run)
- observation: "<pattern observed>"
  run_date: "<date>"
  context: "<run context>"

## Anti-patterns to avoid
(Appended by reflect node)
- pattern: "<anti-pattern description>"
  reason: "<why it fails>"
  discovered_in: "<run identifier>"
```

### Reflect Node Behavior

**Inputs:**
- All run artifacts (`clarify.md`, `design.md`, `implementation.md`, `test-results.md`, `code-review.md`, `test-review.md`, `final-review.md`)
- All memory files (current state)

**Outputs:**
- `reflect.md` — run summary, gate statistics, what worked, what degraded, carry-forward
- Updated memory files (7 outputs: one per role)

**Memory update mechanism:**
Reflect outputs updated memory content. PromptProcessor writes to memory files via standard output mechanism.

## Implementation Notes

### No Engine Changes Required

Design relies on existing engine infrastructure:
- Human approval nodes (`executor: human`)
- Conditional transitions (`when: verdict == "APPROVED"`)
- MAX_REJECTS=5 limit (reuse existing)
- PromptProcessor for optional inputs (skip missing files)
- Bash executor for GitHub nodes

### Optional Input Handling

PromptProcessor already handles missing files gracefully (logs warning, skips). Nodes with retry inputs will:
- First run: processor skips `domain_review`, `reject_reason` (files don't exist)
- Retry run: processor reads both files after human gate BLOCKED

### Gate Verdict Format

Gate nodes write `verdict.txt` with first line exactly `APPROVED` or `BLOCKED`. Transition conditions use:
```yaml
when: verdict == "APPROVED"
when: verdict == "BLOCKED"
```

Engine reads first line of `verdict.txt` for condition evaluation.

### Track Sequencing

Spec describes parallel tracks, but implementation uses sequential execution:
- Developer track first (`developer → human_code_review`)
- Test track second (`test_developer → human_test_review`)
- Both must APPROVED before `final_review` (implicit join via inputs)

Rationale: Sequential execution is simpler, no engine changes, implicit join works naturally.

## Files to Create

1. `.flows/workflows/spec-to-code-v2.yaml` — workflow definition
2. `.flows/prompts/clarity.md` — BA node prompt
3. `.flows/prompts/domain-review.md` — human domain gate prompt
4. `.flows/prompts/design.md` — architect node prompt
5. `.flows/prompts/testability-review.md` — human testability gate prompt
6. `.flows/prompts/test-design.md` — test_arch node prompt
7. `.flows/prompts/implement.md` — developer node prompt
8. `.flows/prompts/code-review.md` — human code review gate prompt
9. `.flows/prompts/test-develop.md` — test_developer node prompt
10. `.flows/prompts/test-review.md` — human test review gate prompt
11. `.flows/prompts/final-review.md` — final reviewer node prompt
12. `.flows/prompts/reflect.md` — reflect node prompt
13. `.flows/memory/ba.md` — BA role prompt + memory (initial)
14. `.flows/memory/architect.md` — Architect role prompt + memory
15. `.flows/memory/test-arch.md` — Test-architect role prompt + memory
16. `.flows/memory/developer.md` — Developer role prompt + memory
17. `.flows/memory/test-developer.md` — Test-developer role prompt + memory
18. `.flows/memory/reviewer.md` — Reviewer role prompt + memory
19. `.flows/memory/meta.md` — Meta role prompt + memory
20. `.flows/roles/test-developer.yaml` — role config (if not exists)
21. `.flows/roles/reviewer.yaml` — role config (if not exists)

## Testing

- Dry-run with `--dry-run` flag to verify prompt assembly
- Manual run through each gate with APPROVED/BLOCKED decisions
- Verify retry loops: BLOCKED → upstream node receives feedback
- Verify reflect updates memory files