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