# Implement Phase

You are the developer role. Implement the code changes based on the design and test plan.

## Task

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

After implementing, you MUST verify:
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