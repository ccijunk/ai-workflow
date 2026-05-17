#!/bin/bash
set -euo pipefail

ISSUE_URL="${1:-}"

if [[ -z "$ISSUE_URL" ]]; then
    echo "Error: issue_url input is required" >&2
    exit 1
fi

if ! command -v gh &> /dev/null; then
    echo "Error: gh CLI is not installed" >&2
    exit 1
fi

if [[ "$ISSUE_URL" =~ ^https://github\.com/([^/]+)/([^/]+)/issues/([0-9]+)$ ]]; then
    OWNER="${BASH_REMATCH[1]}"
    REPO="${BASH_REMATCH[2]}"
    ISSUE_NUMBER="${BASH_REMATCH[3]}"
else
    echo "Error: Invalid GitHub issue URL format: $ISSUE_URL" >&2
    echo "Expected: https://github.com/owner/repo/issues/123" >&2
    exit 1
fi

if ! gh auth status &> /dev/null; then
    echo "Error: gh CLI is not authenticated. Run 'gh auth login' first." >&2
    exit 1
fi

JSON_OUTPUT=$(gh issue view "$ISSUE_NUMBER" --repo "$OWNER/$REPO" --json title,body 2>&1)
if [[ $? -ne 0 ]]; then
    echo "Error: Failed to fetch issue $ISSUE_NUMBER from $OWNER/$REPO" >&2
    echo "$JSON_OUTPUT" >&2
    exit 1
fi

TITLE=$(echo "$JSON_OUTPUT" | jq -r '.title // ""')
BODY=$(echo "$JSON_OUTPUT" | jq -r '.body // ""')

{
    echo "# $TITLE"
    echo ""
    echo "$BODY"
} > "$RUN_DIR/requirement.md"

echo "Fetched issue #$ISSUE_NUMBER from $OWNER/$REPO" >&2