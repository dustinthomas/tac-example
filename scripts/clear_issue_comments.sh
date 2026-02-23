#!/usr/bin/env bash
# Delete all comments from a GitHub issue.
# Useful for cleaning up ADW test runs.
#
# Usage: bash scripts/clear_issue_comments.sh <issue-number>

set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: bash scripts/clear_issue_comments.sh <issue-number>"
    exit 1
fi

ISSUE_NUMBER="$1"
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)

echo "Deleting all comments from issue #${ISSUE_NUMBER} in ${REPO}..."

# Fetch all comment IDs using the GraphQL node IDs
COMMENT_IDS=$(gh api "repos/${REPO}/issues/${ISSUE_NUMBER}/comments" --jq '.[].id')

if [ -z "$COMMENT_IDS" ]; then
    echo "No comments found on issue #${ISSUE_NUMBER}."
    exit 0
fi

COUNT=0
for ID in $COMMENT_IDS; do
    gh api --method DELETE "repos/${REPO}/issues/comments/${ID}" --silent
    COUNT=$((COUNT + 1))
done

echo "Deleted ${COUNT} comment(s) from issue #${ISSUE_NUMBER}."
