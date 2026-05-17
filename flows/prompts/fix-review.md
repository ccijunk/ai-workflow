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