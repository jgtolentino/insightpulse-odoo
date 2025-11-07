#!/bin/bash
# Audit all GitHub Actions workflows for missing or inadequate triggers

set -e

echo "📋 Auditing GitHub Actions Workflows"
echo "===================================="
echo ""

WORKFLOW_DIR=".github/workflows"
MANUAL_ONLY=()
MISSING_TRIGGERS=()
WELL_CONFIGURED=()

# Check each workflow file
shopt -s nullglob
for workflow in "$WORKFLOW_DIR"/*.yml "$WORKFLOW_DIR"/*.yaml; do
  [ -f "$workflow" ] || continue

  filename=$(basename "$workflow")

  # Check if it has an 'on:' section
  if ! grep -q "^on:" "$workflow"; then
    MISSING_TRIGGERS+=("$filename")
    continue
  fi

  # Extract the 'on:' section and check for various trigger types
  has_schedule=$(grep -A 20 "^on:" "$workflow" | grep -c "schedule:" || true)
  has_push=$(grep -A 20 "^on:" "$workflow" | grep -c "push:" || true)
  has_pull=$(grep -A 20 "^on:" "$workflow" | grep -c "pull_request:" || true)
  has_workflow_call=$(grep -A 20 "^on:" "$workflow" | grep -c "workflow_call:" || true)
  has_workflow_run=$(grep -A 20 "^on:" "$workflow" | grep -c "workflow_run:" || true)
  has_issue_comment=$(grep -A 20 "^on:" "$workflow" | grep -c "issue_comment:" || true)
  has_repository_dispatch=$(grep -A 20 "^on:" "$workflow" | grep -c "repository_dispatch:" || true)
  has_release=$(grep -A 20 "^on:" "$workflow" | grep -c "release:" || true)
  has_dispatch=$(grep -A 20 "^on:" "$workflow" | grep -c "workflow_dispatch:" || true)

  total_triggers=$((has_schedule + has_push + has_pull + has_workflow_call + has_workflow_run + has_issue_comment + has_repository_dispatch + has_release))

  if [ "$total_triggers" -eq 0 ] && [ "$has_dispatch" -gt 0 ]; then
    MANUAL_ONLY+=("$filename")
  elif [ "$total_triggers" -eq 0 ] && [ "$has_dispatch" -eq 0 ]; then
    MISSING_TRIGGERS+=("$filename")
  else
    WELL_CONFIGURED+=("$filename")
  fi
done

# Report results
echo "🟢 Well-Configured Workflows (${#WELL_CONFIGURED[@]}):"
echo "These workflows have automated triggers (schedule, push, pull_request, or workflow_call)"
for wf in "${WELL_CONFIGURED[@]}"; do
  echo "  ✓ $wf"
done
echo ""

echo "🟡 Manual-Only Workflows (${#MANUAL_ONLY[@]}):"
echo "These workflows ONLY have workflow_dispatch (manual trigger)"
for wf in "${MANUAL_ONLY[@]}"; do
  echo "  ⚠ $wf"
done
echo ""

echo "🔴 Missing Triggers (${#MISSING_TRIGGERS[@]}):"
echo "These workflows have NO triggers configured"
for wf in "${MISSING_TRIGGERS[@]}"; do
  echo "  ❌ $wf"
done
echo ""

echo "===================================="
echo "Summary:"
echo "  Total workflows: $((${#WELL_CONFIGURED[@]} + ${#MANUAL_ONLY[@]} + ${#MISSING_TRIGGERS[@]}))"
echo "  Well-configured: ${#WELL_CONFIGURED[@]}"
echo "  Manual-only: ${#MANUAL_ONLY[@]}"
echo "  Missing triggers: ${#MISSING_TRIGGERS[@]}"
echo ""

if [ ${#MANUAL_ONLY[@]} -gt 0 ] || [ ${#MISSING_TRIGGERS[@]} -gt 0 ]; then
  echo "⚠️  Action needed: $((${#MANUAL_ONLY[@]} + ${#MISSING_TRIGGERS[@]})) workflow(s) need review"
  exit 1
else
  echo "✅ All workflows are properly configured"
  exit 0
fi
