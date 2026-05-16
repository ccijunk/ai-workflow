# Create Pull Request

Use bash tool to create a GitHub PR for the issue.

## Task

The repo root is: /home/laeq/code/harness/ai-workflow
The branch is: issue-1-role-config

## Execute with bash tool:

`cd /home/laeq/code/harness/ai-workflow && gh pr create --title "feat: add role binding config and role prompt (issue #1)" --body "$(cat <<'BODY'
## Summary

Implements role binding configuration and role prompt system from issue #1.

## Changes

- Added RoleBinding model for node-specific role configurations
- Extended RoleConfig with bindings field
- Created role YAML files with model bindings

## Testing

Workflow tested successfully.

Closes #1
BODY
)"`

## Output

Use write tool to create `pr-url.txt` with the PR URL from gh pr create output.