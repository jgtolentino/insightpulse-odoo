# TASKS — Smart Delta Engine

## Phase 0 — Repo & Guardrails
- [ ] Create repo `smart-delta-engine`
- [ ] Enforce Spec Kit presence via CI
- [ ] Add schema validation for parity JSON
- [ ] Add Smart Delta rule validator

## Phase 1 — Docs Crawler
- [ ] Implement recursive crawler (canonical URLs only)
- [ ] Add stable node ID generator
- [ ] Deduplicate by canonical URL + hash
- [ ] Persist raw crawl output (JSON)

## Phase 2 — Capability Normalization
- [ ] Define enterprise capability taxonomy
- [ ] Map leaf pages → normalized capabilities
- [ ] Tag domain (Finance, PPM, HR, Ops, Analytics)

## Phase 3 — Parity Mapping Engine
- [ ] Implement Odoo core resolver
- [ ] Implement OCA resolver (repo + module)
- [ ] Implement alt-stack resolver (Supabase, n8n)
- [ ] Compute gap_level (0–3)
- [ ] Enforce Smart Delta choice rules

## Phase 4 — Spec Kit Generator
- [ ] Generate constitution.md
- [ ] Generate prd.md
- [ ] Generate plan.md
- [ ] Generate tasks.md
- [ ] Validate machine-readability

## Phase 5 — Automation
- [ ] n8n scheduled crawl
- [ ] Parity diff detection
- [ ] Auto-draft OCA feature requests
- [ ] Slack/Mattermost notifications

## Phase 6 — CI/CD
- [ ] Reject illegal custom modules
- [ ] Reject missing OCA refs
- [ ] Enforce deterministic output hash
