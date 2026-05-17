# Create Branch

## Input

Read `requirement.md` to understand the issue title.
Read `issue-url.txt` to get the issue URL and extract the issue number.
Read `repo-root.txt` to get the repository root path.

## Task

1. cd to the path from repo-root.txt
2. Extract issue number from issue-url.txt
3. Create branch named `issue-<number>-<slug-from-title>`:
   ```bash
   gh issue view <number> --json title
   # Extract slug from title, lowercase, replace spaces with dashes
   git checkout -b issue-<number>-<slug>
   ```
4. Push branch to origin:
   ```bash
   git push -u origin issue-<number>-<slug>
   ```

## Output

Write to `branch-name.txt`: The created branch name (e.g., `issue-9-bash-executor`)