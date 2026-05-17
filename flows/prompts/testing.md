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