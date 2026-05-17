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