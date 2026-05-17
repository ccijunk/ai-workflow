# Create Pull Request

Create a real pull request using bash tool to run git and gh commands.

## Task

Read the repo root path from `repo-root.txt`. Then use bash tool to execute git and gh commands.

## Steps - Use bash tool for each:

1. Read repo root: The repository root path is in `repo-root.txt` (it should be /home/laeq/code/harness/ai-workflow)

2. Use bash tool: `cd /home/laeq/code/harness/ai-workflow && git checkout -b workflow-pr-test`

3. Use bash tool: `cd /home/laeq/code/harness/ai-workflow && git add -A`

4. Use bash tool: `cd /home/laeq/code/harness/ai-workflow && git commit -m "feat: implement from workflow"`

5. Use bash tool: `cd /home/laeq/code/harness/ai-workflow && git push -u origin workflow-pr-test`

6. Use bash tool: `cd /home/laeq/code/harness/ai-workflow && gh pr create --title "Workflow Test PR" --body "This PR was created automatically by the ai-workflow"`

7. Use write tool to save the PR URL to `pr-url.txt`

## Output

Use write tool to create `pr-url.txt` with the PR URL from gh pr create output.