#!/usr/bin/env bash
set -euo pipefail

BRANCH="bot/section19-sync"
TITLE="chore(claude): sync Section 19"
BODY="Automated sync of Section 19."

while [[ $# -gt 0 ]]; do
  case "$1" in
    --branch) BRANCH="$2"; shift 2;;
    --title)  TITLE="$2"; shift 2;;
    --body)   BODY="$2"; shift 2;;
    *) echo "Unknown arg: $1" >&2; exit 2;;
  esac
done

git config user.name "claude-sync-bot"
git config user.email "actions@users.noreply.github.com"

# generate updated section 19 into working tree
chmod +x scripts/skillsmith_sync.py
./scripts/skillsmith_sync.py --write

if git diff --quiet; then
  echo "No changes after --write; no PR required."
  exit 0
fi

git checkout -B "$BRANCH"
git add -A
git commit -m "chore(claude): sync Section 19"
git push -u origin "$BRANCH" --force

# Create or update PR
if gh pr view "$BRANCH" >/dev/null 2>&1; then
  gh pr edit "$BRANCH" --title "$TITLE" --body "$BODY"
else
  gh pr create --fill --title "$TITLE" --body "$BODY" --base main --head "$BRANCH"
fi
