#!/bin/bash
# Close all duplicate health check issues created by the old health monitor

set -e

echo "🧹 Closing duplicate health check issues..."

# Get all open health check issues
ISSUES=$(gh issue list --label "health-check" --state open --json number --jq '.[].number')

if [ -z "$ISSUES" ]; then
  echo "✅ No open health check issues found"
  exit 0
fi

# Count them
COUNT=$(echo "$ISSUES" | wc -l | tr -d ' ')
echo "Found $COUNT open health check issue(s)"

# Close each one
for ISSUE_NUM in $ISSUES; do
  echo "Closing issue #$ISSUE_NUM..."

  # Add closing comment
  gh issue comment "$ISSUE_NUM" --body "✅ **Resolved: Health Monitor Updated**

This issue is being closed because:

1. The health monitor has been updated to prevent duplicate issue creation
2. It now automatically closes issues when health is restored
3. Multiple duplicate issues were created during a transient WAF/CDN issue

The root cause was a Cloudflare WAF configuration that temporarily blocked health check requests. The health monitor now handles this gracefully.

**Changes made:**
- Health monitor now checks for existing open issues before creating new ones
- Auto-closes issues when health is restored
- Added better diagnostics to distinguish between WAF and origin issues

If you continue to see health issues, they will be tracked in a single consolidated issue going forward.

*Auto-closed by health monitor cleanup script*"

  # Close the issue
  gh issue close "$ISSUE_NUM"

  echo "✓ Closed issue #$ISSUE_NUM"
done

echo ""
echo "✅ Closed $COUNT health check issue(s)"
echo "The health monitor will now create only one issue per incident."
