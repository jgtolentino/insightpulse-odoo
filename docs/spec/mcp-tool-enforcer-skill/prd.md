# MCP Tool Enforcer - Product Requirements Document

> Version 1.0.0 | December 2025

## Executive Summary

The MCP Tool Enforcer is a policy skill for Claude Code that ensures optimal tool selection during coding sessions. It monitors command usage, recommends appropriate MCP or built-in tools over shell commands, and provides graceful degradation when preferred tools are unavailable.

### Problem Statement

Claude Code users often use shell commands (`cat`, `grep`, `find`, `sed`) when more powerful built-in or MCP tools are available. This results in:

1. **Increased token usage** - Shell output is verbose and unstructured
2. **Higher error rates** - Shell commands lack context-aware error handling
3. **Reduced capabilities** - Missing structured data, pagination, filtering
4. **Inconsistent behavior** - Platform-specific command differences

### Solution

A transparent policy layer that:
- Detects shell commands with MCP/built-in alternatives
- Recommends appropriate tools with clear rationale
- Maintains graceful degradation when tools are unavailable
- Never blocks existing workflows

---

## Target Users

### 1. Power Users

**Profile**: Experienced developers who know shell commands well

**Needs**:
- Quick recommendations without disruption
- Ability to override suggestions
- Understanding of trade-offs

**Use Case**: "I typed `cat file.txt` but Claude should use the Read tool for better handling of large files"

### 2. Beginners

**Profile**: New to Claude Code, learning the toolset

**Needs**:
- Educational guidance on available tools
- Clear explanations of why one tool over another
- Gentle nudges toward best practices

**Use Case**: "I want to search for files but don't know about Glob vs find"

### 3. Team Leads

**Profile**: Responsible for team coding standards

**Needs**:
- Configurable enforcement levels
- Analytics on tool usage
- Consistent behavior across team

**Use Case**: "I want my team to use structured tools for better code review"

### 4. Framework Maintainers

**Profile**: Building on top of Claude Code

**Needs**:
- Programmatic access to tool selection logic
- Extension points for custom tools
- Stable API for integration

**Use Case**: "I'm building a custom MCP server and want it integrated"

---

## Functional Requirements

### FR-1: Command Detection

**Priority**: P0 (Critical)

The system must detect when a user or Claude issues a command that has a better alternative.

| Input | Detection | Alternative |
|-------|-----------|-------------|
| `cat file.txt` | File read | `Read` tool |
| `head -n 50 file.txt` | File read with limit | `Read` tool with limit |
| `grep "pattern" .` | Content search | `Grep` tool |
| `find . -name "*.py"` | File search | `Glob` tool |
| `sed -i 's/old/new/g' file` | File edit | `Edit` tool |
| `echo "content" > file` | File write | `Write` tool |

**Acceptance Criteria**:
- [ ] Detects 95%+ of common file operation commands
- [ ] Detection latency < 100ms
- [ ] Zero false positives on excluded commands (git, docker, etc.)

### FR-2: Tool Comparison

**Priority**: P0 (Critical)

The system must provide clear comparison between detected command and recommended tool.

**Example Output**:
```
Detected: cat README.md
Recommended: Read tool

Comparison:
| Aspect | cat | Read tool |
|--------|-----|-----------|
| Large file handling | May truncate | Pagination |
| Binary detection | Raw output | Safe handling |
| Line numbers | Requires -n | Built-in |
| Token efficiency | Higher | Lower |

Recommendation: Use Read tool for structured output
```

**Acceptance Criteria**:
- [ ] Comparison shown for 100% of detected commands
- [ ] Includes at least 3 comparison points
- [ ] Links to relevant documentation

### FR-3: MCP Tool Availability

**Priority**: P1 (High)

The system must detect which MCP tools are available in the current session.

**Detection Methods**:
1. Query MCP server capabilities
2. Check tool manifest
3. Runtime probe with fallback

**Acceptance Criteria**:
- [ ] Detects MCP availability within 5 seconds
- [ ] Caches result for session duration
- [ ] Updates on MCP server reconnection

### FR-4: Warning System

**Priority**: P1 (High)

The system must display warnings based on configured enforcement level.

**Warning Levels**:

| Level | Behavior | User Action |
|-------|----------|-------------|
| Advisory | Info message | None required |
| Warning | Yellow warning | Can proceed |
| Confirmation | Prompt | Must confirm |
| Strict | Block | Must use alternative |

**Acceptance Criteria**:
- [ ] Warnings are non-blocking by default
- [ ] Warning format is consistent
- [ ] User can dismiss warnings
- [ ] Warnings include one-click alternative

### FR-5: Graceful Degradation

**Priority**: P0 (Critical)

The system must handle unavailable tools gracefully.

**Degradation Path**:
```
MCP Tool → Built-in Tool → Shell Command → Error with alternatives
```

**Acceptance Criteria**:
- [ ] Never fails silently
- [ ] Always provides working fallback
- [ ] Logs degradation events
- [ ] Maintains functionality even if MCP server is down

### FR-6: User Preferences

**Priority**: P2 (Medium)

Users must be able to configure enforcement behavior.

**Configuration Options**:
```yaml
enforcement_level: advisory
show_comparisons: true
preferred_tools:
  file_read: mcp
  file_search: builtin
excluded_patterns:
  - "git *"
  - "docker *"
  - "make *"
```

**Acceptance Criteria**:
- [ ] Config file in `.claude/` directory
- [ ] Environment variable overrides
- [ ] Session-level overrides
- [ ] Sensible defaults (zero-config works)

---

## Non-Functional Requirements

### NFR-1: Performance

| Metric | Target |
|--------|--------|
| Detection latency | < 100ms |
| Memory overhead | < 50MB |
| CPU impact | < 5% |
| Startup time | < 2s |

### NFR-2: Reliability

| Metric | Target |
|--------|--------|
| Uptime | 99.9% |
| Fallback success rate | > 95% |
| False positive rate | < 1% |
| Recovery time | < 5s |

### NFR-3: Usability

| Metric | Target |
|--------|--------|
| User satisfaction | > 85% |
| Time to understand | < 30s |
| Override actions | < 3 clicks |
| Learning curve | Minimal |

### NFR-4: Security

| Metric | Target |
|--------|--------|
| Data exposure | None |
| Permission escalation | Prevented |
| Audit logging | Complete |
| Input validation | All inputs |

### NFR-5: Integration

| Metric | Target |
|--------|--------|
| Claude Code compatibility | 100% |
| MCP server support | All standard servers |
| CI/CD integration | GitHub Actions, GitLab CI |
| IDE support | VS Code, terminal |

---

## User Stories

### US-1: File Reading Recommendation

**As a** developer using Claude Code
**I want** to be notified when I use `cat` instead of Read
**So that** I can benefit from structured file handling

**Acceptance Criteria**:
- [ ] Warning appears within 100ms
- [ ] Shows comparison of `cat` vs `Read`
- [ ] One-click to switch to Read
- [ ] Can dismiss and proceed with `cat`

### US-2: Search Tool Guidance

**As a** new Claude Code user
**I want** to learn about Glob and Grep tools
**So that** I can search files more effectively

**Acceptance Criteria**:
- [ ] When I type `find`, suggest Glob
- [ ] When I type `grep`, suggest Grep
- [ ] Include example of equivalent command
- [ ] Link to documentation

### US-3: Team Enforcement

**As a** team lead
**I want** to configure strict enforcement for my team
**So that** everyone uses optimal tools

**Acceptance Criteria**:
- [ ] Can set enforcement level in config file
- [ ] Config can be committed to repo
- [ ] Team members inherit settings
- [ ] Can override for specific commands

### US-4: Graceful Fallback

**As a** developer in a restricted environment
**I want** Claude to fall back to shell commands when MCP is unavailable
**So that** my work is not blocked

**Acceptance Criteria**:
- [ ] Detects MCP unavailability within 5s
- [ ] Automatically uses shell fallback
- [ ] Shows info message about degraded mode
- [ ] Resumes MCP when available

---

## Success Metrics

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| MCP tool usage for file ops | 20% | 80% | Analytics |
| Search command errors | 15% | 7.5% | Error logs |
| User satisfaction | N/A | 85%+ | Surveys |
| Workflow disruption | N/A | < 5% | Issue reports |
| Token efficiency | 100 | 70 | Token counter |

---

## Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| User frustration with warnings | High | Medium | Non-blocking default |
| Performance impact | Medium | Low | Async detection |
| False positives | High | Low | Conservative matching |
| MCP server instability | High | Low | Graceful degradation |

---

## Dependencies

| Dependency | Type | Owner |
|------------|------|-------|
| Claude Code CLI | Runtime | Anthropic |
| MCP Protocol | Standard | Anthropic |
| Built-in tools | Runtime | Anthropic |
| Configuration system | Runtime | Anthropic |

---

## Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| M1: Foundation | 1 week | Detection engine, basic warnings |
| M2: Integration | 1 week | MCP availability, tool comparison |
| M3: Degradation | 1 week | Fallback system, caching |
| M4: Configuration | 1 week | User preferences, team config |
| M5: Analytics | 1 week | Usage tracking, dashboards |
| M6: Testing | 1 week | E2E tests, performance |
| M7: Documentation | 1 week | Guides, API docs |
| M8: Launch | 1 week | Rollout, monitoring |

**Total**: 8 weeks

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-12-19 | Claude | Initial PRD |
