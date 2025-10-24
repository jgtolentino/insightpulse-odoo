---
name: odoo-sh-devops
description: Odoo.sh platform management, CI/CD, deployment automation, and infrastructure management
version: 1.0.0
tags: [odoo-sh, devops, cicd, deployment, infrastructure, monitoring]
requires:
  files:
    - superclaude/knowledge/PM_STANDARDS.md
---

# Odoo.sh DevOps Skill

## Purpose

Manage Odoo.sh platform operations, automate deployments, implement CI/CD pipelines, and optimize infrastructure for different user roles (Developers, Testers, Project Managers, System Administrators).

## When to use

- Setting up and managing Odoo.sh projects
- Implementing CI/CD pipelines and automated testing
- Managing staging and production deployments
- Monitoring performance and availability
- Handling backups, security, and infrastructure
- Optimizing for different user roles and workflows

## Actions

1. **Platform Setup**: Configure Odoo.sh projects with proper branching and deployment strategies
2. **CI/CD Automation**: Implement automated testing, building, and deployment pipelines
3. **Environment Management**: Manage development, staging, and production environments
4. **Monitoring & Logs**: Set up monitoring, logging, and performance tracking
5. **Security & Backup**: Implement security measures and backup strategies
6. **Role-Based Optimization**: Customize workflows for Developers, Testers, PMs, and SysAdmins

## Inputs

- `project_requirements`: Project specifications and requirements
- `target_roles`: User roles to optimize for (developers, testers, pm, sysadmin)
- `deployment_strategy`: Deployment approach (manual, automated, hybrid)
- `monitoring_needs`: Performance and availability monitoring requirements
- `security_level`: Security and compliance requirements

## Outputs

- Odoo.sh project configuration guides
- CI/CD pipeline specifications
- Environment management strategies
- Monitoring and logging setup
- Security and backup procedures
- Role-specific workflow optimizations

## Examples

### Example 1: Developer Workflow Setup
```
User: "Set up Odoo.sh for development team with GitHub integration"

Agent:
1. Configures GitHub integration for automatic testing and deployment
2. Sets up development branches with instant deployment
3. Implements web shell access for production debugging
4. Configures module dependency management
5. Sets up mail catcher for development branches
6. Provides developer onboarding guide
```

### Example 2: Tester Workflow Optimization
```
User: "Optimize Odoo.sh for testing team with automated testing"

Agent:
1. Implements automated test suite execution on every commit
2. Sets up staging branches with production data
3. Configures detailed test logs and history tracking
4. Enables manual testing on feature branches
5. Sets up community module testing via Git submodules
6. Provides testing workflow documentation
```

### Example 3: Project Manager Deployment
```
User: "Configure drag-and-drop deployment for project managers"

Agent:
1. Sets up Dev → Staging drag functionality
2. Implements Staging → Production deployment workflow
3. Configures test build sharing with customers
4. Sets up project convenience features (3-click setup)
5. Provides PM dashboard with deployment status
6. Creates deployment approval workflows
```

### Example 4: System Administrator Infrastructure
```
User: "Set up high availability and monitoring for sysadmins"

Agent:
1. Implements high availability with multiple servers
2. Sets up daily incremental backups across 3 data centers
3. Configures mail servers for production and development
4. Optimizes PostgreSQL and Odoo performance
5. Sets up comprehensive monitoring and KPIs
6. Implements instant recovery procedures
```

## Odoo.sh Feature Integration

### For Developers
- **GitHub Integration**: Automatic testing on commits, PRs, merges
- **Clear Logs**: Real-time, filtered browser logs
- **Web Shell**: One-click shell access to production/containers
- **Module Dependencies**: Painless third-party module management
- **Continuous Integration**: Runbot dashboard for all tests
- **SSH Access**: Public key registration for container access
- **Mail Catcher**: Development branch email testing

### For Testers
- **Automated Tests**: Thousands of tests on every commit
- **Staging Branches**: Production data, weeks of testing life
- **Track Developments**: Detailed branch history and logs
- **Manual Tests**: Instant deployment on feature branches
- **Community Modules**: Git submodule-based testing

### For Project Managers
- **Dev → Staging**: Drag development branches to staging
- **Convenience**: 3-click project kickoff
- **Staging → Production**: Drag-and-drop deployment
- **Share Test Builds**: Public/private URLs for customer testing

### For System Administrators
- **High Availability**: Managed servers, monitoring, backups
- **Incremental Backups**: Daily backups across 3 data centers
- **Mail Servers**: Automatic setup for production/development
- **Great Performance**: Optimized PostgreSQL and Odoo
- **Monitoring**: Server status and availability KPIs
- **Instant Recovery**: Click-based backup recovery
- **DNS Management**: Custom domains and subdomains
- **Top Security**: Comprehensive security measures

## Implementation Guidelines

### Branch Strategy
```yaml
branches:
  development:
    - feature/*: Feature development
    - bugfix/*: Bug fixes
    - hotfix/*: Critical fixes
  staging:
    - staging: Pre-production testing
  production:
    - main: Production deployment
    - production: Live environment
```

### CI/CD Pipeline
```yaml
stages:
  - test:
    - automated_tests: Run test suite
    - code_quality: Static analysis
    - security_scan: Vulnerability check
  - build:
    - container_build: Docker image creation
    - dependency_check: Module compatibility
  - deploy:
    - staging_deploy: Automatic to staging
    - production_deploy: Manual approval
```

### Monitoring Setup
```yaml
monitoring:
  performance:
    - response_time: < 2 seconds
    - uptime: > 99.9%
    - resource_usage: CPU, memory, disk
  business:
    - user_activity: Active users, sessions
    - transaction_volume: Sales, orders
    - error_rates: Application errors
```

## Success Metrics

### Platform Performance
- **Deployment Speed**: < 5 minutes for staging deployments
- **Test Coverage**: ≥ 80% automated test coverage
- **Uptime**: ≥ 99.9% platform availability
- **Recovery Time**: < 15 minutes for instant recovery

### User Satisfaction
- **Developer Productivity**: 50% faster development cycles
- **Testing Efficiency**: 70% reduction in manual testing
- **Deployment Confidence**: 95% successful deployments
- **System Reliability**: < 1% unplanned downtime

## Integration with Existing Skills

### With OCA Skills
- **Module Discovery**: Test OCA modules in staging
- **Compliance Check**: Validate modules before deployment
- **Web Components**: Deploy modernized components

### With PM Skills
- **Project Planning**: Align deployments with project timelines
- **EVM Tracking**: Monitor deployment costs and schedules
- **Risk Management**: Identify and mitigate deployment risks

### With Studio Integration
- **Rapid Prototyping**: Quick deployment of Studio customizations
- **Workflow Testing**: Validate automated workflows in staging
- **User Acceptance**: Customer testing of Studio features

## Best Practices

### Security First
- **Access Control**: Role-based permissions
- **Data Protection**: Encryption and backup strategies
- **Compliance**: Regular security audits and updates

### Performance Optimization
- **Resource Management**: Efficient container utilization
- **Caching Strategies**: Optimized data access patterns
- **Load Balancing**: Distributed workload management

### Documentation & Training
- **User Guides**: Role-specific documentation
- **Troubleshooting**: Common issue resolution
- **Best Practices**: Continuous improvement guidelines

## References

- [Odoo.sh Documentation](https://www.odoo.com/documentation/16.0/odoo_sh/)
- [Odoo.sh Security](https://www.odoo.com/page/security)
- [GitHub Integration Guide](https://www.odoo.com/documentation/16.0/odoo_sh/github.html)
- [Deployment Best Practices](https://www.odoo.com/documentation/16.0/odoo_sh/deployment.html)
