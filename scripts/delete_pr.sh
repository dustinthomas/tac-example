#!/usr/bin/env bash
# Close a pull request and optionally delete its branch.
#
# Usage: bash scripts/delete_pr.sh <pr-number> [--delete-branch]

set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: bash scripts/delete_pr.sh <pr-number> [--delete-branch]"
    exit 1
fi

PR_NUMBER="$1"
DELETE_BRANCH="${2:-}"

echo "Closing PR #${PR_NUMBER}..."
gh pr close "$PR_NUMBER"

if [ "$DELETE_BRANCH" = "--delete-branch" ]; then
    BRANCH=$(gh pr view "$PR_NUMBER" --json headRefName -q .headRefName)
    if [ -n "$BRANCH" ]; then
        echo "Deleting branch: ${BRANCH}"
        git push origin --delete "$BRANCH" 2>/dev/null || echo "Remote branch already deleted."
        git branch -D "$BRANCH" 2>/dev/null || echo "Local branch already deleted."
    fi
fi

echo "Done."
