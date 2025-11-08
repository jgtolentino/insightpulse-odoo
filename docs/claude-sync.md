# Claude Config Sync — Ops Runbook

## Overview
Ensures `claude.md` Section 19 stays in sync with `docs/claude-code-skills/`.

## Local

```bash
make claude:validate      # full validation
make claude:sync-check    # detect drift
make claude:sync-write    # apply updates in-place
make claude:ci-local      # validator + drift guard
```

## CI

On push/PR to main:

1. Validate + drift check
2. If `CLAUDE_SYNC_WRITE=true` and drift on push: auto-PR
3. Nightly cron ensures long-lived branches are caught via PR comments.

## Release Hygiene

After merge of a sync PR:

Optionally run `make claude:release-patch` to tag a patch.

## Troubleshooting

- Missing `gh` in CI? Add `actions/setup-gh`.
- False drift? Re-run `make claude:sync-write` and commit.
