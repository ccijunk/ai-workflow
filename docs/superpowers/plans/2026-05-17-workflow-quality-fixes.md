# Workflow Quality Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix 14 workflow quality issues to produce high-quality code through proper artifact flow, quality gates, and rigorous review.

**Architecture:** Modify prompts to add structured outputs and verification steps. Add lint node between implement and testing. Fix workflow transitions for PARTIAL verdict and fix loops. Update review to verify actual files via git diff.

**Tech Stack:** YAML workflow definitions, Markdown prompts, flowctl CLI, pytest, ruff, coverage

---

## File Structure

### Modified Prompts (13 files)
- `.flows/prompts/clarity.md` - Add structured output tables
- `.flows/prompts/human-confirm-clarify.md` - Add structured reject format
- `.flows/prompts/review.md` - Add adaptive AC check, git diff verification, security section
- `.flows/prompts/implement.md` - Add fix iteration handling, verification step
- `.flows/prompts/fix-test.md` - Change from planning to executing fixes
- `.flows/prompts/fix-review.md` - Change from planning to executing fixes
- `.flows/prompts/create-branch-issue.md` - Remove hardcoded path, read repo-root.txt
- `.flows/prompts/explore.md` - Add verification checklist
- `.flows/prompts/testing.md` - Add coverage threshold (80%)
- `.flows/prompts/reflect.md` - Add git diff generation before review
- `.flows/prompts/create-pr-issue.md` - Build PR from workflow artifacts

### New Prompts (2 files)
- `.flows/prompts/lint.md` - Lint/type/format checks
- `.flows/prompts/fix-lint.md` - Execute lint fixes

### Workflow YAML (1 file)
- `.flows/workflows/spec-to-code.yaml` - Add lint nodes, fix inputs to implement, fix transitions, PARTIAL handling, reflect position

---

## Task 1: Clarify Stage Prompts

**Files:**
- Modify: `.flows/prompts/clarity.md`
- Modify: `.flows/prompts/human-confirm-clarify.md`

- [ ] **Step 1: Update clarity.md output format**

Replace the entire output section in `.flows/prompts/clarity.md`:

```markdown
# Clarify Requirements

You are the business analyst role. Clarify and refine the requirements.

## Input

Read the requirement from `requirement.md` in the run directory.

## Task

1. Analyze the requirement
2. Identify ambiguities or missing details
3. Break down into specific sub-requirements
4. Define acceptance criteria with explicit IDs
5. Identify dependencies

## Output Format

Write clarified requirements to `clarify.md` with sections:

## Requirement Summary
[One paragraph summary of the issue/request]

## Sub-Requirements
| ID | Requirement | Priority |
|----|-------------|----------|
| R1 | [First sub-requirement] | High |
| R2 | [Second sub-requirement] | Medium |
| R3 | [Third sub-requirement] | Low |

## Acceptance Criteria
| ID | Criteria | Type |
|----|----------|------|
| AC1 | [Functional criterion 1] | Functional |
| AC2 | [Functional criterion 2] | Functional |
| NF1 | [Non-functional criterion] | Non-Functional |
| EC1 | [Edge case criterion] | Edge Case |

## Dependencies
[List of dependencies identified]

## Questions for Stakeholder
[Any clarifying questions]
```

- [ ] **Step 2: Update human-confirm-clarify.md reject format**

Replace the decision section in `.flows/prompts/human-confirm-clarify.md`:

```markdown
# Human Confirm Clarify

You are the human approver role. Review the clarified requirements.

## Input

Read `clarify.md` to see the clarified requirements.

## Decision

If requirements are clear and complete:
- Write "yes" to `clarify-approved.txt`

If requirements need more clarification:
- Write "no" to `clarify-approved.txt`
- Write to `reject-reason.txt` with STRUCTURED feedback:

```
## Issues Found

1. [Issue 1 - specific gap or ambiguity]
2. [Issue 2 - specific gap or ambiguity]

## Required Clarifications

1. [Question 1 that needs answering]
2. [Question 2 that needs answering]

## Suggestions

- [Optional suggestion 1]
- [Optional suggestion 2]
```

## Output

Write your decision to the appropriate output file.
```

- [ ] **Step 3: Commit clarify stage changes**

```bash
git add .flows/prompts/clarity.md .flows/prompts/human-confirm-clarify.md
git commit -m "feat: add structured output format to clarify prompts"
```

---

## Task 2: Review Prompt Adaptive AC Check

**Files:**
- Modify: `.flows/prompts/review.md` (Phase 3 section)

- [ ] **Step 1: Update Phase 3 acceptance criteria check**

Replace lines 29-35 in `.flows/prompts/review.md`:

```markdown
### Phase 3: Acceptance Criteria Check

**IMPORTANT**: clarify.md may use different section names. Look for:
- "Acceptance Criteria" section with criteria entries
- Any table with criteria/requirements
- Functional, Non-Functional, and Edge Case markers if present

For each criteria found in clarify.md:
1. Verify it with evidence (file paths, test names, or code references)
2. Mark: ✅ Verified / ❌ Not met / ⚠️ Needs verification

DO NOT assume AC1-AC9, NF1-NF4, EC1-EC6 format.
Read the actual clarify.md and extract criteria from whatever format it uses.
```

- [ ] **Step 2: Commit review prompt update**

```bash
git add .flows/prompts/review.md
git commit -m "fix: make review.md adaptive to clarify.md format"
```

---

## Task 3: Implement and Fix Prompts

**Files:**
- Modify: `.flows/prompts/implement.md`
- Modify: `.flows/prompts/fix-test.md`
- Modify: `.flows/prompts/fix-review.md`
- Modify: `.flows/prompts/explore.md`

- [ ] **Step 1: Update implement.md for fix iterations**

Replace `.flows/prompts/implement.md`:

```markdown
# Implement Phase

You are the developer role. Implement the code changes based on the design and test plan.

## Input

Read ALL input files provided:
- `explore.md` - codebase exploration results
- `docs/test-design.md` - test strategy
- `docs/design.md` - technical design
- `repo-root.txt` - repository root path
- `fix.md` - (if exists) test failure analysis and fix plan
- `fix-review.md` - (if exists) review findings to address

## Critical First Step

If `fix.md` exists in run directory, you are in a FIX iteration:
1. Read fix.md to understand what tests failed
2. Apply the planned fixes using edit/write tools
3. Run tests: `uv run pytest tests/ -v`
4. If tests still fail, diagnose and fix again

If `fix-review.md` exists, you are addressing review feedback:
1. Read each issue identified in fix-review.md
2. Make the necessary changes using edit/write tools
3. Run tests to verify changes work

If neither fix file exists, proceed with normal implementation.

## Task (Normal Implementation)

1. Create implementation plan in `implementation.md`
2. **Write/Edit actual code files** in the repo:
   - Use edit tool to modify existing files
   - Use write tool to create new files
   - Follow the design.md architecture
   - Ensure code is complete and functional
3. Write tests as specified in test-design.md
4. Run tests to verify implementation: `uv run pytest tests/ -v`
5. Commit changes with bash tool:
   - `git add -A`
   - `git commit -m "feat: implement <feature-name>"`

## Verification (REQUIRED)

After implementing or fixing, you MUST verify:
1. Run tests: `uv run pytest tests/ -v`
2. Run lint: `uv run ruff check .`
3. Run type check: `uv run mypy src/` (if applicable)

If any fail, FIX THEM before writing implementation.md.

## Output Format

Create two files:

1. `implementation.md` - Implementation plan with:
   - Files modified/created
   - Key code changes
   - Test coverage

2. `changes.md` - Summary of actual changes:
   - What was implemented
   - Files changed
   - Commit hash

## Important

- You MUST write/edit actual code files, not just plan
- Code must be complete and functional
- Tests must pass after implementation
- Commit after successful implementation
```

- [ ] **Step 2: Update fix-test.md to execute fixes**

Replace `.flows/prompts/fix-test.md`:

```markdown
# Fix Test Failures

## Input

Read `test-report.md` to understand test failures.

## Task

1. Analyze the failing tests
2. Identify root cause for each failure
3. **USE EDIT/WRITE TOOLS TO FIX THE CODE FILES**
4. Run tests again: `uv run pytest tests/ -v --tb=short`
5. If tests pass, write pass.txt with "yes"
6. If tests still fail, diagnose and fix again (max 3 attempts)

## Important

- You MUST actually edit/write code files, not just document a plan
- After each fix attempt, run tests to verify
- Continue until tests pass or you've tried 3 different approaches

## Output Format

Write to `fix.md` with:
- What tests were failing (file:line references)
- Root cause analysis
- What changes you made (file:line references)
- Test results after fix

Write to `pass.txt`:
- "yes" if all tests now pass
- "no" if tests still failing after 3 attempts
```

- [ ] **Step 3: Update fix-review.md to execute fixes**

Replace `.flows/prompts/fix-review.md`:

```markdown
# Fix Review Issues

## Input

Read `review.md` to understand review findings.
Read `fix.md` if it exists (may have test fixes already applied).

## Task

1. Analyze each issue in review.md
2. Categorize by severity (Critical, High, Medium)
3. **USE EDIT/WRITE TOOLS TO FIX THE CODE FILES**
4. Run tests: `uv run pytest tests/ -v`
5. Run lint: `uv run ruff check .`

## Important

- Address Critical issues first, then High, then Medium
- You MUST actually edit/write code files, not just document a plan
- Run tests after each fix to verify changes work

## Output Format

Write to `fix-review.md` with:
- Issues addressed (with file:line references)
- Changes made (with file:line references)
- Test results after fixes
- Remaining issues (if any)
```

- [ ] **Step 4: Update explore.md verification**

Replace the output section in `.flows/prompts/explore.md`:

```markdown
# Explore Phase

You are the developer role. Explore the codebase to understand existing patterns.

## Input

Read the design document provided in the inputs section below.

## Task

1. Use glob/grep to find relevant existing code
2. Identify patterns to follow
3. Find files that need modification
4. Understand existing architecture
5. Document findings in explore.md

## Output Format

Write to `explore.md` with:
- **Files Found**: List each file with brief description of relevance
- **Patterns Identified**: Specific code patterns with file:line references
- **Files to Modify**: List with justification
- **Dependencies**: External/internal dependencies
- **Potential Conflicts**: Specific concerns

## Verification Checklist

Before writing explore.md, verify:
- [ ] Found at least 3 relevant existing files
- [ ] Identified specific patterns (not just "I explored")
- [ ] Listed specific files to modify with reasons
- [ ] Documented file:line references for patterns found
```

- [ ] **Step 5: Commit implement and fix prompts**

```bash
git add .flows/prompts/implement.md .flows/prompts/fix-test.md .flows/prompts/fix-review.md .flows/prompts/explore.md
git commit -m "feat: implement prompts now execute fixes, not just plan"
```

---

## Task 4: Create-Branch Prompt Fix

**Files:**
- Modify: `.flows/prompts/create-branch-issue.md`

- [ ] **Step 1: Remove hardcoded path**

Read `.flows/prompts/create-branch-issue.md` and find hardcoded path reference. Replace with:

```markdown
Read `repo-root.txt` to get the repository root path.

## Steps
1. cd to the path from repo-root.txt
2. Extract issue number from issue-url.txt
...
```

(Remove any hardcoded `/home/laeq/code/harness/ai-workflow` paths)

- [ ] **Step 2: Commit branch prompt fix**

```bash
git add .flows/prompts/create-branch-issue.md
git commit -m "fix: remove hardcoded repo path from create-branch prompt"
```

---

## Task 5: Testing Stage Prompts

**Files:**
- Create: `.flows/prompts/lint.md`
- Create: `.flows/prompts/fix-lint.md`
- Modify: `.flows/prompts/testing.md`

- [ ] **Step 1: Create lint.md prompt**

```markdown
# Lint Phase

## Input

Read `implementation.md` to understand what was implemented.

## Task

Run code quality checks:

1. **Lint check**: `uv run ruff check .`
2. **Type check**: `uv run mypy src/` (if mypy configured)
3. **Format check**: `uv run ruff format --check .`

## Output

Write to `lint-pass.txt`:
- "yes" if all checks pass with no errors
- "no" if any check has errors

Write to `lint-report.md` with:
- Linting errors found (with file:line)
- Type errors found (with file:line)
- Formatting issues found
- Fix suggestions for each error

## Thresholds

- Zero lint errors required
- Zero type errors required  
- Formatting must match project style
```

- [ ] **Step 2: Create fix-lint.md prompt**

```markdown
# Fix Lint Issues

## Input

Read `lint-report.md` to understand lint/type/format errors.

## Task

1. Analyze each error in lint-report.md
2. **USE EDIT TOOLS TO FIX THE CODE FILES**
3. Run lint again: `uv run ruff check .`
4. Run type check: `uv run mypy src/` (if configured)
5. Run format: `uv run ruff format --check .`

## Important

- You MUST actually edit code files, not just document fixes
- Address all errors listed
- Re-run checks after fixes

## Output

Write to `lint-pass.txt`:
- "yes" if all checks now pass
- "no" if errors remain
```

- [ ] **Step 3: Update testing.md with coverage**

Replace `.flows/prompts/testing.md`:

```markdown
# Testing Phase

## Input

Read `implementation.md` to understand what was implemented.

## Task

1. Run tests with coverage:
   ```bash
   uv run pytest tests/ -v --cov=src --cov-report=term-missing --cov-fail-under=80
   ```

2. If coverage check fails (below 80%), tests FAIL
3. If any test fails, tests FAIL
4. Document all results

## Coverage Thresholds

- **Minimum overall**: 80% coverage
- **For new code**: 90% coverage expected
- **Critical paths**: Must have explicit test cases

## Output Format

Write to `test-report.md` with:
- Test results summary (pass/fail count)
- Coverage percentage
- Coverage gaps (files/functions not covered)
- Failed tests with error details
- Missing test scenarios identified

Write to `pass.txt`:
- "yes" ONLY if: all tests pass AND coverage >= 80%
- "no" if: any test fails OR coverage < 80%
```

- [ ] **Step 4: Commit testing stage prompts**

```bash
git add .flows/prompts/lint.md .flows/prompts/fix-lint.md .flows/prompts/testing.md
git commit -m "feat: add lint prompts and coverage threshold to testing"
```

---

## Task 6: Reflect Prompt Update

**Files:**
- Modify: `.flows/prompts/reflect.md`

- [ ] **Step 1: Update reflect.md for git diff generation**

Replace `.flows/prompts/reflect.md`:

```markdown
# Reflect Phase

## Input

Read `implementation.md` to understand what was implemented.
Read `repo-root.txt` to get repository root path.

## Task

1. Run git diff to capture actual changes:
   ```bash
   cd $(cat repo-root.txt)
   git diff main...HEAD > code-diff.diff
   ```
   
2. Review the diff for key decisions made
3. Summarize the implementation approach

## Output

Write to `code-diff.diff`: The actual git diff (generated by command above)

Write to `pending.diff`: Summary of key decisions and approach
```

- [ ] **Step 2: Commit reflect prompt**

```bash
git add .flows/prompts/reflect.md
git commit -m "feat: reflect.md now generates git diff before review"
```

---

## Task 7: PR Prompt Update

**Files:**
- Modify: `.flows/prompts/create-pr-issue.md`

- [ ] **Step 1: Update create-pr-issue.md to use artifacts**

Replace `.flows/prompts/create-pr-issue.md`:

```markdown
# Create Pull Request

## Input

Read these files to build PR content:
- `requirement.md` - Original issue/requirement
- `implementation.md` - What was implemented
- `test-report.md` - Testing results
- `review.md` - Review summary
- `branch-name.txt` - Branch name
- `issue-url.txt` - Issue URL (extract issue number)
- `repo-root.txt` - Repository root path

## Task

Create PR using gh CLI:

```bash
cd $(cat repo-root.txt)
gh pr create --title "<derive from requirement.md>" --body "$(cat <<'BODY'
## Summary

<extract key points from requirement.md>

## Changes

<extract from implementation.md>

## Testing

<extract from test-report.md>

## Review Notes

<extract from review.md>

Closes #<issue-number>
BODY
)"
```

## Important

- PR title should match issue title or summarize feature
- Body should be built from actual workflow artifacts
- Include test coverage information
- Include review verdict
```

- [ ] **Step 2: Commit PR prompt**

```bash
git add .flows/prompts/create-pr-issue.md
git commit -m "feat: create-pr prompt builds from workflow artifacts"
```

---

## Task 8: Review Prompt Git Diff and Security

**Files:**
- Modify: `.flows/prompts/review.md` (input section + add Phase 6)

- [ ] **Step 1: Add git diff input and verification**

Replace the input section in `.flows/prompts/review.md` (lines 5-12):

```markdown
## Input Files to Read

**REQUIRED - Read ALL of these:**
1. `clarify.md` - Clarified requirements and acceptance criteria
2. `docs/design.md` - Technical design specification
3. `implementation.md` - Implementation plan and what was done
4. `test-report.md` - Test execution results
5. `code-diff.diff` - Actual git diff of changes made

## Critical: Verify Actual Files

**MANDATORY**: Use the Read tool to verify claims in implementation.md.
DO NOT trust implementation.md at face value.

For each file claimed in implementation.md:
1. Use Read tool to open the actual file
2. Verify the code exists as described
3. Check file paths match what's in code-diff.diff

If you do not read actual files and diff, your review is INCOMPLETE.
```

- [ ] **Step 2: Add Phase 6 security check**

Add after Phase 5 in `.flows/prompts/review.md` (before Output Format section):

```markdown
### Phase 6: Security Check

Review for security issues:

1. **Secrets/Credentials**: No hardcoded passwords, API keys, tokens
2. **Input Validation**: All user inputs validated/sanitized
3. **SQL Injection**: Parameterized queries used (not string concatenation)
4. **XSS Prevention**: Output encoding applied where needed
5. **Auth/Authz**: Proper access controls implemented
6. **Data Exposure**: No sensitive data in logs/responses

For each category, mark: ✅ Secure / ❌ Vulnerable / ⚠️ Needs Review
```

- [ ] **Step 3: Commit review prompt additions**

```bash
git add .flows/prompts/review.md
git commit -m "feat: review now requires git diff verification and security check"
```

---

## Task 9: Workflow YAML Updates

**Files:**
- Modify: `.flows/workflows/spec-to-code.yaml`

- [ ] **Step 1: Add fix inputs to implement node**

Find the `implement` node (lines 79-85) and add inputs:

```yaml
implement:
  role: developer
  prompt: prompts/implement.md
  executor: opencode
  inputs:
    explore: explore.md
    test_design: docs/test-design.md
    design: docs/design.md
    repo_root: repo-root.txt
    fix: fix.md              # NEW
    fix_review: fix-review.md # NEW
  outputs:
    implementation_md: implementation.md
    changes: changes.md
```

- [ ] **Step 2: Add lint and fix_lint nodes**

Add after `implement` node definition:

```yaml
lint:
  role: developer
  prompt: prompts/lint.md
  executor: opencode
  inputs: {implementation: implementation.md}
  outputs: {lint_pass: lint-pass.txt, lint_report: lint-report.md}

fix_lint:
  role: developer
  prompt: prompts/fix-lint.md
  executor: opencode
  inputs: {lint_report: lint-report.md}
  outputs: {lint_pass: lint-pass.txt}
```

- [ ] **Step 3: Update review node inputs**

Find the `review` node (lines 100-105) and add inputs:

```yaml
review:
  role: reviewer
  prompt: prompts/review.md
  executor: opencode
  inputs:
    clarify: clarify.md           # NEW
    design: docs/design.md        # NEW
    implementation: implementation.md
    test_report: test-report.md
    code_diff: code-diff.diff     # NEW
  outputs:
    review_md: review.md
    verdict: verdict.txt
```

- [ ] **Step 4: Update transitions for lint**

Replace transitions from implement (lines 172-174):

```yaml
# WARNING: Fix loops have no iteration limit
# Recommended: If fix_test or fix_review loops >10 times,
# consider manual intervention or failing the workflow

transitions:
  - from: __start__
    to: fetch_issue

  - from: fetch_issue
    to: create_branch

  - from: create_branch
    to: clarify

  - from: clarify
    to: human_confirm_clarify

  - from: human_confirm_clarify
    to: design
    when: clarify_approved == "yes"

  - from: human_confirm_clarify
    to: reclarify
    when: clarify_approved == "no"

  - from: reclarify
    to: human_confirm_clarify

  - from: design
    to: test_design

  - from: test_design
    to: human_confirm_design

  - from: human_confirm_design
    to: explore
    when: design_approved == "yes"

  - from: human_confirm_design
    to: redesign
    when: design_approved == "no"

  - from: redesign
    to: human_confirm_design

  - from: explore
    to: implement

  # LINT GATE
  - from: implement
    to: lint

  - from: lint
    to: testing
    when: lint_pass == "yes"

  - from: lint
    to: fix_lint
    when: lint_pass == "no"

  - from: fix_lint
    to: lint

  # TESTING
  - from: testing
    to: reflect
    when: pass == "yes"

  - from: testing
    to: fix_test
    when: pass == "no"

  - from: fix_test
    to: testing
    when: pass == "yes"

  - from: fix_test
    to: fix_test
    when: pass == "no"  # NOTE: May loop infinitely

  # REVIEW (reflect generates diff before review)
  - from: reflect
    to: review

  - from: review
    to: create_pr
    when: verdict == "PASS"

  - from: review
    to: fix_review
    when: verdict == "FAIL"

  - from: review
    to: fix_review
    when: verdict == "PARTIAL"  # NEW

  - from: fix_review
    to: testing

  # PR
  - from: create_pr
    to: __end__
```

- [ ] **Step 5: Commit workflow YAML**

```bash
git add .flows/workflows/spec-to-code.yaml
git commit -m "feat: add lint gate, fix inputs, PARTIAL handling, reflect before review"
```

---

## Task 10: Verification

- [ ] **Step 1: Verify workflow loads correctly**

```bash
uv run python -c "from flowctl.loader import load_workflow; wf = load_workflow('.flows/workflows/spec-to-code.yaml'); print(f'Nodes: {len(wf.nodes)}, Transitions: {len(wf.transitions)}')"
```

Expected: `Nodes: XX, Transitions: YY` (count all nodes including new lint nodes)

- [ ] **Step 2: Run all tests**

```bash
uv run pytest tests/ -v
```

Expected: All tests pass

- [ ] **Step 3: Commit verification**

```bash
git status
git log --oneline -10
```

Expected: 10 commits from all tasks

---

## Self-Review Checklist

### Spec Coverage
- [x] C1: Fix artifacts consumed → Task 9 (implement inputs)
- [x] C2: PARTIAL handled → Task 9 (PARTIAL transition)
- [x] C3: Fix phases execute → Task 3 (fix-test.md, fix-review.md)
- [x] C4: Review adaptive AC → Task 2 (review.md Phase 3)
- [x] H1: Lint gate → Task 5, Task 9 (lint.md + nodes)
- [x] H2: Git diff input → Task 6, Task 8 (reflect.md + review inputs)
- [x] H3: Coverage threshold → Task 5 (testing.md)
- [x] H4: Iteration warning → Task 9 (workflow comment)
- [x] H5: Hardcoded paths → Task 4 (create-branch-issue.md)
- [x] M1: PR from artifacts → Task 7 (create-pr-issue.md)
- [x] M2: Explore verification → Task 3 (explore.md checklist)
- [x] M3: Structured reject → Task 1 (human-confirm-clarify.md)
- [x] M4: Reflect used → Task 6, Task 9 (reflect generates diff)
- [x] M5: Security check → Task 8 (review.md Phase 6)

### Placeholder Scan
- No TBD/TODO found
- All code steps have actual content
- All commands specified

### Type Consistency
- All file paths match spec locations
- All prompt modifications match spec content