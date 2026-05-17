# Workflow Quality Fixes Design

**Date**: 2026-05-17
**Status**: Approved
**Scope**: Fix 14 issues in spec-to-code workflow for producing high-quality code

---

## Overview

The spec-to-code workflow has structural problems that allow incomplete implementations to pass review. This design fixes critical workflow logic, adds quality gates, improves prompt specificity, and ensures proper artifact flow between nodes.

---

## Issues Addressed

### Critical (4)
- C1: Fix artifacts not consumed by implement node
- C2: PARTIAL verdict not handled in workflow
- C3: Fix phases only plan, never execute fixes
- C4: Review references non-existent AC section numbers

### High Priority (5)
- H1: No linting/type-checking quality gate
- H2: Review lacks actual git diff input
- H3: No coverage threshold in testing
- H4: No iteration limit on fix loops
- H5: Hardcoded paths in prompts

### Medium Priority (5)
- M1: Create PR uses hardcoded content
- M2: Explore phase doesn't verify understanding
- M3: Human approval lacks structured reject format
- M4: Reflect phase output unused
- M5: No security review step

---

## Phase 1: Clarify Stage

### 1.1 clarity.md - Structured Output Format

**File**: `.flows/prompts/clarity.md`

**Changes**: Add explicit output format with tables.

```markdown
## Output Format

Write clarified requirements to `clarify.md` with sections:

## Requirement Summary
[One paragraph summary of the issue/request]

## Sub-Requirements
| ID | Requirement | Priority |
|----|-------------|----------|
| R1 | ... | High |
| R2 | ... | Medium |
| R3 | ... | Low |

## Acceptance Criteria
| ID | Criteria | Type |
|----|----------|------|
| AC1 | ... | Functional |
| AC2 | ... | Functional |
| NF1 | ... | Non-Functional |
| EC1 | ... | Edge Case |

## Dependencies
[List of dependencies identified]

## Questions for Stakeholder
[Any clarifying questions]
```

**Rationale**: Standardized format allows review.md to parse criteria correctly.

---

### 1.2 human-confirm-clarify.md - Structured Reject Format

**File**: `.flows/prompts/human-confirm-clarify.md`

**Changes**: Add structured format for reject feedback.

```markdown
## Decision

If requirements are clear:
- Write "yes" to `clarify-approved.txt`

If requirements need more clarification:
- Write "no" to `clarify-approved.txt`
- Write to `reject-reason.txt` with STRUCTURED feedback:

```
## Issues Found

1. [Issue 1 - specific gap or ambiguity]
2. [Issue 2 - specific gap or ambiguity]

## Required Clarifications

1. [Question 1]
2. [Question 2]

## Suggestions

- [Optional suggestion 1]
```
```

**Rationale**: Structured feedback enables reclarify.md to address specific issues.

---

## Phase 2: Design Stage

### 2.1 review.md - Adaptive Acceptance Criteria Check

**File**: `.flows/prompts/review.md`

**Changes**: Make Phase 3 adaptive to clarify.md format.

```markdown
### Phase 3: Acceptance Criteria Check

**IMPORTANT**: clarify.md may use different section names. Look for:
- "Acceptance Criteria" section with criteria entries
- Any table with criteria/requirements
- Functional, Non-Functional, and Edge Case markers if present

For each criteria found:
1. Verify it with evidence (file paths, test names, or code references)
2. Mark: ✅ Verified / ❌ Not met / ⚠️ Needs verification

DO NOT assume AC1-AC9, NF1-NF4, EC1-EC6 format.
Read the actual clarify.md and extract criteria from whatever format it uses.
```

**Rationale**: Prevents review failures when clarify.md uses different formatting.

---

## Phase 3: Implement Stage

### 3.1 spec-to-code.yaml - Fix Artifacts Consumption

**File**: `.flows/workflows/spec-to-code.yaml`

**Changes**: Add fix inputs to implement node.

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

**Rationale**: When looping back from fix nodes, implement needs to know what to fix.

---

### 3.2 implement.md - Handle Fix Iterations

**File**: `.flows/prompts/implement.md`

**Changes**: Add conditional handling for fix inputs.

```markdown
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
2. Make the necessary changes
3. Run tests to verify changes work

If neither fix file exists, proceed with normal implementation.

## Verification (REQUIRED)

After implementing or fixing, you MUST verify:
1. Run tests: `uv run pytest tests/ -v`
2. Run lint: `uv run ruff check .`
3. Run type check: `uv run mypy src/` (if applicable)

If any fail, FIX THEM before writing implementation.md.
```

**Rationale**: Enables actual fix execution when looping back.

---

### 3.3 fix-test.md - Execute Fixes

**File**: `.flows/prompts/fix-test.md`

**Changes**: Instruct to execute fixes, not just plan.

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
6. If tests still fail, diagnose and fix again

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
- "no" if tests still failing after attempts
```

**Rationale**: Ensures fixes are actually applied, breaking infinite planning loops.

---

### 3.4 fix-review.md - Execute Fixes

**File**: `.flows/prompts/fix-review.md`

**Changes**: Instruct to execute fixes.

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

- Address Critical issues first
- You MUST actually edit/write code files, not just document a plan
- Run tests after each fix to verify changes work

## Output Format

Write to `fix-review.md` with:
- Issues addressed (with file:line references)
- Changes made (with file:line references)
- Test results after fixes
- Remaining issues (if any)
```

**Rationale**: Same as fix-test.md - ensures actual execution.

---

### 3.5 spec-to-code.yaml - Fix Loop Transitions

**File**: `.flows/workflows/spec-to-code.yaml`

**Changes**: Update fix loop transitions.

```yaml
# OLD: fix_test → implement
# NEW: fix_test → testing (fix-test executes fixes directly)

transitions:
  - from: testing
    to: review
    when: pass == "yes"
  
  - from: testing
    to: fix_test
    when: pass == "no"
  
  - from: fix_test
    to: testing
    when: pass == "yes"    # CHANGED
  
  - from: fix_test
    to: fix_test
    when: pass == "no"     # NEW: retry fixing
  
  - from: review
    to: reflect
    when: verdict == "PASS"
  
  - from: review
    to: fix_review
    when: verdict == "FAIL"
  
  - from: review
    to: fix_review
    when: verdict == "PARTIAL"  # NEW
  
  - from: fix_review
    to: testing          # CHANGED: verify fixes via testing
```

**Rationale**: Fix nodes now execute fixes and self-validate, then go to testing.

---

### 3.6 create-branch-issue.md - Remove Hardcoded Paths

**File**: `.flows/prompts/create-branch-issue.md`

**Changes**: Use repo_root input variable.

**Before**:
```markdown
The repo root is: /home/laeq/code/harness/ai-workflow
```

**After**:
```markdown
Read `repo-root.txt` to get the repository root path.

## Steps
1. cd to the path from repo-root.txt
2. Extract issue number from issue-url.txt
...
```

**Rationale**: Portability across different machines/repos.

---

### 3.7 explore.md - Verification Checklist

**File**: `.flows/prompts/explore.md`

**Changes**: Add verification checklist.

```markdown
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

**Rationale**: Forces concrete exploration, not vague descriptions.

---

## Phase 4: Testing Stage

### 4.1 lint.md - New Node

**File**: `.flows/prompts/lint.md` (NEW)

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

**Rationale**: Catches code quality issues before testing.

---

### 4.2 spec-to-code.yaml - Add Lint Node

**File**: `.flows/workflows/spec-to-code.yaml`

**Changes**: Add lint node and transitions.

```yaml
nodes:
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

transitions:
  - from: implement
    to: lint
  
  - from: lint
    to: testing
    when: lint_pass == "yes"
  
  - from: lint
    to: fix_lint
    when: lint_pass == "no"
  
  - from: fix_lint
    to: lint    # Re-check after fix
```

**Rationale**: Quality gate before testing.

---

### 4.3 fix-lint.md - New Node

**File**: `.flows/prompts/fix-lint.md` (NEW)

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

**Rationale**: Enables lint fixes with verification.

---

### 4.4 testing.md - Coverage Threshold

**File**: `.flows/prompts/testing.md`

**Changes**: Add coverage requirement.

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

**Rationale**: Ensures test quality, not just test passing.

---

### 4.5 spec-to-code.yaml - Iteration Limit Documentation

**File**: `.flows/workflows/spec-to-code.yaml`

**Changes**: Add warning comment.

```yaml
# WARNING: Fix loops have no iteration limit
# Recommended: If fix_test or fix_review loops >10 times, 
# consider manual intervention or failing the workflow

transitions:
  - from: fix_test
    to: testing
    when: pass == "yes"
  
  - from: fix_test
    to: fix_test
    when: pass == "no"  # NOTE: May loop infinitely
```

**Rationale**: Warns about potential infinite loops.

---

## Phase 5: Review Stage

### 5.1 review.md - Add Git Diff Input

**File**: `.flows/prompts/review.md`

**Changes**: Use code-diff.diff to verify actual changes.

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

**Rationale**: Prevents fake implementations that only exist in documentation.

---

### 5.2 review.md - Security Check Section

**File**: `.flows/prompts/review.md`

**Changes**: Add Phase 6 for security review.

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

**Rationale**: Explicit security review prevents vulnerabilities.

---

### 5.3 reflect.md - Generate Git Diff

**File**: `.flows/prompts/reflect.md`

**Changes**: Add git diff generation before review.

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

**Rationale**: Generates diff before review so review can verify actual changes.

---

### 5.4 spec-to-code.yaml - Review Inputs Update

**File**: `.flows/workflows/spec-to-code.yaml`

**Changes**: Add clarify, design, code_diff inputs.

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
    code_diff: code-diff.diff     # NEW (from reflect)
  outputs:
    review_md: review.md
    verdict: verdict.txt
```

**Rationale**: Review needs full context to verify properly.

---

### 5.5 spec-to-code.yaml - Update Reflect Position

**File**: `.flows/workflows/spec-to-code.yaml`

**Changes**: Reflect runs before review (to generate diff).

```yaml
# OLD: review → reflect → create_pr
# NEW: testing → reflect → review → create_pr

transitions:
  - from: testing
    to: reflect
    when: pass == "yes"
  
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
    when: verdict == "PARTIAL"
```

**Rationale**: Reflect generates diff, review consumes it.

---

## Phase 6: PR Stage

### 6.1 create-pr-issue.md - Use Workflow Artifacts

**File**: `.flows/prompts/create-pr-issue.md`

**Changes**: Build PR from workflow outputs.

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

**Rationale**: PR content reflects actual work, not hardcoded template.

---

## File Changes Summary

| File | Action | Phase |
|------|--------|-------|
| `.flows/prompts/clarity.md` | Modify | 1 |
| `.flows/prompts/human-confirm-clarify.md` | Modify | 1 |
| `.flows/prompts/review.md` | Modify | 2, 5 |
| `.flows/prompts/implement.md` | Modify | 3 |
| `.flows/prompts/fix-test.md` | Modify | 3 |
| `.flows/prompts/fix-review.md` | Modify | 3 |
| `.flows/prompts/create-branch-issue.md` | Modify | 3 |
| `.flows/prompts/explore.md` | Modify | 3 |
| `.flows/prompts/lint.md` | Create | 4 |
| `.flows/prompts/fix-lint.md` | Create | 4 |
| `.flows/prompts/testing.md` | Modify | 4 |
| `.flows/prompts/reflect.md` | Modify | 5 |
| `.flows/prompts/create-pr-issue.md` | Modify | 6 |
| `.flows/workflows/spec-to-code.yaml` | Modify | 3, 4, 5 |

**Total**: 13 modified, 2 created

---

## Implementation Order

1. Phase 1: Clarify prompts (clarity.md, human-confirm-clarify.md)
2. Phase 2: Review prompt partial fix (review.md)
3. Phase 3: Implement/fix prompts + workflow YAML
4. Phase 4: Lint node + testing coverage
5. Phase 5: Review inputs + reflect + PARTIAL transition
6. Phase 6: PR prompt

Each phase commits changes, can be run in isolation.

---

## Testing Strategy

After all changes:
1. Run workflow with dry-run: `flowctl run --dry-run --issue "url" .flows/workflows/spec-to-code.yaml`
2. Verify new nodes (lint, fix_lint) execute
3. Verify fix loops transition correctly
4. Verify PARTIAL verdict handled
5. Run full workflow with real issue to verify end-to-end