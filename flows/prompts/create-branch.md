# Create Git Branch

Use bash tool to create a new git branch.

## Task

The repo root is: /home/laeq/code/harness/ai-workflow

## Execute these commands with bash tool:

1. `cd /home/laeq/code/harness/ai-workflow && git checkout -b workflow-test-branch`
2. `cd /home/laeq/code/harness/ai-workflow && echo "Test change from workflow" > docs/workflow-test.md`
3. `cd /home/laeq/code/harness/ai-workflow && git add docs/workflow-test.md`
4. `cd /home/laeq/code/harness/ai-workflow && git commit -m "test: add workflow test file"`
5. `cd /home/laeq/code/harness/ai-workflow && git push -u origin workflow-test-branch`

## Output

Use write tool to create `branch-name.txt` with content: workflow-test-branch