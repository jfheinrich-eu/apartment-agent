#!/usr/bin/env bash
#
# Check if all required status checks have passed for a PR
#
# Usage: check-pr-status.sh PR_NUMBER GITHUB_REPOSITORY
#
# Environment variables:
#   ACTIONS_STEP_DEBUG - Enable debug output (optional)
#
# Outputs:
#   Sets can_review=true/false in GITHUB_OUTPUT
#

set -euo pipefail

PR_NUMBER="${1:?PR number is required}"
GITHUB_REPOSITORY="${2:?GitHub repository is required}"
ACTIONS_STEP_DEBUG="${ACTIONS_STEP_DEBUG:-false}"

# Get PR details using GitHub CLI
PR_DATA=$(gh pr view "$PR_NUMBER" --json state,isDraft,mergeable,statusCheckRollup)

# Check if PR is still open and not draft
STATE=$(echo "$PR_DATA" | jq -r '.state')
IS_DRAFT=$(echo "$PR_DATA" | jq -r '.isDraft')

if [ "$STATE" != "OPEN" ]; then
  echo "PR is not open (state: $STATE), skipping review"
  echo "can_review=false" >> "$GITHUB_OUTPUT"
  exit 0
fi

if [ "$IS_DRAFT" = "true" ]; then
  echo "PR is in draft mode, skipping review"
  echo "can_review=false" >> "$GITHUB_OUTPUT"
  exit 0
fi

# Debug: Show raw PR data
if [ "$ACTIONS_STEP_DEBUG" = "true" ]; then
  echo "DEBUG: Raw PR data:"
  echo "$PR_DATA" | jq '.'
fi

# Determine PR check state directly from `gh pr checks`, which maps to the
# checks shown in the GitHub PR UI and avoids race conditions in commit check-runs.
CHECKS_JSON=$(gh pr checks "$PR_NUMBER" --json name,state,bucket,workflow 2>/dev/null || echo "[]")

# Exclude this workflow's own checks to prevent self-pending loops.
EXTERNAL_CHECKS=$(echo "$CHECKS_JSON" | jq '[.[] | select(.workflow != "Auto Request Reviews" and .name != "Auto Review by Bot" and .name != "request-review")]')
TOTAL_EXTERNAL=$(echo "$EXTERNAL_CHECKS" | jq 'length')
PASSING_CHECKS=$(echo "$EXTERNAL_CHECKS" | jq '[.[] | select(.bucket == "pass")] | length')
PENDING_CHECKS=$(echo "$EXTERNAL_CHECKS" | jq '[.[] | select(.bucket == "pending")] | length')
FAILING_CHECKS=$(echo "$EXTERNAL_CHECKS" | jq '[.[] | select(.bucket == "fail")] | length')

echo "PR checks analysis:"
echo "  - Total external checks: $TOTAL_EXTERNAL"
echo "  - Passing: $PASSING_CHECKS"
echo "  - Pending: $PENDING_CHECKS"
echo "  - Failing: $FAILING_CHECKS"

if [ "$ACTIONS_STEP_DEBUG" = "true" ]; then
  echo "DEBUG: External checks considered for review gate:"
  echo "$EXTERNAL_CHECKS" | jq '.'
fi

if [ "$FAILING_CHECKS" -gt 0 ]; then
  echo "❌ One or more external checks are failing - skipping review"
  echo "can_review=false" >> "$GITHUB_OUTPUT"
  exit 0
fi

if [ "$PENDING_CHECKS" -gt 0 ]; then
  echo "⏳ External checks are still pending - skipping review for now"
  echo "can_review=false" >> "$GITHUB_OUTPUT"
  exit 0
fi

if [ "$TOTAL_EXTERNAL" -gt 0 ] && [ "$PASSING_CHECKS" -eq "$TOTAL_EXTERNAL" ]; then
  echo "✅ All external checks succeeded - proceeding with automated review"
  echo "can_review=true" >> "$GITHUB_OUTPUT"
  exit 0
fi

# Fallback for edge cases where no checks are reported yet.
echo "ℹ️ No external checks detected yet - skipping review for now"
echo "can_review=false" >> "$GITHUB_OUTPUT"
