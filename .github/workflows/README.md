# CI/CD Workflows Documentation

## 📋 Table of Contents

- [Overview](#overview)
- [Workflow Catalog](#workflow-catalog)
- [Architecture](#architecture)
- [Quick Start Guide](#quick-start-guide)
- [Configuration](#configuration)
- [Reusable Templates](#reusable-templates)
- [Dependencies](#dependencies)
- [Secrets & Variables](#secrets--variables)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

This directory contains GitHub Actions workflows for the InsightPulse Odoo project. The workflows are designed to be **modular, reusable, and production-ready** for teams working in DevOps spaces.

### Design Principles

1. **Security First** - Multiple scanning layers (code, dependencies, containers, secrets)
2. **Zero Downtime** - Blue-green deployment strategy with automated rollback
3. **Comprehensive Testing** - Unit, integration, E2E, and performance tests
4. **Observable** - Monitoring, alerting, and incident tracking
5. **Reusable** - Can be adapted for other Odoo or Python projects

## Workflow Catalog

### 🚀 Core Production Workflows

| Workflow | Purpose | Trigger | Key Features |
|----------|---------|---------|--------------|
| **comprehensive-cicd.yml** | Complete CI/CD pipeline | Push to main/develop, PR | 6-stage pipeline with security scanning, testing, deployment |
| **rollback.yml** | Emergency rollback | Manual dispatch | 3 rollback strategies, database backup, incident tracking |
| **production-deploy.yml** | Production deployment | Manual dispatch | Blue-green deployment, health checks |
| **digitalocean-deploy.yml** | DigitalOcean deployment | Push to main | DO-specific deployment automation |

### 🔍 Quality & Testing Workflows

| Workflow | Purpose | Trigger | Key Features |
|----------|---------|---------|--------------|
| **quality-gate.yml** | PR quality checks | PR creation/update | Blocks merge on failures, comprehensive checks |
| **quality.yml** | Code quality scanning | Push | Linting, formatting, security checks |
| **odoo-ci.yml** | Odoo-specific CI | PR | Module validation, upgrade tests |
| **odoo-module-test.yml** | Module testing | Manual/PR | Individual module testing |

### 🤖 Automation Workflows

| Workflow | Purpose | Trigger | Key Features |
|----------|---------|---------|--------------|
| **oca-bot-automation.yml** | OCA community automation | Schedule/manual | Module fetching, PR creation |
| **oca-fetch-test.yml** | OCA module testing | Manual | Fetch and test OCA modules |
| **auto-patch.yml** | Automated patching | Issue comments | Auto-fix common issues |
| **parity-live-sync.yml** | Environment sync | Schedule | Keep staging/production in parity |

### 🛠️ Utility Workflows

| Workflow | Purpose | Trigger | Key Features |
|----------|---------|---------|--------------|
| **ai-code-review.yml** | AI-powered code review | PR | Claude-based code analysis |
| **agent-eval.yml** | Agent evaluation | Manual | Test AI agents |
| **docker-image.yml** | Docker build/push | Push | Multi-platform builds |
| **dockerhub-publish.yml** | DockerHub publishing | Release | Public image publishing |

### 📊 Monitoring & Observability

| Workflow | Purpose | Trigger | Key Features |
|----------|---------|---------|--------------|
| **insightpulse-monitor-deploy.yml** | Monitoring stack deployment | Push | Grafana, Prometheus, alerts |
| **post-deploy-refresh.yml** | Post-deployment tasks | Deployment completion | Cache refresh, warmup |

### 🎯 Issue & PR Management

| Workflow | Purpose | Trigger | Key Features |
|----------|---------|---------|--------------|
| **issue-validation.yml** | Issue validation | Issue creation | Template compliance |
| **issue-from-comment.yml** | Create issue from comment | PR comment | `/create-issue` command |
| **auto-close-resolved.yml** | Auto-close resolved issues | Schedule | Cleanup resolved issues |
| **triage.yml** | Issue triage | Issue creation | Auto-label and assign |

## Architecture

### Comprehensive CI/CD Pipeline (comprehensive-cicd.yml)

```
┌─────────────────────────────────────────────────────────────────┐
│                     STAGE 1: CODE QUALITY & SECURITY            │
├─────────────────────────────────────────────────────────────────┤
│ • Python Linting (Ruff, Pylint, Black)                         │
│ • Security Scanning (Bandit, Safety, TruffleHog)               │
│ • XML/YAML Validation                                           │
│ • Dependency Audit                                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       STAGE 2: TESTING                          │
├─────────────────────────────────────────────────────────────────┤
│ • Unit Tests (pytest with coverage)                            │
│ • Integration Tests (Docker Compose)                           │
│ • Odoo Module Validation                                       │
│ • Database Migration Tests                                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    STAGE 3: BUILD & PACKAGE                     │
├─────────────────────────────────────────────────────────────────┤
│ • Docker Multi-platform Build (AMD64, ARM64)                   │
│ • Container Security Scan (Trivy)                              │
│ • Image Signing (Cosign)                                       │
│ • Registry Push (GHCR)                                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      STAGE 4: DEPLOYMENT                        │
├─────────────────────────────────────────────────────────────────┤
│ • Staging Deployment (Auto)                                    │
│ • Production Blue-Green Deployment (Manual Approval)           │
│ • Database Backup (Pre-deployment)                             │
│ • Blue Version Retention (Rollback capability)                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                 STAGE 5: POST-DEPLOYMENT VALIDATION             │
├─────────────────────────────────────────────────────────────────┤
│ • Smoke Tests (Health endpoints)                               │
│ • E2E Tests (Playwright)                                       │
│ • Performance Tests (k6)                                       │
│ • Database Integrity Checks                                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  STAGE 6: MONITORING & ALERTS                   │
├─────────────────────────────────────────────────────────────────┤
│ • Deployment Annotations (Grafana)                             │
│ • Slack Notifications                                          │
│ • Email Incident Reports                                       │
│ • Performance Baselines                                        │
└─────────────────────────────────────────────────────────────────┘
```

### Emergency Rollback Flow (rollback.yml)

```
┌─────────────────────────────────────────────────────────────────┐
│                    1. VALIDATE ROLLBACK                         │
├─────────────────────────────────────────────────────────────────┤
│ • Get current deployment                                       │
│ • Determine rollback target (3 strategies)                     │
│   - Blue-Green Swap                                            │
│   - Previous Image                                             │
│   - Specific Version                                           │
│ • Verify target image exists                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    2. CREATE SNAPSHOT                           │
├─────────────────────────────────────────────────────────────────┤
│ • Backup PostgreSQL database                                   │
│ • Snapshot Kubernetes state                                    │
│ • Upload to S3/GCS                                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    3. EXECUTE ROLLBACK                          │
├─────────────────────────────────────────────────────────────────┤
│ • Enable maintenance mode                                      │
│ • Execute rollback strategy                                    │
│ • Health checks                                                │
│ • Disable maintenance mode                                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    4. VALIDATE & NOTIFY                         │
├─────────────────────────────────────────────────────────────────┤
│ • Smoke tests                                                  │
│ • Performance comparison                                       │
│ • Slack notification                                           │
│ • Email incident report                                        │
│ • Create GitHub incident ticket                                │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start Guide

### For New Projects

1. **Copy Workflows**
   ```bash
   # Copy entire workflows directory
   cp -r .github/workflows /path/to/your/project/.github/

   # Or copy specific workflows
   cp .github/workflows/comprehensive-cicd.yml /path/to/your/project/.github/workflows/
   cp .github/workflows/rollback.yml /path/to/your/project/.github/workflows/
   ```

2. **Configure Secrets** (See [Secrets & Variables](#secrets--variables))

3. **Customize for Your Project**
   - Update environment variables in workflows
   - Adjust test commands for your project structure
   - Configure deployment targets

4. **Test Workflows**
   ```bash
   # Create a feature branch
   git checkout -b test/workflow-integration

   # Push to trigger CI
   git push origin test/workflow-integration

   # Create PR to trigger quality gates
   gh pr create --title "Test: Workflow Integration"
   ```

### For Odoo Projects

The workflows are **pre-configured for Odoo 19.0 CE** but can be adapted:

1. **Change Odoo Version**
   ```yaml
   # In comprehensive-cicd.yml
   env:
     ODOO_VERSION: "18.0"  # Change from 19.0
   ```

2. **Adjust Module Paths**
   ```yaml
   # If your custom modules are in different directory
   env:
     CUSTOM_ADDONS_PATH: "addons/custom"  # Default
     # Change to: "src/custom_modules"
   ```

3. **Database Configuration**
   ```yaml
   # Adjust PostgreSQL version if needed
   services:
     postgres:
       image: postgres:16-alpine  # Change version
   ```

## Configuration

### Environment-Specific Settings

The workflows support multiple environments:

| Environment | Purpose | Auto-Deploy | Approval Required |
|-------------|---------|-------------|-------------------|
| **development** | Local/dev testing | No | No |
| **staging** | Pre-production | Yes (on develop branch) | No |
| **production** | Live system | Yes (on main branch) | Yes (manual approval) |

### Workflow Inputs

#### comprehensive-cicd.yml

```yaml
# Triggered automatically on:
# - push to main/develop
# - pull_request to main/develop

# Manual trigger with options:
workflow_dispatch:
  inputs:
    environment:
      description: 'Target environment'
      type: choice
      options: [development, staging, production]
    skip_tests:
      description: 'Skip tests (not recommended)'
      type: boolean
      default: false
```

#### rollback.yml

```yaml
workflow_dispatch:
  inputs:
    environment:
      description: 'Environment to rollback'
      required: true
      type: choice
      options: [staging, production]

    rollback_type:
      description: 'Rollback strategy'
      required: true
      type: choice
      options:
        - blue_green_swap    # Swap to blue deployment
        - previous_image     # Rollback to previous version
        - specific_version   # Rollback to specific version

    version:
      description: 'Specific version (for specific_version option)'
      required: false
      type: string

    reason:
      description: 'Reason for rollback'
      required: true
      type: string
```

## Reusable Templates

### Creating a Reusable Workflow

```yaml
# .github/workflows/reusable-test.yml
name: Reusable Test Workflow

on:
  workflow_call:
    inputs:
      python-version:
        required: false
        type: string
        default: '3.11'
    secrets:
      DATABASE_URL:
        required: true

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ inputs.python-version }}
      - run: pytest tests/
```

### Calling a Reusable Workflow

```yaml
# .github/workflows/my-workflow.yml
name: My Workflow

on: push

jobs:
  test:
    uses: ./.github/workflows/reusable-test.yml
    with:
      python-version: '3.11'
    secrets:
      DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

## Dependencies

### Required GitHub Actions

```yaml
# Core actions used across workflows
actions/checkout@v4                    # Code checkout
actions/setup-python@v5                # Python setup
docker/setup-buildx-action@v3          # Docker Buildx
docker/build-push-action@v5            # Docker build/push
azure/k8s-set-context@v3              # Kubernetes config
slackapi/slack-github-action@v1       # Slack notifications

# Security scanning
trufflesecurity/trufflehog@main       # Secret scanning
aquasecurity/trivy-action@master      # Container scanning
pyupio/safety-action@v1               # Python dependency audit

# Testing & Quality
codecov/codecov-action@v4             # Code coverage
github/codeql-action@v3               # CodeQL analysis
```

### Required Tools

```bash
# Python tools (install via requirements-dev.txt)
black==24.3.0           # Code formatting
ruff==0.3.0            # Fast linting
pylint==3.1.0          # Comprehensive linting
pytest==8.1.0          # Testing framework
pytest-cov==5.0.0      # Coverage plugin
bandit==1.7.8          # Security linting
safety==3.1.0          # Dependency vulnerability scanner

# Container tools
trivy                  # Container vulnerability scanner
cosign                 # Container signing
hadolint              # Dockerfile linter

# Kubernetes tools
kubectl               # Kubernetes CLI
helm                  # Kubernetes package manager

# Performance testing
k6                    # Load testing
playwright            # E2E testing
```

## Secrets & Variables

### Required Secrets

Create these secrets in your GitHub repository (Settings → Secrets and variables → Actions):

#### Docker & Registry

```bash
DOCKER_USERNAME                    # Docker Hub username
DOCKER_PASSWORD                    # Docker Hub password (or token)
GHCR_TOKEN                        # GitHub Container Registry token
```

#### Kubernetes & Cloud

```bash
KUBE_CONFIG_STAGING               # Staging cluster kubeconfig (base64)
KUBE_CONFIG_PRODUCTION            # Production cluster kubeconfig (base64)
DO_API_TOKEN                      # DigitalOcean API token
DO_SPACES_ACCESS_KEY              # DigitalOcean Spaces access key
DO_SPACES_SECRET_KEY              # DigitalOcean Spaces secret key
```

#### Database

```bash
DATABASE_URL_STAGING              # Staging database connection string
DATABASE_URL_PRODUCTION           # Production database connection string
POSTGRES_PASSWORD                 # PostgreSQL admin password
```

#### Notifications

```bash
SLACK_WEBHOOK_URL                 # Slack incoming webhook
EMAIL_USERNAME                    # SMTP username
EMAIL_PASSWORD                    # SMTP password
INCIDENT_EMAIL_LIST               # Comma-separated incident email list
```

#### Monitoring

```bash
GRAFANA_API_KEY                   # Grafana API key for annotations
SENTRY_DSN                        # Sentry error tracking DSN
DATADOG_API_KEY                   # Datadog API key (optional)
```

#### Security

```bash
COSIGN_PRIVATE_KEY                # Container image signing key
COSIGN_PASSWORD                   # Cosign key password
GITHUB_TOKEN                      # Auto-provided by GitHub Actions
```

### Repository Variables

Set these in Settings → Secrets and variables → Actions → Variables:

```bash
DOCKER_REGISTRY=ghcr.io
IMAGE_NAME=${{ github.repository }}
STAGING_URL=https://staging.insightpulseai.net
PRODUCTION_URL=https://insightpulseai.net
ODOO_VERSION=19.0
PYTHON_VERSION=3.11
POSTGRES_VERSION=16
```

### How to Create Secrets

```bash
# Using GitHub CLI
gh secret set DOCKER_USERNAME -b"myusername"
gh secret set DOCKER_PASSWORD < docker-token.txt

# Using GitHub Web UI
# 1. Go to repository Settings
# 2. Secrets and variables → Actions
# 3. New repository secret
# 4. Enter name and value
# 5. Add secret

# For kubeconfig (needs base64 encoding)
cat ~/.kube/config | base64 -w 0 | gh secret set KUBE_CONFIG_PRODUCTION
```

## Best Practices

### 1. Security

✅ **DO**:
- Use GitHub secrets for all sensitive data
- Enable secret scanning in repository settings
- Use environment protection rules for production
- Sign container images with Cosign
- Scan dependencies and containers before deployment
- Rotate secrets regularly (every 90 days)
- Use minimal permissions for service accounts

❌ **DON'T**:
- Hardcode credentials in workflows
- Disable security scans to "speed up" CI
- Use same credentials across environments
- Skip approval for production deployments
- Commit secrets to git (even in .env files)

### 2. Performance

✅ **DO**:
- Use caching for dependencies and Docker layers
- Run jobs in parallel when possible
- Use matrix builds for multi-version testing
- Limit test scope to changed files when appropriate
- Use self-hosted runners for heavy workloads

❌ **DON'T**:
- Run full test suite on every commit
- Build Docker images on every push to feature branches
- Use GitHub-hosted runners for compute-intensive tasks
- Skip caching to "ensure fresh builds"

### 3. Reliability

✅ **DO**:
- Always create database backups before deployments
- Keep blue deployment for instant rollback
- Implement comprehensive health checks
- Use retry logic for flaky operations
- Monitor workflow success rates
- Document incident response procedures

❌ **DON'T**:
- Deploy to production without staging validation
- Skip health checks to save time
- Delete old deployments immediately
- Ignore failed workflows
- Deploy during peak business hours

### 4. Maintainability

✅ **DO**:
- Use reusable workflows for common tasks
- Document workflow inputs and outputs
- Keep workflows under 500 lines (split if larger)
- Use clear job and step names
- Version pin all actions and dependencies
- Add comments for complex logic

❌ **DON'T**:
- Copy-paste entire workflows (use reusable)
- Use latest tags for actions (pin to specific versions)
- Leave TODO comments in production workflows
- Mix multiple responsibilities in one workflow

## Troubleshooting

### Common Issues

#### 1. Workflow Not Triggering

**Symptoms**: Push to main/develop doesn't trigger workflow

**Solutions**:
```yaml
# Check trigger configuration
on:
  push:
    branches: [main, develop]  # Ensure branch names match
  pull_request:
    branches: [main, develop]

# Check workflow file location
# Must be in: .github/workflows/
# Not in:     .github/workflow/ (missing 's')
```

#### 2. Docker Build Failures

**Symptoms**: "no space left on device" or build timeout

**Solutions**:
```yaml
# Add cleanup step before build
- name: Clean Docker
  run: |
    docker system prune -af --volumes
    docker buildx prune -af

# Use BuildKit with better caching
- name: Build and push
  uses: docker/build-push-action@v5
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

#### 3. Test Failures in CI but Pass Locally

**Symptoms**: Tests pass locally but fail in GitHub Actions

**Solutions**:
```yaml
# Ensure same Python version
- uses: actions/setup-python@v5
  with:
    python-version: '3.11'  # Match local version exactly

# Check for timing issues
- name: Run tests
  run: |
    pytest tests/ --timeout=300  # Add timeout
  env:
    CI: true  # Some tests check for CI environment

# Verify database state
- name: Setup test database
  run: |
    psql -U odoo -c "DROP DATABASE IF EXISTS test_db;"
    psql -U odoo -c "CREATE DATABASE test_db;"
```

#### 4. Deployment Timeouts

**Symptoms**: Deployment step times out after 10 minutes

**Solutions**:
```yaml
# Increase timeout
- name: Deploy to production
  timeout-minutes: 30  # Default is 360 (6 hours)

# Check rollout status with longer timeout
- name: Wait for rollout
  run: |
    kubectl rollout status deployment/odoo \
      -n production \
      --timeout=15m  # Increase from default 10m
```

#### 5. Secret Not Found

**Symptoms**: "Error: Secret DOCKER_PASSWORD not found"

**Solutions**:
```bash
# Verify secret exists
gh secret list

# Check secret name matches exactly (case-sensitive)
# Workflow: ${{ secrets.DOCKER_PASSWORD }}
# Secret name: DOCKER_PASSWORD (not docker_password)

# For organization secrets, check access
# Settings → Secrets → Actions → Organization secrets
# Ensure repository is in "Selected repositories"

# Re-create secret if still failing
gh secret delete DOCKER_PASSWORD
gh secret set DOCKER_PASSWORD -b"your-token"
```

#### 6. Kubernetes Connection Issues

**Symptoms**: "Unable to connect to cluster"

**Solutions**:
```bash
# Verify kubeconfig is base64 encoded correctly
cat ~/.kube/config | base64 -w 0 > kubeconfig.b64
gh secret set KUBE_CONFIG_PRODUCTION < kubeconfig.b64

# Test connection in workflow
- name: Test kubectl
  run: |
    echo "${{ secrets.KUBE_CONFIG_PRODUCTION }}" | base64 -d > /tmp/kubeconfig
    export KUBECONFIG=/tmp/kubeconfig
    kubectl cluster-info
    kubectl get nodes
```

### Debug Mode

Enable debug logging for workflows:

```yaml
# Add to workflow
jobs:
  debug:
    runs-on: ubuntu-latest
    steps:
      - name: Dump GitHub context
        env:
          GITHUB_CONTEXT: ${{ toJson(github) }}
        run: echo "$GITHUB_CONTEXT"

      - name: Dump runner context
        env:
          RUNNER_CONTEXT: ${{ toJson(runner) }}
        run: echo "$RUNNER_CONTEXT"
```

Or enable via GitHub:
1. Go to repository Settings
2. Secrets and variables → Actions → Variables
3. Add variable: `ACTIONS_RUNNER_DEBUG` = `true`
4. Add variable: `ACTIONS_STEP_DEBUG` = `true`

### Getting Help

1. **Check workflow run logs**
   - Go to Actions tab → Select failed run → Click on failed job
   - Expand failed step to see detailed logs

2. **Review recent changes**
   ```bash
   # See what changed in workflows
   git log --oneline .github/workflows/
   git diff HEAD~1 .github/workflows/comprehensive-cicd.yml
   ```

3. **Test locally with act**
   ```bash
   # Install act (GitHub Actions local runner)
   brew install act  # macOS

   # Run specific job locally
   act -j test --secret-file .secrets

   # List available jobs
   act -l
   ```

4. **Community Support**
   - [GitHub Actions Documentation](https://docs.github.com/en/actions)
   - [GitHub Community Forum](https://github.community/)
   - [Stack Overflow](https://stackoverflow.com/questions/tagged/github-actions)

## Additional Resources

- [Odoo Development Documentation](https://www.odoo.com/documentation/19.0/developer.html)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Kubernetes Deployment Strategies](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [GitHub Actions Security Hardening](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)

---

**Last Updated**: 2025-11-10
**Maintained by**: InsightPulseAI DevOps Team
**License**: AGPL-3.0
