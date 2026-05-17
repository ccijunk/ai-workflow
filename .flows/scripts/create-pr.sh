#!/bin/bash
set -euo pipefail

REQUIREMENT="${1:-}"
BRANCH_NAME="${2:-}"
REPO_ROOT="${3:-}"

if [[ -z "$BRANCH_NAME" ]]; then
    echo "Error: branch_name input is required" >&2
    exit 1
fi

if [[ -z "$REPO_ROOT" ]]; then
    echo "Error: repo_root input is required" >&2
    exit 1
fi

if ! command -v gh &> /dev/null; then
    echo "Error: gh CLI is not installed" >&2
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo "Error: git is not installed" >&2
    exit 1
fi

cd "$REPO_ROOT"

if ! gh auth status &> /dev/null; then
    echo "Error: gh CLI is not authenticated. Run 'gh auth login' first." >&2
    exit 1
fi

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [[ "$CURRENT_BRANCH" != "$BRANCH_NAME" ]]; then
    echo "Error: Current branch '$CURRENT_BRANCH' does not match expected branch '$BRANCH_NAME'" >&2
    exit 1
fi

REMOTE=$(git config --get branch."$BRANCH_NAME".remote || echo "origin")
if ! git ls-remote --exit-code "$REMOTE" "refs/heads/$BRANCH_NAME" &> /dev/null; then
    echo "Branch '$BRANCH_NAME' is not pushed to remote. Pushing..." >&2
    git push -u "$REMOTE" "$BRANCH_NAME"
fi

TITLE=""
if [[ -n "$REQUIREMENT" ]]; then
    TITLE=$(echo "$REQUIREMENT" | head -n 1 | sed 's/^# //')
fi

if [[ -z "$TITLE" ]]; then
    TITLE="Implement changes for $BRANCH_NAME"
fi

BODY="${REQUIREMENT}"

PR_URL=$(gh pr create --title "$TITLE" --body "$BODY" --base main 2>&1)
if [[ $? -ne 0 ]]; then
    echo "Error: Failed to create PR" >&2
    echo "$PR_URL" >&2
    exit 1
fi

echo "$PR_URL" > "$RUN_DIR/pr-url.txt"

echo "Created PR: $PR_URL" >&2