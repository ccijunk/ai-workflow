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