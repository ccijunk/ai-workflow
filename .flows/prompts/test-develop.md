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