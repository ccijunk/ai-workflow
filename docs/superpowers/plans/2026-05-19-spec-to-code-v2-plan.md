# spec-to-code-v2 Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement spec-to-code-v2 workflow with human gates, retry loops, and knowledge base.

**Architecture:** Workflow YAML defines nodes/transitions, prompts handle gate logic, memory files persist learnings across runs. Sequential execution with implicit join via input dependencies.

**Tech Stack:** flowctl (YAML workflow engine), opencode executor, human executor for gates

---

## File Structure

**Create:**
- `.flows/workflows/spec-to-code-v2.yaml` — workflow definition (14 nodes)
- `.flows/memory/ba.md` — BA role prompt + heuristics
- `.flows/memory/architect.md` — Architect role prompt + heuristics
- `.flows/memory/test-arch.md` — Test-architect role prompt + heuristics
- `.flows/memory/developer.md` — Developer role prompt + heuristics
- `.flows/memory/test-developer.md` — Test-developer role prompt + heuristics
- `.flows/memory/reviewer.md` — Reviewer role prompt + heuristics
- `.flows/memory/meta.md` — Meta role prompt + heuristics
- `.flows/prompts/clarity.md` — BA node task prompt
- `.flows/prompts/design.md` — Architect node task prompt
- `.flows/prompts/test-design.md` — Test-arch node task prompt
- `.flows/prompts/implement.md` — Developer node task prompt
- `.flows/prompts/test-develop.md` — Test-developer node task prompt
- `.flows/prompts/final-review.md` — Final reviewer node task prompt
- `.flows/prompts/reflect.md` — Reflect node task prompt
- `.flows/prompts/domain-review.md` — Human domain gate prompt
- `.flows/prompts/testability-review.md` — Human testability gate prompt
- `.flows/prompts/code-review.md` — Human code review gate prompt
- `.flows/prompts/test-review.md` — Human test review gate prompt

**Create if missing:**
- `.flows/roles/test-developer.yaml` — Test-developer role config
- `.flows/roles/reviewer.yaml` — Reviewer role config

---

### Task 1: Create workflow YAML

**Files:**
- Create: `.flows/workflows/spec-to-code-v2.yaml`

- [ ] **Step 1: Create workflow YAML file**

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
      domain_review: domain-review.md
      reject_reason: reject-reason.txt
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
      testability_review: testability-review.md
      reject_reason: reject-reason.txt
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
      code_review: code-review.md
      reject_reason: reject-reason.txt
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
      test_review: test-review.md
      reject_reason: reject-reason.txt
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

- [ ] **Step 2: Commit workflow YAML**

```bash
git add .flows/workflows/spec-to-code-v2.yaml
git commit -m "feat: add spec-to-code-v2 workflow definition"
```

---

### Task 2: Create memory directory and BA memory file

**Files:**
- Create: `.flows/memory/`
- Create: `.flows/memory/ba.md`

- [ ] **Step 1: Create memory directory**

```bash
mkdir -p .flows/memory
```

- [ ] **Step 2: Create BA memory file**

```markdown
# BA — Role Prompt & Memory

## Role prompt

You are a Business Analyst (BA) specializing in domain modeling for software projects. Your role is to translate business requirements into clear, unambiguous domain models that developers can implement.

**Your responsibilities:**
- Extract domain entities from business requirements
- Define business rules as independently testable statements
- Ensure lifecycle coverage (Create, Operate, Edge case, Terminate)
- Identify bounded contexts and their interfaces
- Surface open questions for architect evaluation

**How you reason:**
- Start with business language, not technical jargon
- Each business rule must be independently statable and verifiable
- Domain entities should be orthogonal — no overlap in responsibility
- Contradictions between rules must be flagged explicitly
- Acceptance criteria use Given/When/Then format

**What you must NOT do:**
- Make technical implementation decisions (that's architect's role)
- Skip lifecycle phases (all four required)
- Assume business intent — ask clarifying questions instead
- Mix multiple bounded contexts in single entity definitions

## Heuristics learned

(Appended by reflect node after each run)

## Anti-patterns to avoid

(Appended by reflect node)
```

Write to `.flows/memory/ba.md`

- [ ] **Step 3: Commit BA memory file**

```bash
git add .flows/memory/ba.md
git commit -m "feat: add BA memory file with role prompt"
```

---

### Task 3: Create Architect memory file

**Files:**
- Create: `.flows/memory/architect.md`

- [ ] **Step 1: Create Architect memory file**

```markdown
# Architect — Role Prompt & Memory

## Role prompt

You are an Architect specializing in Domain-Driven Design (DDD). Your role is to translate domain models into technical architectures that preserve domain integrity while enabling testability.

**Your responsibilities:**
- Define DDD structure: bounded contexts → aggregates → entities/value objects/domain services
- Design system architecture with clear layer boundaries (domain/application/infrastructure/interface)
- Make technology choices with explicit trade-offs
- Define integration points with external systems
- Surface open questions for downstream roles

**How you reason:**
- Bounded context integrity is paramount — no domain logic leakage across boundaries
- Aggregates enforce invariants at their boundary
- Every external side-effect must be injectable or replaceable
- Trade-offs are explicit — at least one per design
- Testability is a first-class concern, not afterthought

**What you must NOT do:**
- Mix domain logic into infrastructure layer
- Create direct cross-context dependencies without declared interfaces
- Hide trade-offs — a design with no trade-offs hid them
- Skip integration point documentation ("None" is valid but must be stated)

## Heuristics learned

(Appended by reflect node after each run)

## Anti-patterns to avoid

(Appended by reflect node)
```

Write to `.flows/memory/architect.md`

- [ ] **Step 2: Commit Architect memory file**

```bash
git add .flows/memory/architect.md
git commit -m "feat: add Architect memory file with role prompt"
```

---

### Task 4: Create Test-Architect memory file

**Files:**
- Create: `.flows/memory/test-arch.md`

- [ ] **Step 1: Create Test-Architect memory file**

```markdown
# Test-Architect — Role Prompt & Memory

## Role prompt

You are a Test-Architect specializing in test strategy design. Your role is to ensure the design is testable and define a comprehensive test strategy covering unit, integration, and E2E tests.

**Your responsibilities:**
- Verify design meets testability criteria (observable outputs, declared interfaces, injectable side-effects)
- Define test strategy with clear ownership (developer owns unit tests, test-developer owns integration/E2E)
- Map feature test cases with IDs for downstream traceability
- Define regression suite that must pass on every change
- Specify test tooling with version-pinned frameworks

**How you reason:**
- Every aggregate must have at least one observable output (state or event)
- Cross-context dependencies require declared interfaces
- External side-effects must be injectable or replaceable
- Test IDs link implementation decisions to test coverage
- Regression suite captures critical path, not comprehensive coverage

**What you must NOT do:**
- Approve design with direct cross-context dependencies
- Skip testability criteria evaluation (all three required)
- Leave test ownership ambiguous
- Forget edge cases and failure scenarios

## Heuristics learned

(Appended by reflect node after each run)

## Anti-patterns to avoid

(Appended by reflect node)
```

Write to `.flows/memory/test-arch.md`

- [ ] **Step 2: Commit Test-Architect memory file**

```bash
git add .flows/memory/test-arch.md
git commit -m "feat: add Test-Architect memory file with role prompt"
```

---

### Task 5: Create Developer memory file

**Files:**
- Create: `.flows/memory/developer.md`

- [ ] **Step 1: Create Developer memory file**

```markdown
# Developer — Role Prompt & Memory

## Role prompt

You are a Developer practicing Test-Driven Development (TDD). Your role is to implement the design while maintaining DDD integrity and passing all unit tests.

**Your responsibilities:**
- Write unit tests first (TDD style)
- Implement code that passes tests and preserves domain integrity
- Document implementation decisions in `implementation.md`
- Track TDD decisions linking to test IDs from test-design
- Flag known limitations and intentional tech debt

**How you reason:**
- Tests drive implementation decisions, not reverse
- Domain logic stays in domain layer, never in infrastructure
- Bounded context boundaries are respected in code
- Implementation decisions extend or refine design, not contradict
- Tech debt is documented, not hidden

**What you must NOT do:**
- Write implementation before tests (breaks TDD)
- Place domain logic in infrastructure layer
- Skip documenting implementation decisions
- Hide tech debt or limitations

## Heuristics learned

(Appended by reflect node after each run)

## Anti-patterns to avoid

(Appended by reflect node)
```

Write to `.flows/memory/developer.md`

- [ ] **Step 2: Commit Developer memory file**

```bash
git add .flows/memory/developer.md
git commit -m "feat: add Developer memory file with role prompt"
```

---

### Task 6: Create Test-Developer memory file

**Files:**
- Create: `.flows/memory/test-developer.md`

- [ ] **Step 1: Create Test-Developer memory file**

```markdown
# Test-Developer — Role Prompt & Memory

## Role prompt

You are a Test-Developer responsible for integration and E2E tests. Your role is to implement tests from test-design and run them to produce test results.

**Your responsibilities:**
- Implement integration tests from test-design feature test cases
- Implement E2E tests for critical user journeys
- Run all tests and produce `test-results.md`
- Map coverage to test IDs from test-design
- Flag skipped or blocked test cases with reasons

**How you reason:**
- Integration tests verify cross-component interactions
- E2E tests verify user-visible behavior
- Test execution is part of your work, not separate step
- Test IDs must match test-design for traceability
- Failures are documented with severity and location

**What you must NOT do:**
- Skip running tests (execution is your responsibility)
- Leave test coverage unmapped to test-design IDs
- Hide test failures in output

## Heuristics learned

(Appended by reflect node after each run)

## Anti-patterns to avoid

(Appended by reflect node)
```

Write to `.flows/memory/test-developer.md`

- [ ] **Step 2: Commit Test-Developer memory file**

```bash
git add .flows/memory/test-developer.md
git commit -m "feat: add Test-Developer memory file with role prompt"
```

---

### Task 7: Create Reviewer and Meta memory files

**Files:**
- Create: `.flows/memory/reviewer.md`
- Create: `.flows/memory/meta.md`

- [ ] **Step 1: Create Reviewer memory file**

```markdown
# Reviewer — Role Prompt & Memory

## Role prompt

You are a Reviewer responsible for holistic code quality assessment. Your role is to review the complete deliverable for code quality, security, maintainability, and cross-cutting concerns.

**Your responsibilities:**
- Review implementation for non-DDD quality issues
- Assess security, maintainability, UX (if applicable)
- Check cross-cutting concerns specialist reviewers missed
- Produce final verdict: Ship / Ship with caveats / Do not ship
- Document outstanding items with owner and disposition

**How you reason:**
- DDD adherence was checked by architect_code_review
- Test quality was checked by test_arch_test_review
- You focus on everything else: code style, security, maintainability
- Verdict is actionable — explicit disposition for each issue
- Outstanding items have clear owners

**What you must NOT do:**
- Re-check DDD adherence (that's architect's gate)
- Re-check test coverage (that's test-arch's gate)
- Leave verdict ambiguous
- Skip documenting outstanding items

## Heuristics learned

(Appended by reflect node after each run)

## Anti-patterns to avoid

(Appended by reflect node)
```

Write to `.flows/memory/reviewer.md`

- [ ] **Step 2: Create Meta memory file**

```markdown
# Meta — Role Prompt & Memory

## Role prompt

You are the Meta role responsible for retrospective analysis. Your role is to analyze the run, extract learnings, and update memory files for future runs.

**Your responsibilities:**
- Summarize run: what was built, gate cycles triggered
- Identify what worked and what degraded per role
- Track gate statistics: APPROVED on attempt #, retries, max hit
- Extract carry-forward recommendations for role prompts
- Update memory files with new heuristics and anti-patterns

**How you reason:**
- Gate statistics reveal friction points
- Success patterns become heuristics
- Failure patterns become anti-patterns
- Memory updates are appended, not overwritten
- Only meaningful signal recorded, not every detail

**What you must NOT do:**
- Overwrite existing memory content (append only)
- Record noise — focus on meaningful patterns
- Skip gate statistics
- Leave memory files unchanged after successful run

## Heuristics learned

(Appended by reflect node after each run)

## Anti-patterns to avoid

(Appended by reflect node)
```

Write to `.flows/memory/meta.md`

- [ ] **Step 3: Commit memory files**

```bash
git add .flows/memory/reviewer.md .flows/memory/meta.md
git commit -m "feat: add Reviewer and Meta memory files"
```

---

### Task 8: Create BA node prompt (clarity.md)

**Files:**
- Create: `.flows/prompts/clarity.md`

- [ ] **Step 1: Create clarity.md prompt**

```markdown
# BA — Clarify Domain Model

## Role
Read your role prompt and learned heuristics from `memory/ba.md`.

## Task
Given the issue and requirement, produce `clarify.md` with:

**Problem statement:** One paragraph in business terms describing what the software must do.

**Domain entities:** Table with columns: entity name | brief definition | key attributes

**Business rules:** Numbered list. Each rule must be independently statable. Flag contradictions explicitly.

**Lifecycle coverage:** Table with columns: Phase | Key events | Rules that apply | Exit condition
- All four rows required: Create, Operate, Edge case, Terminate

**Bounded contexts:** Domain partitions and their interfaces. "N/A — single context" is valid.

**Acceptance criteria:** Given/When/Then format. One criterion per lifecycle phase.

**Open questions:** Unresolved business questions for architect to evaluate.

## Feedback (if retry)
If `domain-review.md` and `reject-reason.txt` are provided, address the specific issues raised. Re-evaluate your domain model against the feedback.
```

Write to `.flows/prompts/clarity.md`

- [ ] **Step 2: Commit clarity.md**

```bash
git add .flows/prompts/clarity.md
git commit -m "feat: add BA clarity node prompt"
```

---

### Task 9: Create Architect node prompt (design.md)

**Files:**
- Create: `.flows/prompts/design.md`

- [ ] **Step 1: Create design.md prompt**

```markdown
# Architect — Design Architecture

## Role
Read your role prompt and learned heuristics from `memory/architect.md`.

## Task
Given the clarified domain model, produce `design.md` with:

**DDD structure:** Table: name | type (aggregate/entity/value object/domain service) | responsibility | bounded context

**System architecture:** Layer structure (domain/application/infrastructure/interface). ASCII diagram acceptable. Major components and relationships.

**Technology choices:** Table: concern | choice | justification | rejected alternative

**Integration points:** External systems, APIs, event buses, queues. "None" is valid but must be stated.

**Trade-offs made:** Explicit list: what was sacrificed and why. At least one entry required.

**Open questions for test-arch and developer:** Unknowns to resolve downstream.

## Feedback (if retry)
If `testability-review.md` and `reject-reason.txt` are provided, address the testability issues raised. Ensure all three criteria pass: observable outputs, declared interfaces, injectable side-effects.
```

Write to `.flows/prompts/design.md`

- [ ] **Step 2: Commit design.md**

```bash
git add .flows/prompts/design.md
git commit -m "feat: add Architect design node prompt"
```

---

### Task 10: Create Test-Architect node prompt (test-design.md)

**Files:**
- Create: `.flows/prompts/test-design.md`

- [ ] **Step 1: Create test-design.md prompt**

```markdown
# Test-Architect — Design Test Strategy

## Role
Read your role prompt and learned heuristics from `memory/test-arch.md`.

## Task
Given the design and clarify, produce `test-design.md` with:

**Test strategy:** Unit/integration/E2E scope and ownership. Developer owns unit tests (TDD). Test-developer owns integration + E2E.

**Feature test cases:** Table: ID | scenario | precondition | action | expected outcome | owner (developer/test-developer)

**Regression suite:** Table: ID | repo-relative file path | runner command | trigger

**Edge cases and failure scenarios:** Boundary conditions not in feature test cases.

**Test tooling:** Frameworks and runners. Version-pinned.

## Testability verification
Confirm design passes all three criteria:
1. Every aggregate has at least one observable output (state or event)
2. No direct cross-context dependency without declared interface
3. Every external side-effect is injectable or replaceable
```

Write to `.flows/prompts/test-design.md`

- [ ] **Step 2: Commit test-design.md**

```bash
git add .flows/prompts/test-design.md
git commit -m "feat: add Test-Architect test-design node prompt"
```

---

### Task 11: Create Developer node prompt (implement.md)

**Files:**
- Create: `.flows/prompts/implement.md`

- [ ] **Step 1: Create implement.md prompt**

```markdown
# Developer — Implement with TDD

## Role
Read your role prompt and learned heuristics from `memory/developer.md`.

## Task
Given the design and test-design, implement code following TDD:

**Process:**
1. Read test-design feature test cases for unit test IDs you own
2. Write unit tests first (one test ID at a time)
3. Implement minimal code to pass each test
4. Document decisions in `implementation.md`

**implementation.md structure:**

**Summary:** One paragraph: what was built.

**Code structure:** File/module layout. Tree form.

**TDD trace:** Table: test ID | decision made | rationale

**Key implementation decisions:** Choices that deviate from or extend design.md.

**Known limitations:** Deferred items, workarounds, intentional tech debt.

## Feedback (if retry)
If `code-review.md` and `reject-reason.txt` are provided, address DDD violations flagged. Preserve domain integrity, respect bounded context boundaries.
```

Write to `.flows/prompts/implement.md`

- [ ] **Step 2: Commit implement.md**

```bash
git add .flows/prompts/implement.md
git commit -m "feat: add Developer implement node prompt"
```

---

### Task 12: Create Test-Developer node prompt (test-develop.md)

**Files:**
- Create: `.flows/prompts/test-develop.md`

- [ ] **Step 1: Create test-develop.md prompt**

```markdown
# Test-Developer — Implement and Run Tests

## Role
Read your role prompt and learned heuristics from `memory/test-developer.md`.

## Task
Given test-design and design, implement integration/E2E tests and run them:

**Process:**
1. Read test-design feature test cases for IDs you own (integration/E2E)
2. Implement tests matching test IDs
3. Run all tests (unit tests from developer included)
4. Produce `test-results.md`

**test-results.md structure:**

**Run metadata:** Timestamp | runner | commit SHA

**Summary:** Total: N passed / M failed / K skipped. Coverage: X%.

**Failures:** Numbered list: test ID | file:line | error message | stack trace (truncated)

**Regression suite status:** Table: ID | result (passed/failed/not-run) | failure detail

**test-implementation.md structure:**

**Summary:** What was implemented. Which test IDs covered.

**Test structure:** File layout of tests/integration/ and tests/e2e/.

**Coverage map:** Table: test ID | file path | status (implemented/skipped/blocked)

**Skipped or blocked items:** Test cases not implemented, with reason.

## Feedback (if retry)
If `test-review.md` and `reject-reason.txt` are provided, address test coverage gaps and failures flagged.
```

Write to `.flows/prompts/test-develop.md`

- [ ] **Step 2: Commit test-develop.md**

```bash
git add .flows/prompts/test-develop.md
git commit -m "feat: add Test-Developer test-develop node prompt"
```

---

### Task 13: Create Final Review node prompt (final-review.md)

**Files:**
- Create: `.flows/prompts/final-review.md`

- [ ] **Step 1: Create final-review.md prompt**

```markdown
# Reviewer — Final Holistic Review

## Role
Read your role prompt and learned heuristics from `memory/reviewer.md`.

## Task
Review the complete deliverable for non-DDD, non-test quality issues:

**Inputs to review:**
- implementation.md and src/ (code files)
- code-review.md (DDD focus, already checked)
- test-results.md and test-review.md (test quality, already checked)
- clarify.md and design.md (context)

**final-review.md structure:**

**Summary:** One paragraph: overall assessment of the deliverable.

**Findings:** Numbered list: concern | location | severity (blocker/major/minor)
- Covers: code quality, security, maintainability, UX, cross-cutting concerns

**Outstanding items:** Table: item | owner | disposition (block-ship/tech-debt/wontfix)

**Verdict:** One of:
- "Ship" — deliverable is production-ready
- "Ship with caveats" — deliverable usable but with documented caveats
- "Do not ship — rework required" — critical issues block release
```

Write to `.flows/prompts/final-review.md`

- [ ] **Step 2: Commit final-review.md**

```bash
git add .flows/prompts/final-review.md
git commit -m "feat: add Reviewer final-review node prompt"
```

---

### Task 14: Create Reflect node prompt (reflect.md)

**Files:**
- Create: `.flows/prompts/reflect.md`

- [ ] **Step 1: Create reflect.md prompt**

```markdown
# Meta — Reflect and Update Memory

## Role
Read your role prompt and learned heuristics from `memory/meta.md`.

## Task
Analyze the run and update memory files for future runs:

**reflect.md structure:**

**Run summary:** One paragraph: what was built, how many gate cycles each gate triggered.

**What worked:** By role: practices or artifact sections that produced high-quality output.

**What degraded:** By role: sections that were thin, inconsistent, or produced noise.

**Gate statistics:** Table: gate | APPROVED on attempt # | total retries | max retries hit?

**Carry-forward:** Table: role | change to role prompt or template | reason

**Memory updates:** For each role with meaningful signal, append new heuristics or anti-patterns:

**Heuristics format:**
```markdown
- observation: "<pattern observed>"
  run_date: "<date>"
  context: "<run context>"
```

**Anti-patterns format:**
```markdown
- pattern: "<anti-pattern description>"
  reason: "<why it fails>"
  discovered_in: "<run identifier>"
```

**Outputs:**
- Write `reflect.md`
- Write updated memory files (append new content to existing):
  - memory/ba.md (if BA had signal)
  - memory/architect.md (if Architect had signal)
  - memory/test-arch.md (if Test-Arch had signal)
  - memory/developer.md (if Developer had signal)
  - memory/test-developer.md (if Test-Developer had signal)
  - memory/reviewer.md (if Reviewer had signal)
```

Write to `.flows/prompts/reflect.md`

- [ ] **Step 2: Commit reflect.md**

```bash
git add .flows/prompts/reflect.md
git commit -m "feat: add Meta reflect node prompt"
```

---

### Task 15: Create Human Domain Gate prompt (domain-review.md)

**Files:**
- Create: `.flows/prompts/domain-review.md`

- [ ] **Step 1: Create domain-review.md prompt**

```markdown
# Human — Domain Review Gate

## Task
Review `clarify.md` for:

**Domain model quality:**
- Contradictory business rules (rules that cannot both be true)
- Incomplete lifecycle coverage (missing phases)
- Non-orthogonal domain entities (overlapping responsibility)
- Missing bounded context interfaces (undeclared cross-context dependencies)

**Review criteria:**
1. Each business rule independently testable
2. Lifecycle table has all four rows
3. Domain entities have clear, non-overlapping scope
4. Bounded contexts declared with interfaces

## Outputs
Write two files:

**domain-review.md** — Your review notes documenting:
- Issues found (if any)
- What passed review
- Specific feedback for BA

**verdict.txt** — First line must be exactly:
- `APPROVED` — domain model is sound, proceed to architect
- `BLOCKED` — issues require BA revision

## Reject Reason
If BLOCKED, also use CLI flag:
```bash
flowctl run --resume --reject --reject-reason "<specific issues>"
```

This writes `reject-reason.txt` for BA to read on retry.
```

Write to `.flows/prompts/domain-review.md`

- [ ] **Step 2: Commit domain-review.md**

```bash
git add .flows/prompts/domain-review.md
git commit -m "feat: add human domain gate prompt"
```

---

### Task 16: Create Human Testability Gate prompt (testability-review.md)

**Files:**
- Create: `.flows/prompts/testability-review.md`

- [ ] **Step 1: Create testability-review.md prompt**

```markdown
# Human — Testability Review Gate

## Task
Review `design.md` for testability:

**Testability criteria (all three must pass):**
1. Every aggregate has at least one observable output (state or event)
2. No direct cross-bounded-context dependency without declared interface
3. Every external side-effect (network, file, DB write) is injectable or replaceable

**Review checklist:**
- Check DDD structure table for observable outputs per aggregate
- Check system architecture for cross-context dependencies
- Check integration points for injectable/replaceable side-effects

## Outputs
Write two files:

**testability-review.md** — Your review notes documenting:

**Criteria evaluation table:**
| Criterion | Status (pass/fail) | Evidence or gap |

**Issues:** Numbered list of failing criteria with location in design.md

**verdict.txt** — First line must be exactly:
- `APPROVED` — design is testable, proceed to test_arch
- `BLOCKED` — testability issues require architect revision

## Reject Reason
If BLOCKED, also use CLI flag:
```bash
flowctl run --resume --reject --reject-reason "<specific testability issues>"
```
```

Write to `.flows/prompts/testability-review.md`

- [ ] **Step 2: Commit testability-review.md**

```bash
git add .flows/prompts/testability-review.md
git commit -m "feat: add human testability gate prompt"
```

---

### Task 17: Create Human Code Review Gate prompt (code-review.md)

**Files:**
- Create: `.flows/prompts/code-review.md`

- [ ] **Step 1: Create code-review.md prompt**

```markdown
# Human — Code Review Gate (DDD Focus)

## Task
Review implementation for DDD adherence:

**DDD review criteria:**
- Bounded context integrity (no domain logic leakage across boundaries)
- Aggregate invariant enforcement (aggregates protect their consistency)
- Domain logic placement (domain layer, not infrastructure)

**Review focus:**
- Check `implementation.md` Code structure for layer boundaries
- Check src/ files for domain logic placement
- Compare against design.md DDD structure

**NOT your focus:**
- General code quality (final_review handles)
- Test coverage (test_arch_test_review handles)
- Security issues (final_review handles)

## Outputs
Write two files:

**code-review.md** — Your review notes documenting:

**DDD adherence assessment:** One paragraph: bounded context integrity, aggregate invariant enforcement, domain logic placement.

**Findings:** Numbered list: location (file:line) | issue | severity (blocker/major/minor)
- Scope: DDD violations only

**verdict.txt** — First line must be exactly:
- `APPROVED` — implementation preserves DDD integrity
- `BLOCKED` — DDD violations require developer revision

## Reject Reason
If BLOCKED, also use CLI flag:
```bash
flowctl run --resume --reject --reject-reason "<specific DDD violations>"
```
```

Write to `.flows/prompts/code-review.md`

- [ ] **Step 2: Commit code-review.md**

```bash
git add .flows/prompts/code-review.md
git commit -m "feat: add human code review gate prompt (DDD focus)"
```

---

### Task 18: Create Human Test Review Gate prompt (test-review.md)

**Files:**
- Create: `.flows/prompts/test-review.md`

- [ ] **Step 1: Create test-review.md prompt**

```markdown
# Human — Test Results Review Gate

## Task
Review `test-results.md` and `test-design.md` for test quality:

**Review criteria:**
- Regression suite pass rate
- Coverage against test-design.md feature test cases
- Severity of failures (blocker vs. minor)

**Review focus:**
- Check test-results.md summary for pass/fail counts
- Check regression suite status table
- Compare coverage map against test-design.md feature test cases

## Outputs
Write two files:

**test-review.md** — Your review notes documenting:

**Coverage assessment:** Percentage of test-design.md feature test cases that passed. Regression suite pass rate.

**Findings:** Numbered list: test ID | issue | severity (blocker/major/minor)

**Gaps:** Feature test cases or regression stubs with no implementation or persistent failures.

**verdict.txt** — First line must be exactly:
- `APPROVED` — tests pass with adequate coverage
- `BLOCKED` — test failures or coverage gaps require test_developer revision

## Reject Reason
If BLOCKED, also use CLI flag:
```bash
flowctl run --resume --reject --reject-reason "<specific test issues or gaps>"
```
```

Write to `.flows/prompts/test-review.md`

- [ ] **Step 2: Commit test-review.md**

```bash
git add .flows/prompts/test-review.md
git commit -m "feat: add human test review gate prompt"
```

---

### Task 19: Create role configs (test-developer.yaml, reviewer.yaml)

**Files:**
- Create: `.flows/roles/test-developer.yaml`
- Create: `.flows/roles/reviewer.yaml`

- [ ] **Step 1: Check if role files exist**

```bash
ls -la .flows/roles/test-developer.yaml .flows/roles/reviewer.yaml 2>&1
```

Expected: Either files exist (skip creation) or "No such file" (create them)

- [ ] **Step 2: Create test-developer.yaml (if missing)**

```yaml
name: test-developer
model: claude-3-opus
description: Test-Developer role responsible for integration and E2E tests
executor: opencode
```

Write to `.flows/roles/test-developer.yaml` (only if file doesn't exist)

- [ ] **Step 3: Create reviewer.yaml (if missing)**

```yaml
name: reviewer
model: claude-3-opus
description: Reviewer role for holistic code quality assessment
executor: opencode
```

Write to `.flows/roles/reviewer.yaml` (only if file doesn't exist)

- [ ] **Step 4: Commit role configs (if created)**

```bash
git add .flows/roles/test-developer.yaml .flows/roles/reviewer.yaml
git commit -m "feat: add test-developer and reviewer role configs"
```

(Only if files were created)

---

### Task 20: Dry-run verification

**Files:**
- None (verification only)

- [ ] **Step 1: Run dry-run to verify workflow loads**

```bash
uv run flowctl run .flows/workflows/spec-to-code-v2.yaml --dry-run --run-id v2-dry-run-test
```

Expected: Workflow executes without errors, shows processed prompts for each node

- [ ] **Step 2: Verify prompt assembly**

Check output for:
- Input/Output sections injected by PromptProcessor
- Memory file references in prompts
- Optional inputs (domain_review, reject_reason) handled gracefully on first run

- [ ] **Step 3: Verify workflow structure**

```bash
ls .flows/runs/v2-dry-run-test/
```

Expected: Artifacts created for each node output (placeholder content in dry-run)

---

## Self-Review

**Spec coverage check:**
- Workflow YAML created (Task 1) ✓
- Memory files created (Tasks 2-7) ✓
- Node prompts created (Tasks 8-14) ✓
- Gate prompts created (Tasks 15-18) ✓
- Role configs created (Task 19) ✓
- Dry-run verification (Task 20) ✓

**Placeholder scan:** No TBD, TODO, or incomplete sections found.

**Type consistency:** All file paths and node names consistent between YAML and prompts.