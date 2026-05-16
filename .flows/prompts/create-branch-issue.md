# Create Git Branch

Use bash tool to create a new git branch for the issue.

## Task

Read `requirement.md` to understand the issue title.
Read `issue-url.txt` to get the issue URL and extract the issue number.

The repo root is: /home/laeq/code/harness/ai-workflow

## Steps

1. Extract issue number from the URL (e.g., `https://github.com/owner/repo/issues/10` → issue number is `10`)
2. Create a branch name from the issue number and a slug derived from the issue title (e.g., issue #10 with title "Add mixed executor support" → `issue-10-mixed-executor-support`)
3. Execute with bash tool:
   - `git checkout main && git pull`
   - `git checkout -b <branch-name>`
   - `git push -u origin <branch-name>`

## Output

Use write tool to create `branch-name.txt` with the branch name you created.