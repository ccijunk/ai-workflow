# Create Pull Request

Create a real pull request using git and gh commands.

## Task

Read the repo root path from `repo-root.txt`. Then execute git commands from that directory.

Steps:

1. Read repo root: The repository root path is in `repo-root.txt`
2. Check current branch: `cd {repo_root} && git branch --show-current`
3. Create new branch: `cd {repo_root} && git checkout -b test-pr-workflow`
4. Create test file: Use the write tool to create `docs/test-pr-output.md` with content from `test-output.txt`
5. Add and commit: `cd {repo_root} && git add docs/test-pr-output.md && git commit -m "test: add test PR output from workflow"`
6. Push to remote: `cd {repo_root} && git push -u origin test-pr-workflow`
7. Create PR: `cd {repo_root} && gh pr create --title "Test PR from ai-workflow" --body "Automated test PR from workflow execution"`

## Output

Write the actual PR URL (from gh pr create output) to `pr-url.txt`.