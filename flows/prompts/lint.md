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