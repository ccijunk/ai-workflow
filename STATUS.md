# Flowctl Project Status

## Goal
Build flowctl workflow system with opencode executor that fetches GitHub issues, creates branches, modifies code, and creates PRs

## Constraints & Preferences
- Opencode executor must delete sessions after node completion
- Workflow must use bash tool explicitly for git/gh commands (opencode doesn't auto-detect)
- All roles use `alibaba-cn/glm-5` model
- Human confirmation nodes after clarify and design phases

## Progress
### Done
- 21 tests passing
- Opencode executor implemented with bash/write tool support
- spec-to-code.yaml: 16 nodes, 21 transitions (fetch → create_branch → clarify → design → ... → modify → testing → review → create_pr)
- Role configs created in `.flows/roles/` (ba, fetcher, architect, developer, tester, reviewer, human, meta, pr-creator)
- CLI `--issue` option for GitHub issue URL
- PRs #2, #3, #4 created via workflow execution
- GitHub CLI authenticated (`gh auth login`)
- **Session cleanup working** - sessions are properly deleted after node execution
- Prompt files now load correctly from workflow_dir (not run_dir)
- Absolute paths used for opencode --dir and cwd

### In Progress
- Nothing - session deletion issue resolved

### Blocked
- None

## Key Decisions
- Opencode requires explicit "Use bash tool to run: `git checkout -b ...`" instructions
- Workflow prompts must specify exact repo path `/home/laeq/code/harness/ai-workflow`
- `gh pr create` works when authenticated via `gh auth login --web`
- Loop structure: fix_test → modify, fix_review → modify (not back to testing)
- ExecutorInput now has `workflow_dir` field for resolving prompt/skill paths
- Absolute paths (`.resolve()`) required for opencode subprocess cwd

## Next Steps
- Run full spec-to-code workflow with real GitHub issue
- Add more node types if needed

## Critical Context
- Session deletion flow:
  1. Extract sessionID from JSON stdout (first line with "sessionID" field)
  2. Run `opencode session delete <sessionID>`
  3. Works only with absolute paths for `--dir` and `cwd`

## Relevant Files
- `/home/laeq/code/harness/ai-workflow/src/flowctl/executors/opencode.py`: OpencodeAdapter with session cleanup
- `/home/laeq/code/harness/ai-workflow/src/flowctl/executors/base.py`: ExecutorInput with workflow_dir field
- `/home/laeq/code/harness/ai-workflow/src/flowctl/runner.py`: run_workflow accepts workflow_dir
- `/home/laeq/code/harness/ai-workflow/src/flowctl/cli.py`: passes workflow_dir from wf_path
- `/home/laeq/code/harness/ai-workflow/.flows/workflows/spec-to-code.yaml`: 16-node workflow
- `/home/laeq/code/harness/ai-workflow/.flows/roles/*.yaml`: role configs