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