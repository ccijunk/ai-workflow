# Modify Code

Implement the requirement from issue #1: add role binding config, add role prompt.

## Task

Read requirement.md to understand what needs to be implemented.

The requirement is to add:
1. Role binding configuration (role can have bindings for specific nodes)
2. Role prompt system (prompt resolution: node → role binding → role default)

## Implementation

Modify the following files:
1. `src/flowctl/models.py` - add RoleBinding model and update RoleConfig
2. Create role config files in `.flows/roles/` directory

## Execute with bash tool:

1. `cd /home/laeq/code/harness/ai-workflow && git add -A`
2. `cd /home/laeq/code/harness/ai-workflow && git commit -m "feat: implement role binding config from issue #1"`

## Output

Use write tool to create `changes.md` describing the changes made.