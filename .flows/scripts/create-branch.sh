#!/bin/bash
set -euo pipefail

REQUIREMENT="${1:-}"
REPO_ROOT="${2:-}"
ISSUE_URL="${3:-}"

if [[ -z "$REPO_ROOT" ]]; then
    echo "Error: repo_root input is required" >&2
    exit 1
fi

if [[ -z "$ISSUE_URL" ]]; then
    echo "Error: issue_url input is required" >&2
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo "Error: git is not installed" >&2
    exit 1
fi

if [[ "$ISSUE_URL" =~ ^https://github\.com/([^/]+)/([^/]+)/issues/([0-9]+)$ ]]; then
    ISSUE_NUMBER="${BASH_REMATCH[3]}"
else
    echo "Error: Invalid GitHub issue URL format: $ISSUE_URL" >&2
    exit 1
fi

cd "$REPO_ROOT"

if [[ -n "$(git status --porcelain)" ]]; then
    echo "Error: Working directory has uncommitted changes" >&2
    git status --short >&2
    exit 1
fi

BRANCH_NAME="issue-${ISSUE_NUMBER}"

if git show-ref --verify --quiet "refs/heads/${BRANCH_NAME}"; then
    echo "Branch '$BRANCH_NAME' already exists, checking it out" >&2
    git checkout "$BRANCH_NAME"
else
    echo "Creating new branch: $BRANCH_NAME" >&2
    git checkout -b "$BRANCH_NAME"
fi

echo "$BRANCH_NAME" > "$RUN_DIR/branch-name.txt"

echo "Branch '$BRANCH_NAME' is ready" >&2