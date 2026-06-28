#!/usr/bin/env bash
#
# Add 'automated' label to PR after successful review
#
# Usage: add-review-label.sh PR_NUMBER
#
# Outputs:
#   Adds 'automated' label if not already present
#

set -euo pipefail

PR_NUMBER="${1:?PR number is required}"
GITHUB_REPOSITORY="${GITHUB_REPOSITORY:?GITHUB_REPOSITORY is required}"

# Add 'automated' label to indicate bot has reviewed
# Only add the label if it is not already present
EXISTING_LABELS=$(gh pr view "$PR_NUMBER" --json labels -q '.labels[].name')
if ! echo "$EXISTING_LABELS" | grep -qx "automated"; then
  if ! gh api "repos/${GITHUB_REPOSITORY}/labels/automated" > /dev/null 2>&1; then
    gh api --method POST "repos/${GITHUB_REPOSITORY}/labels" -f name='automated' -f color='0e8a16' -f description='Reviewed by automation' > /dev/null
  fi
  gh pr edit "$PR_NUMBER" --add-label "automated"
  echo "✅ Added 'automated' label to PR"
else
  echo "ℹ️ 'automated' label already present on PR"
fi
