# SuperClaude Skills Architecture

## Overview

This repository contains a comprehensive set of Claude Skills designed to transform your Odoo development and project management workflows. The architecture integrates OCA (Odoo Community Association) repositories, PMBOK-aligned project management, diagramming standards, and Odoo Studio capabilities.

## Architecture Structure

```
insightpulse-odoo/
├─ .claude/skills/                    # Claude Skills Directory
│  ├─ ai-analytics-genie/             # AI-powered analytics
│  ├─ design-tokens/                  # Design system management
│  ├─ odoo-migration/                 # Odoo migration assistance
│  ├─ qweb-to-react/                  # QWeb template conversion
│  ├─ oca-module-scaffold/            # OCA-compliant module generation
│  ├─ oca-web-components/             # Web component migration
│  ├─ oca-module-discovery/           # Module discovery and compatibility
│  ├─ oca-compliance-check/           # OCA standards validation
│  └─ odoo-studio-integration/        # No-code/low-code customization
├─ vendor/                            # External dependencies
│  ├─ oca-web/                        # OCA web framework (git submodule)
│  ├─ oca-template/                   # OCA module template (git submodule)
│  └─ oca-apps-store/                 # OCA apps marketplace (git submodule)
└─ superclaude/                       # Shared knowledge base
   ├─ knowledge/
   │  ├─ STYLE_GUIDE.md               # Diagram and design standards
   │  ├─ PM_STANDARDS.md              # PMBOK 7 + ISO 21502 standards
   │  └─ EV_FORMULAS.md               # Earned Value Management formulas
   └─ agents/                         # Future agent implementations
```

## Skills Catalog

### Core Development Skills

#### 1. ai-analytics-genie
- **Purpose**: AI-powered business intelligence and analytics
- **Use Cases**: Data analysis, predictive modeling, dashboard creation
- **Integration**: Works with Odoo reporting and Apache Superset

#### 2. design-tokens
- **Purpose**: Design system management and consistency
- **Use Cases**: Brand consistency, UI standardization, theme management
- **Features**: Color palettes, typography, spacing, component libraries

#### 3. odoo-migration
- **Purpose**: Odoo version migration assistance
- **Use Cases**: Database migration, module compatibility, data transformation
- **Features**: Migration planning, compatibility analysis, automated scripts

#### 4. qweb-to-react
- **Purpose**: Convert QWeb templates to React components
- **Use Cases**: Modernizing Odoo interfaces, React integration
- **Features**: Template conversion, component generation, testing

### OCA Integration Skills

#### 5. oca-module-scaffold
- **Purpose**: Generate OCA-compliant modules
- **Use Cases**: New module development, standards compliance
- **Features**: Template generation, standards validation, best practices

#### 6. oca-web-components
- **Purpose**: Migrate OCA web components to modern frameworks
- **Use Cases**: JavaScript widget modernization, React/Vue conversion
- **Features**: Pattern extraction, migration planning, compatibility testing

#### 7. oca-module-discovery
- **Purpose**: Discover and recommend OCA modules
- **Use Cases**: Module selection, dependency management, installation planning
- **Features**: Compatibility analysis, dependency resolution, installation scripts

#### 8. oca-compliance-check
- **Purpose**: Validate modules against OCA standards
- **Use Cases**: Contribution preparation, quality assurance, standards compliance
- **Features**: Validation scoring, improvement suggestions, automated fixes

### Business Process Skills

#### 9. odoo-studio-integration
- **Purpose**: Leverage Odoo Studio for no-code customization
- **Use Cases**: Rapid prototyping, workflow automation, UI customization
- **Features**: Custom field management, view customization, automation design

## Installation & Setup

### Prerequisites

1. **Claude Code** with Skills support
2. **Git** for submodule management
3. **Odoo 19.0+** environment

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/jgtolentino/insightpulse-odoo.git
   cd insightpulse-odoo
   ```

2. **Initialize submodules**:
   ```bash
   git submodule update --init --recursive
   ```

3. **Install skills to Claude**:
   ```bash
   # Copy skills to Claude directory
   cp -r .claude/skills/* ~/.claude/skills/
   ```

4. **Configure knowledge base**:
   ```bash
   # Ensure knowledge base is accessible
   cp -r superclaude/knowledge/ ~/.claude/knowledge/
   ```

### Manual Installation (Alternative)

If using Claude Desktop or different setup:

1. **Copy skills manually** to your Claude skills directory
2. **Update file paths** in SKILL.md files if needed
3. **Configure vendor paths** for OCA integration

## Usage Examples

### OCA Module Development

```bash
# Generate a new OCA-compliant module
claude "Use oca-module-scaffold to create an expense approval module for Odoo 19"

# Validate existing module against OCA standards
claude "Use oca-compliance-check to validate my custom CRM module"

# Discover relevant OCA modules
claude "Use oca-module-discovery to find project management modules for Odoo 19"
```

### Project Management

```bash
# Create project charter and planning documents
claude "Use PMP skills to create project charter for website development"

# Generate EVM reports
claude "Calculate EVM metrics: PV=50k, EV=45k, AC=55k, BAC=100k"

# Create BPMN diagrams
claude "Use diagram-parity to create HR onboarding process with BPMN"
```

### Odoo Studio Customization

```bash
# Design custom workflows
claude "Use odoo-studio-integration to create multi-level approval workflow"

# Customize user interfaces
claude "Design custom CRM dashboard with Studio for sales team"

# Build mobile interfaces
claude "Create mobile-optimized expense submission form with Studio"
```

## Integration Patterns

### With Existing Odoo Modules

The skills integrate seamlessly with:
- **OCA modules** (accounting, HR, project management)
- **Custom modules** (extend functionality with Studio)
- **Third-party integrations** (API connections, external systems)

### Development Workflow

1. **Requirement Analysis** → Use appropriate skill for analysis
2. **Solution Design** → Generate specifications and plans
3. **Implementation** → Execute with step-by-step guidance
4. **Validation** → Test and verify against standards
5. **Documentation** → Generate user and technical documentation

## Knowledge Base Integration

### Shared Standards

The knowledge base provides consistent standards across all skills:

- **STYLE_GUIDE.md**: Visual design and diagramming standards
- **PM_STANDARDS.md**: Project management methodologies
- **EV_FORMULAS.md**: Performance measurement formulas

### Custom Extensions

Extend the knowledge base by adding:
- Organization-specific standards
- Industry-specific templates
- Custom integration patterns

## Best Practices

### Skill Selection

1. **Start with analysis skills** for requirements gathering
2. **Use OCA skills** for standards-compliant development
3. **Leverage Studio integration** for rapid customization
4. **Apply PMP skills** for project governance

### Performance Optimization

- **Cache frequently used patterns**
- **Batch similar operations**
- **Use appropriate skill combinations**
- **Monitor skill execution times**

### Maintenance

- **Regularly update OCA submodules**
- **Review and refresh knowledge base**
- **Test skill combinations**
- **Document custom extensions**

## Troubleshooting

### Common Issues

1. **Skill not found**: Ensure skills are copied to correct Claude directory
2. **File path errors**: Update requires paths in SKILL.md files
3. **Submodule issues**: Run `git submodule update --init --recursive`
4. **Performance issues**: Check skill dependencies and optimize patterns

### Debug Mode

Enable debug logging for skill execution:
```bash
# Set environment variable for detailed logging
export CLAUDE_SKILL_DEBUG=1
```

## Contributing

### Adding New Skills

1. **Follow SKILL.md template structure**
2. **Include comprehensive examples**
3. **Reference relevant knowledge base files**
4. **Test with real-world scenarios**
5. **Document integration patterns**

### Updating Knowledge Base

1. **Maintain backward compatibility**
2. **Update all referencing skills**
3. **Version control changes**
4. **Document modifications**

## Roadmap

### Phase 1: Foundation (Complete)
- ✅ Core skills architecture
- ✅ OCA integration
- ✅ Knowledge base setup
- ✅ Basic documentation

### Phase 2: Enhancement (In Progress)
- [ ] Advanced AI analytics integration
- [ ] Real-time collaboration features
- [ ] Automated testing frameworks
- [ ] Performance optimization

### Phase 3: Expansion (Planned)
- [ ] Additional industry-specific skills
- [ ] Mobile app development skills
- [ ] Advanced integration patterns
- [ ] Community skill marketplace

## Support

- **Documentation**: This README and individual SKILL.md files
- **Issues**: GitHub issues for bug reports and feature requests
- **Community**: OCA community forums and discussions
- **Updates**: Regular skill and knowledge base updates

## License

This skills architecture is designed to work with OCA repositories under their respective licenses. Please review individual OCA repository licenses for compliance.

---

**SuperClaude Skills Architecture** - Transforming Odoo development with AI-powered assistance and community standards.
