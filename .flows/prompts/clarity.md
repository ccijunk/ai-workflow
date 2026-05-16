# Clarify Requirements

Task: Add role configuration system to flowctl

## Requirements to Clarify

1. Change clarify node role from "architect" to "ba" (Business Analyst)
2. Add role configuration system:
   - Role has a model binding (e.g., ba uses glm-5, architect uses deepseek)
   - Role has default prompt template
   - Roles defined in `.flows/roles/<role>.yaml`

## Questions

1. What roles need configuration?
2. What models should each role use?
3. Should role configs be loaded at workflow level or global level?

## Output

Write clarification notes to `clarify.md`.
