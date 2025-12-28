# MCP Tool Enforcer - Implementation Plan

> Technical architecture and implementation roadmap

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Claude Code Session                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Command    │───▶│    Tool      │───▶│   Warning    │      │
│  │  Detection   │    │  Comparison  │    │   System     │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │     MCP      │    │   Built-in   │    │   Fallback   │      │
│  │  Availability│    │    Tools     │    │   Handler    │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                   │               │
│         └───────────────────┴───────────────────┘               │
│                             │                                   │
│                             ▼                                   │
│                    ┌──────────────┐                             │
│                    │  Execution   │                             │
│                    │   Engine     │                             │
│                    └──────────────┘                             │
│                             │                                   │
│                             ▼                                   │
│                    ┌──────────────┐                             │
│                    │  Analytics   │                             │
│                    │   Logger     │                             │
│                    └──────────────┘                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Design

### 1. Command Detection Engine

**Purpose**: Identify shell commands that have MCP/built-in alternatives

**Implementation**:
```python
class CommandDetector:
    """Detects shell commands with tool alternatives."""

    PATTERNS = {
        'file_read': [
            r'^cat\s+',
            r'^head\s+',
            r'^tail\s+',
            r'^less\s+',
            r'^more\s+',
        ],
        'file_search': [
            r'^find\s+',
            r'^locate\s+',
            r'^ls\s+.*-R',
        ],
        'content_search': [
            r'^grep\s+',
            r'^rg\s+',
            r'^ag\s+',
            r'^ack\s+',
        ],
        'file_edit': [
            r'^sed\s+',
            r'^awk\s+',
            r'^perl\s+-[pi]',
        ],
        'file_write': [
            r'^echo\s+.*>',
            r'^printf\s+.*>',
            r'^cat\s+<<',
        ],
    }

    EXCLUSIONS = [
        r'^git\s+',
        r'^docker\s+',
        r'^npm\s+',
        r'^make\s+',
        r'^ssh\s+',
    ]

    def detect(self, command: str) -> Optional[Detection]:
        """Detect if command has a better alternative."""
        pass
```

**Performance**:
- Compile regex patterns once
- Short-circuit on exclusions
- Cache detection results

### 2. MCP Availability Checker

**Purpose**: Determine which MCP tools are available in the session

**Implementation**:
```python
class MCPChecker:
    """Checks MCP tool availability."""

    def __init__(self):
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes

    async def check_availability(self, tool_name: str) -> bool:
        """Check if MCP tool is available."""
        if tool_name in self._cache:
            if not self._is_expired(tool_name):
                return self._cache[tool_name]

        available = await self._probe_tool(tool_name)
        self._cache[tool_name] = available
        return available

    async def _probe_tool(self, tool_name: str) -> bool:
        """Probe MCP server for tool availability."""
        pass
```

### 3. Tool Comparison Engine

**Purpose**: Generate comparison between detected command and recommended tool

**Implementation**:
```python
class ToolComparator:
    """Compares shell commands with tool alternatives."""

    COMPARISONS = {
        'file_read': {
            'shell': {
                'large_files': 'May truncate output',
                'binary_files': 'Raw output, may corrupt terminal',
                'line_numbers': 'Requires -n flag',
                'tokens': 'Verbose output',
            },
            'tool': {
                'large_files': 'Pagination support',
                'binary_files': 'Safe detection and handling',
                'line_numbers': 'Built-in',
                'tokens': 'Optimized output',
            },
        },
        # ... more comparisons
    }

    def compare(self, detection: Detection) -> Comparison:
        """Generate comparison for detected command."""
        pass
```

### 4. Warning System

**Purpose**: Display warnings based on enforcement level

**Implementation**:
```python
class WarningSystem:
    """Displays warnings for detected commands."""

    def __init__(self, config: Config):
        self.level = config.enforcement_level

    def warn(self, detection: Detection, comparison: Comparison) -> Warning:
        """Generate warning based on enforcement level."""
        if self.level == 'advisory':
            return InfoWarning(detection, comparison)
        elif self.level == 'warning':
            return YellowWarning(detection, comparison)
        elif self.level == 'confirmation':
            return ConfirmWarning(detection, comparison)
        elif self.level == 'strict':
            return BlockWarning(detection, comparison)
```

### 5. Fallback Handler

**Purpose**: Handle graceful degradation when preferred tools unavailable

**Implementation**:
```python
class FallbackHandler:
    """Handles tool fallback when preferred option unavailable."""

    FALLBACK_CHAIN = {
        'file_read': ['mcp__filesystem__read', 'Read', 'cat'],
        'file_search': ['mcp__search__glob', 'Glob', 'find'],
        'content_search': ['mcp__search__grep', 'Grep', 'grep'],
        'file_edit': ['mcp__filesystem__patch', 'Edit', 'sed'],
        'file_write': ['mcp__filesystem__write', 'Write', 'echo'],
    }

    async def get_available_tool(self, operation: str) -> str:
        """Get first available tool in fallback chain."""
        for tool in self.FALLBACK_CHAIN[operation]:
            if await self._is_available(tool):
                return tool
        raise NoToolAvailable(operation)
```

### 6. Analytics Logger

**Purpose**: Track tool usage and decisions for metrics

**Implementation**:
```python
class AnalyticsLogger:
    """Logs tool selection decisions for analytics."""

    def log_decision(self, decision: Decision):
        """Log a tool selection decision."""
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'command': decision.original_command,
            'detected_as': decision.detection_type,
            'recommended_tool': decision.recommended_tool,
            'actual_tool': decision.actual_tool,
            'user_action': decision.user_action,
            'fallback_used': decision.fallback_used,
        }
        self._write(entry)
```

---

## Implementation Milestones

### M1: Foundation (Week 1)

**Deliverables**:
- Command detection engine
- Basic pattern matching
- Unit tests for detection

**Tasks**:
1. Implement `CommandDetector` class
2. Define regex patterns for all operations
3. Add exclusion list for git/docker/etc.
4. Write unit tests (90% coverage)
5. Performance benchmarks (< 100ms)

**Exit Criteria**:
- [ ] Detects all file operation commands
- [ ] Zero false positives on exclusions
- [ ] Detection latency < 100ms

### M2: Tool Integration (Week 2)

**Deliverables**:
- MCP availability checker
- Built-in tool registry
- Fallback chain

**Tasks**:
1. Implement `MCPChecker` class
2. Build tool capability registry
3. Define fallback chains
4. Add caching layer
5. Integration tests

**Exit Criteria**:
- [ ] Detects MCP availability in < 5s
- [ ] Fallback works when MCP unavailable
- [ ] Cache invalidation works

### M3: Comparison Engine (Week 3)

**Deliverables**:
- Tool comparison logic
- Comparison output formatting
- Documentation links

**Tasks**:
1. Implement `ToolComparator` class
2. Define comparison criteria
3. Build output formatter
4. Add documentation links
5. User testing

**Exit Criteria**:
- [ ] Comparisons for all operations
- [ ] Clear, actionable output
- [ ] Links to docs work

### M4: Warning System (Week 4)

**Deliverables**:
- Warning display
- Enforcement levels
- User override handling

**Tasks**:
1. Implement `WarningSystem` class
2. Build warning formatters
3. Add enforcement levels
4. Handle user overrides
5. UX testing

**Exit Criteria**:
- [ ] Warnings non-blocking by default
- [ ] All enforcement levels work
- [ ] Override takes < 3 clicks

### M5: Configuration (Week 5)

**Deliverables**:
- Configuration file support
- Environment variable overrides
- Default configuration

**Tasks**:
1. Define config schema
2. Implement config loader
3. Add env var support
4. Create defaults
5. Documentation

**Exit Criteria**:
- [ ] Zero-config works
- [ ] Config file overrides defaults
- [ ] Env vars override config

### M6: Analytics (Week 6)

**Deliverables**:
- Usage logging
- Decision tracking
- Basic dashboard

**Tasks**:
1. Implement `AnalyticsLogger`
2. Define metrics schema
3. Build log aggregation
4. Create dashboard views
5. Privacy review

**Exit Criteria**:
- [ ] All decisions logged
- [ ] Metrics accurate
- [ ] No PII in logs

### M7: Testing & Documentation (Week 7)

**Deliverables**:
- E2E test suite
- Performance tests
- User documentation

**Tasks**:
1. Write E2E tests
2. Performance benchmarks
3. User guide
4. API documentation
5. Troubleshooting guide

**Exit Criteria**:
- [ ] 90% test coverage
- [ ] Performance targets met
- [ ] Docs reviewed and published

### M8: Launch (Week 8)

**Deliverables**:
- Production deployment
- Monitoring setup
- Launch announcement

**Tasks**:
1. Deploy to production
2. Set up monitoring
3. Create rollback plan
4. Launch communications
5. Post-launch support

**Exit Criteria**:
- [ ] Deployed successfully
- [ ] Monitoring active
- [ ] No P0 bugs

---

## Technical Specifications

### Configuration Schema

```yaml
# .claude/mcp-enforcer.yml
version: "1.0"

enforcement:
  level: advisory  # advisory | warning | confirmation | strict
  log_decisions: true
  show_comparisons: true

tools:
  file_read:
    preferred: mcp  # mcp | builtin | shell
    fallback: [builtin, shell]
  file_search:
    preferred: builtin
    fallback: [shell]
  content_search:
    preferred: builtin
    fallback: [shell]

exclusions:
  commands:
    - "git *"
    - "docker *"
    - "make *"
  paths:
    - ".git/**"
    - "node_modules/**"

analytics:
  enabled: true
  retention_days: 30
```

### Metrics Schema

```json
{
  "decision": {
    "id": "uuid",
    "timestamp": "ISO8601",
    "session_id": "uuid",
    "command": {
      "raw": "cat file.txt",
      "detected_as": "file_read",
      "tokens": 5
    },
    "recommendation": {
      "tool": "Read",
      "reason": "Structured output",
      "comparison_shown": true
    },
    "outcome": {
      "tool_used": "Read",
      "user_action": "accepted",
      "fallback_triggered": false
    },
    "performance": {
      "detection_ms": 45,
      "execution_ms": 120
    }
  }
}
```

---

## Risk Mitigation

| Risk | Mitigation | Owner |
|------|------------|-------|
| Performance regression | Benchmark on each PR | Dev |
| User frustration | Non-blocking default | Product |
| MCP instability | Graceful fallback | Dev |
| Configuration complexity | Zero-config default | Product |

---

## Dependencies

### Internal

- Claude Code CLI
- Built-in tool registry
- MCP client library

### External

- MCP protocol specification
- Shell command documentation
- Analytics infrastructure

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-19 | Initial plan |
