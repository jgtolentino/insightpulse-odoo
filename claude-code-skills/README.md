# Claude Code Skills Catalog

**Last Updated**: November 1, 2025
**Total Skills**: 61+ specialized skills for Claude Code (including Audit Skill)
**Source**: Integrated from Claude Desktop skill packs + Anthropic official repository

---

## 🎯 Quick Start

### How to Use Skills with Claude Code

Since Claude Code cannot use uploaded skills like Claude Desktop, all skills are extracted as documentation that can be accessed via the Read tool.

**Usage Pattern**:
1. **Identify Task**: Determine which skill category applies
2. **Read Skill Doc**: Use Read tool on the relevant `SKILL.md` file
3. **Review Examples**: Check `examples/` directory for practical guides
4. **Apply Patterns**: Follow `reference/` documentation
5. **Validate**: Use `evaluations/` for testing scenarios

---

## 📂 Skill Categories

### 🔍 Audit & Security (Priority P0) **NEW**
**Location**: `audit-skill/`

**Primary Skill**: `audit-skill/SKILL.md` (12.6KB)
- Comprehensive security audit capabilities
- Code quality and OCA compliance validation
- Module structure auditing
- Performance analysis
- Dependency vulnerability scanning
- Configuration security checks

**Key Files**:
- `audit-skill/SKILL.md` - Main audit skill documentation
- `audit-skill/reference/security-audit-guide.md` - Security audit procedures (19.7KB)
- `audit-skill/reference/module-audit-guide.md` - Module structure validation (22.9KB)
- `audit-skill/examples/security-audit-example.md` - Security audit walkthrough (13.2KB)
- `audit-skill/examples/module-audit-example.md` - Module audit walkthrough (17.2KB)
- `audit-skill/evaluations/test-scenarios.md` - Test scenarios for validation (12.9KB)

**Use Cases**:
- ✅ Detect hardcoded credentials and secrets
- ✅ Identify SQL injection and XSS vulnerabilities
- ✅ Validate OCA module structure compliance
- ✅ Check security rules and access controls
- ✅ Audit performance issues (missing indexes, N+1 queries)
- ✅ Scan dependencies for vulnerabilities
- ✅ Generate comprehensive audit reports

**Integration**:
- Works with existing `scripts/audit-modules.sh`
- Compatible with `SECURITY_AUDIT_REPORT.md` format
- Integrates with CI/CD security gates
- Supports multiple audit types: security, code-quality, module-structure, performance

---

### 🔧 Odoo Development (Priority P0)
**Location**: `odoo/`

**Primary Skill**: `odoo/SKILL.md` (13KB)
- Module scaffolding with OCA compliance
- Production deployment patterns
- Docker configuration for Odoo 19
- Enterprise feature alternatives
- Security hardening checklists

**Key Files**:
- `odoo/SKILL.md` - Main DevOps skill documentation
- `odoo/reference/oca-module-structure.md` - OCA compliance guide (8KB)
- `odoo/reference/enterprise-alternatives.md` - Open-source alternatives (7KB)
- `odoo/reference/docker-production.md` - Production Docker patterns
- `odoo/reference/supabase-integration.md` - Database integration
- `odoo/reference/oca-vendoring.md` - OCA module management
- `odoo/examples/scaffold-module.md` - Module creation example
- `odoo/examples/production-deployment.md` - Deployment workflow
- `odoo/evaluations/` - Test scenarios

**Use Cases**:
- ✅ Create OCA-compliant custom modules
- ✅ Deploy Odoo to production (DigitalOcean, AWS, etc.)
- ✅ Vendor OCA community modules
- ✅ Replace Enterprise features with open-source alternatives
- ✅ Security hardening and access controls

**Current Production**: insightpulseai.net (Odoo 19)

---

### 📝 Notion Integration (Priority P0)
**Location**: `notion/`

#### 1. Knowledge Capture
**Path**: `notion/notion-knowledge-capture/SKILL.md`

**Capabilities**:
- Convert conversations to documentation
- Create decision logs from discussions
- Generate FAQs from support conversations
- Build team wiki pages automatically

**Use Cases**:
- ✅ Meeting notes → Notion action items
- ✅ Slack conversations → FAQ database
- ✅ Technical discussions → decision records
- ✅ Research findings → wiki documentation

#### 2. Meeting Intelligence
**Path**: `notion/notion-meeting-intelligence/SKILL.md`

**Capabilities**:
- Extract action items from meeting transcripts
- Generate meeting summaries with decisions
- Create follow-up task databases
- Link related discussions automatically

#### 3. Research Documentation
**Path**: `notion/notion-research-documentation/SKILL.md`

**Capabilities**:
- Structure research findings into organized pages
- Create bibliographies and citations
- Link related research topics
- Generate research status dashboards

#### 4. Spec to Implementation
**Path**: `notion/notion-spec-to-implementation/SKILL.md`

**Capabilities**:
- Convert PRDs to implementation tasks
- Break specifications into development stories
- Track specification compliance
- Link code to requirements

---

### 🎨 Diagram & Visualization (Priority P1)
**Location**: `diagrams/` (Currently empty - skills available in Downloads)

**Available Skills**:
- `drawio-diagrams-enhanced.zip` - Automated diagram generation
- `drawio-pmbok-skills.zip` - Project management workflow diagrams
- `enhanced-drawio-pmbok-skills.zip` - Advanced PMBOK visualizations

**Use Cases**:
- ✅ Generate architecture diagrams from descriptions
- ✅ Create PMBOK workflow visualizations
- ✅ Automate ER diagrams from database schemas
- ✅ Build system interaction diagrams

---

### 📊 Project Management (Priority P1)
**Location**: `project-management/` (Currently empty - skill available in Downloads)

**Available Skill**: `pmbok-project-management.zip`

**Capabilities**:
- PMBOK-compliant project tracking
- Risk management workflows
- Stakeholder communication templates
- Project status reporting automation

---

### 🌐 Anthropic Official Skills (Priority P2)
**Location**: `anthropic-official/`

**Total**: 12 official skills + templates

#### Featured Skills

**1. Algorithmic Art** (`algorithmic-art/`)
- Generative art creation
- JavaScript-based procedural generation
- HTML5 Canvas integration

**2. Artifacts Builder** (`artifacts-builder/`)
- shadcn component bundling
- React artifact creation
- Frontend component packaging

**3. Brand Guidelines** (`brand-guidelines/`)
- Brand consistency enforcement
- Design system documentation
- Style guide generation

**4. Canvas Design** (`canvas-design/`)
- Visual design automation
- Typography and layout tools
- Custom font integration

**5. Document Skills** (`document-skills/`)
- Technical documentation patterns
- User guide templates
- API documentation generation

**6. Internal Communications** (`internal-comms/`)
- Corporate communication templates
- Announcement formatting
- Employee update generation

**7. MCP Builder** (`mcp-builder/`)
- Model Context Protocol server creation
- MCP tool development
- Server configuration templates

**8. Skill Creator** (`skill-creator/`)
- Meta-skill for creating new skills
- Skill structure templates
- Evaluation framework generation

**9. Slack GIF Creator** (`slack-gif-creator/`)
- Animated GIF generation for Slack
- Meme creation automation
- Team communication visuals

**10. Template Skill** (`template-skill/`)
- Base template for new skills
- Skill structure reference
- Best practices documentation

**11. Theme Factory** (`theme-factory/`)
- Design theme generation
- Color palette creation
- Component theming automation

**12. Webapp Testing** (`webapp-testing/`)
- End-to-end testing patterns
- Test automation frameworks
- Quality assurance workflows

---

## 🚀 Integration with SuperClaude Framework

### Agent-Skill Mapping

**odoo-erp-architect** + `odoo/SKILL.md`
- Enhanced module development
- OCA compliance automation
- Enterprise feature implementation

**odoo-devops-architect** + `odoo/reference/docker-production.md`
- Production deployment workflows
- Infrastructure as code
- Security hardening

**odoo-security-engineer** + `audit-skill/SKILL.md` + `odoo/SKILL.md`
- Comprehensive security audits
- Vulnerability detection and remediation
- Access control implementation
- RLS policy creation
- Security audit workflows

**project-coordinator** + `notion/knowledge-capture/` + `pmbok/`
- Automated documentation
- Meeting intelligence
- Project tracking

**bi-designer** + `diagrams/` (when extracted)
- Architecture visualization
- Dashboard diagram generation
- Data flow diagrams

---

## 📖 Common Workflows

### 1. Perform Security Audit
```
1. Read: docs/claude-code-skills/audit-skill/SKILL.md
2. Read: docs/claude-code-skills/audit-skill/reference/security-audit-guide.md
3. Follow security-audit-example.md walkthrough
4. Run automated scans (grep, bandit, safety)
5. Generate comprehensive audit report
6. Track remediation in GitHub issues
```

### 2. Create OCA-Compliant Odoo Module
```
1. Read: docs/claude-code-skills/odoo/SKILL.md
2. Read: docs/claude-code-skills/odoo/reference/oca-module-structure.md
3. Follow scaffold-module.md example
4. Use Bash tool to create directories
5. Use Write tool to create files
6. Validate against OCA standards
```

### 3. Document Meeting in Notion
```
1. Read: docs/claude-code-skills/notion/notion-meeting-intelligence/SKILL.md
2. Extract meeting transcript
3. Follow pattern to generate action items
4. Create Notion page structure
5. Format with decision records
```

### 4. Audit Module Structure
```
1. Read: docs/claude-code-skills/audit-skill/SKILL.md
2. Read: docs/claude-code-skills/audit-skill/reference/module-audit-guide.md
3. Follow module-audit-example.md walkthrough
4. Validate manifest, security, models, views
5. Generate compliance report
6. Fix issues before OCA submission
```

### 5. Generate Architecture Diagram
```
1. Read: docs/claude-code-skills/diagrams/drawio-enhanced/SKILL.md (when extracted)
2. Analyze system components
3. Apply diagram patterns
4. Generate draw.io XML
5. Export to PNG/SVG
```

### 6. Deploy to Production
```
1. Read: docs/claude-code-skills/odoo/reference/docker-production.md
2. Read: docs/claude-code-skills/odoo/examples/production-deployment.md
3. Configure environment variables
4. Deploy using deployment scripts
5. Validate with health checks
```

---

## 📊 Skill Statistics

| Category | Skills | Size | Priority | Status |
|----------|--------|------|----------|--------|
| Odoo Development | 1 + 6 refs | 32KB | P0 | ✅ Ready |
| Notion Integration | 4 skills | 120KB | P0 | ✅ Ready |
| Diagrams | 3 skills | 72KB | P1 | ⏳ Pending |
| Project Management | 1 skill | 10KB | P1 | ⏳ Pending |
| Anthropic Official | 12 skills | 3.4MB | P2 | ✅ Ready |
| **Total** | **21 skills** | **~3.6MB** | - | **85% Ready** |

---

## 🎯 Production Deployment Context

### Current Production: insightpulseai.net

**Stack**:
- Odoo 19 (official Docker image)
- PostgreSQL 15
- 9 custom modules deployed
- DigitalOcean Droplet (188.166.237.231)

**Repository Health** (from comprehensive review):
- Overall Score: 44/100 (F) - NOT PRODUCTION READY
- Security: 38/100 (D-) - 18 Critical + 24 High vulnerabilities
- Test Coverage: 12% (87.5% modules with 0% coverage)
- Production Risk: 8.7/10 (CRITICAL)

**Emergency Remediation Required**:
- Fix plaintext credentials (CVSS 8.1)
- Add access controls (18% → 100%)
- Implement security tests (0% → 80%)
- Add database indexes (15+ missing)
- Complete incomplete modules (6 of 8 at 15-65%)

**Skills Available for Remediation**:
- `audit-skill/SKILL.md` - **NEW** Comprehensive audit capabilities
- `audit-skill/reference/security-audit-guide.md` - Security vulnerability detection
- `audit-skill/reference/module-audit-guide.md` - Module structure validation
- `odoo/SKILL.md` - Module scaffolding and OCA compliance
- `odoo/reference/oca-module-structure.md` - Access control patterns
- `odoo/reference/docker-production.md` - Production hardening
- `notion/knowledge-capture/` - Documentation automation

---

## 🔍 Finding Skills

### By Use Case

**"I need to audit security vulnerabilities"** **NEW**
→ Read `audit-skill/SKILL.md` and `audit-skill/reference/security-audit-guide.md`

**"I need to validate module structure"** **NEW**
→ Read `audit-skill/SKILL.md` and `audit-skill/reference/module-audit-guide.md`

**"I need to create an Odoo module"**
→ Read `odoo/SKILL.md` and `odoo/reference/oca-module-structure.md`

**"I need to document a meeting"**
→ Read `notion/notion-meeting-intelligence/SKILL.md`

**"I need to deploy to production"**
→ Read `odoo/reference/docker-production.md` and `odoo/examples/production-deployment.md`

**"I need to create a diagram"**
→ Extract and read `diagrams/drawio-enhanced/SKILL.md`

**"I need to manage a project"**
→ Extract and read `project-management/pmbok/SKILL.md`

**"I need to create a custom skill"**
→ Read `anthropic-official/skill-creator/SKILL.md`

### By Agent

**odoo-erp-architect**
→ `odoo/SKILL.md`, `odoo/reference/oca-module-structure.md`

**odoo-devops-architect**
→ `odoo/reference/docker-production.md`, deployment examples

**odoo-security-engineer**
→ `audit-skill/SKILL.md`, `audit-skill/reference/security-audit-guide.md`, access control references

**project-coordinator**
→ `notion/knowledge-capture/`, `project-management/pmbok/`

**testing-engineer**
→ `anthropic-official/webapp-testing/SKILL.md`

---

## 🛠️ Maintenance

### Updating Skills

**From Claude Desktop**:
1. Export updated skill as ZIP
2. Extract to appropriate subdirectory
3. Update this catalog if needed
4. Commit changes

**From Anthropic Official**:
1. Download updated skills-main.zip
2. Extract to `anthropic-official/`
3. Review CHANGELOG
4. Update catalog

### Adding New Skills

1. Create subdirectory in appropriate category
2. Extract skill files
3. Add entry to this catalog
4. Update agent references if relevant
5. Add use case examples

---

## 📝 Notes

**Repository Size**: Skills add ~3.6MB to repository (acceptable for modern repos)

**Git LFS**: Not required unless individual files exceed 100MB

**Extraction Status**:
- ✅ Audit skill (newly created - 98.4KB) **NEW**
- ✅ Odoo skills (odoo19-oca-devops.zip)
- ✅ Notion skills (4 files)
- ✅ Anthropic official (skills-main.zip)
- ⏳ Diagram skills (available in Downloads, not yet extracted)
- ⏳ PMBOK skills (available in Downloads, not yet extracted)
- ⏳ Unidentified files (3 files in Downloads, not yet investigated)

**Next Steps**:
1. Extract remaining diagram skills
2. Extract PMBOK project management skills
3. Investigate unidentified files (8).zip, (9).zip, (10).zip
4. Update SuperClaude agent files with skill references
5. Create example workflows for common tasks

---

## 🚀 Quick Links

### Core Skills
- **[Audit Skill](./audit-skill/SKILL.md)** - **NEW** Comprehensive security and quality audits
- [Odoo Development Skill](./odoo/SKILL.md)
- [OCA Module Structure](./odoo/reference/oca-module-structure.md)
- [Production Deployment](./odoo/reference/docker-production.md)

### Reference Guides
- **[Security Audit Guide](./audit-skill/reference/security-audit-guide.md)** - **NEW**
- **[Module Audit Guide](./audit-skill/reference/module-audit-guide.md)** - **NEW**

### Examples
- **[Security Audit Example](./audit-skill/examples/security-audit-example.md)** - **NEW**
- **[Module Audit Example](./audit-skill/examples/module-audit-example.md)** - **NEW**

### Other Skills
- [Notion Knowledge Capture](./notion/notion-knowledge-capture/SKILL.md)
- [Skill Creator (Meta-Skill)](./anthropic-official/skill-creator/SKILL.md)
- [MCP Builder](./anthropic-official/mcp-builder/SKILL.md)

---

**Ready to use**: Start with `audit-skill/SKILL.md` for comprehensive audits or `odoo/SKILL.md` for Odoo development tasks!
