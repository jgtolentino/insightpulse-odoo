# MCP Tool Enforcer - Constitution

> Governing principles for tool selection and enforcement in Claude Code sessions.

## Purpose

The MCP Tool Enforcer ensures Claude Code uses the most appropriate tools for each operation, preferring MCP (Model Context Protocol) tools over raw shell commands when available, while maintaining graceful degradation and user workflow continuity.

---

## Core Principles

### 1. Tool Hierarchy Principle

**Always prefer the most powerful, purpose-built tool available.**

| Priority | Tool Type | Examples |
|----------|-----------|----------|
| 1 (Highest) | MCP Tools | `mcp__filesystem__read`, `mcp__search__grep` |
| 2 | Built-in Tools | `Read`, `Glob`, `Grep`, `Edit`, `Write` |
| 3 | Shell Commands | `cat`, `find`, `grep`, `sed` |

**Rationale**: MCP tools provide:
- Structured input/output
- Better error handling
- Richer context for the model
- Permission-aware operations
- Audit trail capabilities

### 2. Explicit Selection Principle

**Tool selection must be transparent and justifiable.**

- Never silently fall back to inferior tools
- Always log tool selection decisions when multiple options exist
- Provide clear reasoning when recommending tool changes

### 3. Non-Blocking Principle

**Never break existing workflows.**

- Warnings are advisory, not blocking
- Users can override recommendations
- Existing scripts and commands continue to work
- No forced migrations

### 4. Graceful Degradation Principle

**When preferred tools are unavailable, degrade gracefully.**

Degradation tiers:
1. **MCP tool available** → Use MCP tool
2. **MCP unavailable, built-in available** → Use built-in tool
3. **Built-in unavailable** → Fall back to shell command
4. **All unavailable** → Clear error with alternatives

### 5. Evidence-Based Decisions

**All recommendations must be backed by measurable criteria.**

Metrics for tool selection:
- Success rate (higher is better)
- Token efficiency (lower is better)
- Error recovery capability
- User satisfaction ratings

### 6. Education Over Enforcement

**Teach users why certain tools are preferred.**

- Provide context for recommendations
- Link to documentation
- Show comparative examples
- Allow users to learn at their own pace

---

## Non-Negotiables

### 1. Never Break Workflows

```yaml
rule: workflow_continuity
description: Existing commands must continue to work
enforcement: hard_block
rationale: User trust requires reliability
```

### 2. Zero Configuration Required

```yaml
rule: zero_config
description: Must work out-of-box without setup
enforcement: default_behavior
rationale: Reduce adoption friction
```

### 3. Evidence-Based Recommendations

```yaml
rule: evidence_required
description: All suggestions backed by data
enforcement: soft_requirement
rationale: Build trust through transparency
```

### 4. Graceful Degradation

```yaml
rule: graceful_fallback
description: Always have a working fallback
enforcement: hard_requirement
rationale: Never leave user stuck
```

### 5. Transparent Trade-offs

```yaml
rule: transparency
description: Explain why one tool over another
enforcement: advisory
rationale: Informed users make better decisions
```

---

## Scope Definition

### In Scope

Operations where MCP tools provide clear advantages:

| Operation | Shell Command | Preferred Tool |
|-----------|---------------|----------------|
| File reading | `cat`, `head`, `tail` | `Read`, `mcp__filesystem__read` |
| File writing | `echo >`, `cat <<EOF` | `Write`, `mcp__filesystem__write` |
| File editing | `sed`, `awk` | `Edit`, `mcp__filesystem__patch` |
| File search | `find` | `Glob` |
| Content search | `grep`, `rg` | `Grep` |
| Directory listing | `ls` | `Glob` with pattern |

### Out of Scope

Operations where shell commands are appropriate:

| Operation | Reason |
|-----------|--------|
| `git` commands | Git-specific workflows |
| `npm`, `yarn`, `pnpm` | Package manager operations |
| `docker` commands | Container operations |
| `make` commands | Build system operations |
| `ssh`, `scp` | Remote operations |
| Custom scripts | User-defined automation |

---

## Decision Matrix

### When to Recommend MCP/Built-in Tools

```
IF operation == "read file" AND file_exists:
    RECOMMEND Read tool
    REASON "Structured output, better for large files"

IF operation == "search files" AND pattern_based:
    RECOMMEND Glob tool
    REASON "Faster than find, integrated results"

IF operation == "search content" AND regex_pattern:
    RECOMMEND Grep tool
    REASON "Streaming results, file type filtering"

IF operation == "edit file" AND targeted_change:
    RECOMMEND Edit tool
    REASON "Atomic operations, conflict detection"

IF operation == "write file" AND new_content:
    RECOMMEND Write tool
    REASON "Proper encoding, permission handling"
```

### When Shell Commands Are Acceptable

```
IF command in ["git", "npm", "docker", "make"]:
    ALLOW shell command
    REASON "Specialized tooling, no MCP equivalent"

IF operation == "system administration":
    ALLOW shell command
    REASON "Root operations, system-specific"

IF user explicitly requests shell:
    ALLOW shell command
    REASON "User autonomy"
```

---

## Enforcement Levels

### Level 1: Advisory (Default)

- Show recommendations in output
- Log tool selection rationale
- No blocking

### Level 2: Warning

- Display warning before shell command execution
- Suggest alternative
- Allow proceed

### Level 3: Confirmation

- Require user confirmation for shell commands
- Show comparison of options
- Log decision

### Level 4: Strict (Opt-in)

- Block shell commands when MCP alternative exists
- Require explicit override
- Audit trail

---

## User Preferences

Users can configure behavior via:

```yaml
# .claude/mcp-enforcer.yml
enforcement_level: advisory  # advisory | warning | confirmation | strict
log_decisions: true
show_alternatives: true
preferred_tools:
  file_read: mcp  # mcp | builtin | shell
  file_search: builtin
  content_search: builtin
excluded_commands:
  - git
  - docker
  - make
```

---

## Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| MCP tool usage for file ops | > 80% | Tool usage analytics |
| Search error reduction | > 50% | Error rate comparison |
| User satisfaction | > 85% | Survey/feedback |
| Workflow disruption | < 5% | Issue reports |
| Fallback success rate | > 95% | Degradation tests |

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-19 | Initial constitution |
