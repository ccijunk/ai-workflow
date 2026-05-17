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