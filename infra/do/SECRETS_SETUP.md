# GitHub Secrets Configuration Guide

Comprehensive guide for configuring GitHub Secrets required for CI/CD pipelines in the InsightPulse Odoo SaaS Parity Platform.

## Table of Contents

- [Overview](#overview)
- [Required Secrets](#required-secrets)
- [Setup Instructions](#setup-instructions)
- [Security Best Practices](#security-best-practices)
- [Troubleshooting](#troubleshooting)
- [Workflow Usage Examples](#workflow-usage-examples)

---

## Overview

The InsightPulse Odoo platform uses GitHub Actions for continuous integration and deployment to DigitalOcean App Platform and Supabase. This guide documents all required secrets and their configuration process.

**Deployment Stack:**
- **CI/CD**: GitHub Actions
- **Application Hosting**: DigitalOcean App Platform
- **Database**: Supabase PostgreSQL
- **Frontend**: Vercel (optional)

**GitHub Actions Workflows:**
- `.github/workflows/digitalocean-deploy.yml` - Automated deployment to DigitalOcean
- `.github/workflows/ci.yml` - Continuous integration checks

---

## Required Secrets

### 1. DO_APP_ID
**Purpose**: DigitalOcean App Platform application identifier
**Format**: UUID (e.g., `b1bb1b07-46a6-4bbb-85a2-e1e8c7f263b9`)
**Usage**: Deployment targeting, app spec updates
**Required By**: `digitalocean-deploy.yml`

### 2. DO_ACCESS_TOKEN
**Purpose**: DigitalOcean API authentication token
**Format**: Alphanumeric string (e.g., `dop_v1_abc123...`)
**Usage**: All DigitalOcean CLI operations
**Required By**: `digitalocean-deploy.yml`

### 3. SUPABASE_PROJECT_REF
**Purpose**: Supabase project reference identifier
**Format**: Alphanumeric string (e.g., `xkxyvboeubffxxbebsll`)
**Usage**: Database connections, migrations
**Required By**: `ci.yml`, `digitalocean-deploy.yml`

### 4. SUPABASE_ACCESS_TOKEN
**Purpose**: Supabase API authentication token
**Format**: JWT token starting with `sbp_`
**Usage**: Database operations, schema migrations
**Required By**: `ci.yml`, `digitalocean-deploy.yml`

### 5. GITHUB_TOKEN (Auto-Provided)
**Purpose**: GitHub API authentication
**Format**: Automatically generated per workflow run
**Usage**: Repository operations, PR comments
**Required By**: All workflows (automatic)

---

## Setup Instructions

### Prerequisites

Before configuring GitHub Secrets, ensure you have:

1. **DigitalOcean Account** with App Platform access
2. **Supabase Account** with project access
3. **GitHub Repository** admin permissions
4. **CLI Tools** (optional but recommended):
   - `doctl` (DigitalOcean CLI)
   - `supabase` (Supabase CLI)
   - `gh` (GitHub CLI)

---

### Step 1: Obtain DigitalOcean Credentials

#### A. Get DO_ACCESS_TOKEN

**Via DigitalOcean Web Console:**

1. Log in to [DigitalOcean Cloud Console](https://cloud.digitalocean.com)
2. Navigate to **API** section in left sidebar
3. Click **Generate New Token**
4. Configure token:
   - **Token Name**: `GitHub Actions CI/CD`
   - **Expiration**: 90 days (recommended) or No expiry
   - **Scopes**: Select **Write** (read + write permissions)
5. Click **Generate Token**
6. **IMPORTANT**: Copy the token immediately (shown only once)
7. Save securely - this is your `DO_ACCESS_TOKEN`

**Via doctl CLI:**

```bash
# Authenticate doctl
doctl auth init

# Verify authentication
doctl account get

# List existing tokens (optional)
doctl auth list
```

**Token Format:**
```
dop_v1_abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
```

#### B. Get DO_APP_ID

**Via DigitalOcean Web Console:**

1. Navigate to [Apps](https://cloud.digitalocean.com/apps)
2. Click on your application (e.g., `ade-ocr-backend`)
3. Copy the App ID from the URL:
   ```
   https://cloud.digitalocean.com/apps/b1bb1b07-46a6-4bbb-85a2-e1e8c7f263b9
                                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   ```

**Via doctl CLI:**

```bash
# List all apps
doctl apps list --format ID,Spec.Name

# Get specific app details
doctl apps get b1bb1b07-46a6-4bbb-85a2-e1e8c7f263b9
```

**App ID Format:**
```
b1bb1b07-46a6-4bbb-85a2-e1e8c7f263b9
```

---

### Step 2: Obtain Supabase Credentials

#### A. Get SUPABASE_PROJECT_REF

**Via Supabase Dashboard:**

1. Log in to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project
3. Navigate to **Settings** → **General**
4. Copy **Reference ID** from Project Settings section

**Location in Dashboard:**
```
Project Settings
├── General
│   ├── Name: InsightPulse Odoo
│   ├── Reference ID: xkxyvboeubffxxbebsll  ← Copy this
│   └── Region: AWS us-east-1
```

**Via Supabase CLI:**

```bash
# List projects
supabase projects list

# Get project details
supabase projects info
```

**Project Ref Format:**
```
xkxyvboeubffxxbebsll
```

#### B. Get SUPABASE_ACCESS_TOKEN

**Via Supabase Dashboard:**

1. Navigate to **Settings** → **API**
2. Scroll to **Access Tokens** section
3. Click **Generate new token**
4. Configure token:
   - **Name**: `GitHub Actions CI/CD`
   - **Scopes**: Select required permissions (Management API)
5. Click **Generate token**
6. Copy the token immediately (shown only once)

**Via Supabase CLI:**

```bash
# Generate access token
supabase login

# Verify authentication
supabase projects list
```

**Token Format:**
```
sbp_c28f4a28eeb3d2f41719e289b9687c4dbda2580a
```

**Security Note:** This is NOT the same as:
- `SUPABASE_ANON_KEY` (public client key)
- `SUPABASE_SERVICE_ROLE_KEY` (backend service key)

---

### Step 3: Configure GitHub Secrets

#### Via GitHub Web Interface

1. Navigate to your repository on GitHub
2. Go to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. For each secret:
   - Enter **Name** (exact case-sensitive match)
   - Paste **Value** (no quotes, trim whitespace)
   - Click **Add secret**

**Add the following secrets:**

| Secret Name | Example Value | Notes |
|-------------|---------------|-------|
| `DO_APP_ID` | `b1bb1b07-46a6-4bbb-85a2-e1e8c7f263b9` | UUID format |
| `DO_ACCESS_TOKEN` | `dop_v1_abc123...` | Starts with `dop_v1_` |
| `SUPABASE_PROJECT_REF` | `xkxyvboeubffxxbebsll` | Lowercase alphanumeric |
| `SUPABASE_ACCESS_TOKEN` | `sbp_c28f4a28...` | Starts with `sbp_` |

#### Via GitHub CLI

```bash
# Navigate to repository
cd /Users/tbwa/insightpulse-odoo

# Set DO_APP_ID
gh secret set DO_APP_ID --body "b1bb1b07-46a6-4bbb-85a2-e1e8c7f263b9"

# Set DO_ACCESS_TOKEN
gh secret set DO_ACCESS_TOKEN --body "dop_v1_your_token_here"

# Set SUPABASE_PROJECT_REF
gh secret set SUPABASE_PROJECT_REF --body "xkxyvboeubffxxbebsll"

# Set SUPABASE_ACCESS_TOKEN
gh secret set SUPABASE_ACCESS_TOKEN --body "sbp_your_token_here"

# Verify secrets
gh secret list
```

#### Via Environment Variables (Local Testing)

For local testing, add to `~/.zshrc` or `~/.bashrc`:

```bash
# DigitalOcean
export DO_APP_ID="b1bb1b07-46a6-4bbb-85a2-e1e8c7f263b9"
export DO_ACCESS_TOKEN="dop_v1_your_token_here"

# Supabase
export SUPABASE_PROJECT_REF="xkxyvboeubffxxbebsll"
export SUPABASE_ACCESS_TOKEN="sbp_your_token_here"
```

**Load configuration:**
```bash
source ~/.zshrc
```

---

### Step 4: Verify Configuration

#### Test DigitalOcean Access

```bash
# Authenticate doctl
doctl auth init --access-token "$DO_ACCESS_TOKEN"

# Test app access
doctl apps get "$DO_APP_ID"

# Expected output:
# ID: b1bb1b07-46a6-4bbb-85a2-e1e8c7f263b9
# Spec.Name: ade-ocr-backend
# Region: sgp
```

#### Test Supabase Access

```bash
# Set project ref
export SUPABASE_PROJECT_REF="xkxyvboeubffxxbebsll"

# Test connection
supabase projects info

# Expected output:
# Project ID: xkxyvboeubffxxbebsll
# Project Name: InsightPulse Odoo
# Region: us-east-1
```

#### Test GitHub Secrets (CI/CD)

Create a test workflow:

```yaml
# .github/workflows/test-secrets.yml
name: Test Secrets Configuration

on:
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Verify DO_APP_ID
        run: |
          if [ -z "${{ secrets.DO_APP_ID }}" ]; then
            echo "ERROR: DO_APP_ID not set"
            exit 1
          fi
          echo "DO_APP_ID is configured"

      - name: Verify DO_ACCESS_TOKEN
        run: |
          if [ -z "${{ secrets.DO_ACCESS_TOKEN }}" ]; then
            echo "ERROR: DO_ACCESS_TOKEN not set"
            exit 1
          fi
          echo "DO_ACCESS_TOKEN is configured"

      - name: Verify SUPABASE_PROJECT_REF
        run: |
          if [ -z "${{ secrets.SUPABASE_PROJECT_REF }}" ]; then
            echo "ERROR: SUPABASE_PROJECT_REF not set"
            exit 1
          fi
          echo "SUPABASE_PROJECT_REF is configured"

      - name: Verify SUPABASE_ACCESS_TOKEN
        run: |
          if [ -z "${{ secrets.SUPABASE_ACCESS_TOKEN }}" ]; then
            echo "ERROR: SUPABASE_ACCESS_TOKEN not set"
            exit 1
          fi
          echo "SUPABASE_ACCESS_TOKEN is configured"

      - name: Test doctl authentication
        run: |
          curl -sL https://github.com/digitalocean/doctl/releases/download/v1.104.0/doctl-1.104.0-linux-amd64.tar.gz | tar -xzv
          sudo mv doctl /usr/local/bin
          doctl auth init --access-token "${{ secrets.DO_ACCESS_TOKEN }}"
          doctl apps get "${{ secrets.DO_APP_ID }}"
```

**Run test:**
```bash
gh workflow run test-secrets.yml
gh run watch
```

---

## Security Best Practices

### Secret Management

1. **Rotation Schedule**
   - Rotate tokens every 90 days
   - Update GitHub Secrets immediately after rotation
   - Test new tokens before deactivating old ones

2. **Access Control**
   - Limit repository access to trusted collaborators
   - Use separate tokens for staging and production
   - Never commit secrets to repository

3. **Token Scopes**
   - Use minimum required permissions
   - DigitalOcean: Read-only for monitoring, Write for deployments
   - Supabase: Management API access only

4. **Monitoring**
   - Enable audit logs for secret access
   - Monitor GitHub Actions logs for unauthorized usage
   - Set up alerts for failed authentication attempts

### Secure Token Storage

**DO NOT:**
- Commit secrets to `.env` files
- Share secrets via email or chat
- Log secret values in workflow outputs
- Use personal access tokens for production

**DO:**
- Use GitHub Secrets for CI/CD
- Store local secrets in `~/.zshrc` (not tracked by git)
- Use Supabase Vault for application secrets
- Implement secret scanning in pre-commit hooks

### Emergency Procedures

**If Token Compromised:**

1. **Immediate Actions**
   ```bash
   # Revoke DigitalOcean token
   doctl auth list
   doctl auth remove <token-name>

   # Revoke Supabase token
   # Via Dashboard: Settings → API → Revoke token

   # Rotate GitHub Secrets
   gh secret set DO_ACCESS_TOKEN --body "new_token_here"
   ```

2. **Audit Access**
   - Review GitHub Actions logs for unauthorized runs
   - Check DigitalOcean audit logs for suspicious API calls
   - Review Supabase activity logs

3. **Notify Team**
   - Document incident in security log
   - Inform team members via secure channel
   - Update incident response procedures

---

## Troubleshooting

### Common Issues

#### Issue 1: Workflow Fails with "Secret not found"

**Symptoms:**
```
Error: The secret DO_ACCESS_TOKEN was not found
```

**Solutions:**
1. Verify secret name matches exactly (case-sensitive)
2. Check secret is set at repository level (not organization)
3. Confirm secret has been saved (refresh secrets page)
4. Test with `gh secret list` command

#### Issue 2: DigitalOcean Authentication Failed

**Symptoms:**
```
Error: Unable to authenticate you
```

**Solutions:**
1. Verify token format starts with `dop_v1_`
2. Check token hasn't expired (90-day expiration)
3. Confirm token has Write scope enabled
4. Test locally: `doctl auth init --access-token "$DO_ACCESS_TOKEN"`

#### Issue 3: Supabase Connection Refused

**Symptoms:**
```
Error: Could not connect to project xkxyvboeubffxxbebsll
```

**Solutions:**
1. Verify project ref is correct (lowercase, no spaces)
2. Check Supabase project is not paused
3. Confirm access token has Management API permissions
4. Test with: `supabase projects info`

#### Issue 4: App ID Not Found

**Symptoms:**
```
Error: App b1bb1b07-46a6-4bbb-85a2-e1e8c7f263b9 not found
```

**Solutions:**
1. Verify app exists: `doctl apps list`
2. Confirm app ID is correct UUID format
3. Check DO_ACCESS_TOKEN has access to this app
4. Ensure app hasn't been deleted

#### Issue 5: Workflow Permissions Denied

**Symptoms:**
```
Error: Resource not accessible by integration
```

**Solutions:**
1. Go to **Settings** → **Actions** → **General**
2. Scroll to **Workflow permissions**
3. Select **Read and write permissions**
4. Check **Allow GitHub Actions to create and approve pull requests**
5. Click **Save**

### Debug Workflow

Add debug step to workflows:

```yaml
- name: Debug Secrets
  run: |
    echo "DO_APP_ID length: ${#DO_APP_ID}"
    echo "DO_ACCESS_TOKEN length: ${#DO_ACCESS_TOKEN}"
    echo "SUPABASE_PROJECT_REF: $SUPABASE_PROJECT_REF"
    echo "SUPABASE_ACCESS_TOKEN prefix: ${SUPABASE_ACCESS_TOKEN:0:4}"
  env:
    DO_APP_ID: ${{ secrets.DO_APP_ID }}
    DO_ACCESS_TOKEN: ${{ secrets.DO_ACCESS_TOKEN }}
    SUPABASE_PROJECT_REF: ${{ secrets.SUPABASE_PROJECT_REF }}
    SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
```

**Security Note:** Never echo full token values in logs.

---

## Workflow Usage Examples

### Example 1: DigitalOcean Deployment

```yaml
name: Deploy to DigitalOcean

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install doctl
        uses: digitalocean/action-doctl@v2
        with:
          token: ${{ secrets.DO_ACCESS_TOKEN }}

      - name: Update App Spec
        run: |
          doctl apps update ${{ secrets.DO_APP_ID }} \
            --spec infra/do/ade-ocr-service.yaml

      - name: Create Deployment
        run: |
          doctl apps create-deployment ${{ secrets.DO_APP_ID }} \
            --force-rebuild

      - name: Wait for Deployment
        run: |
          doctl apps list-deployments ${{ secrets.DO_APP_ID }} \
            --format ID,Phase
```

### Example 2: Supabase Migration

```yaml
name: Database Migration

on:
  push:
    paths:
      - 'packages/db/sql/**'

jobs:
  migrate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Supabase CLI
        run: |
          curl -sL https://github.com/supabase/cli/releases/download/v1.123.4/supabase_1.123.4_linux_amd64.tar.gz | tar -xz
          sudo mv supabase /usr/local/bin

      - name: Run Migration
        run: |
          export SUPABASE_ACCESS_TOKEN="${{ secrets.SUPABASE_ACCESS_TOKEN }}"
          export SUPABASE_PROJECT_REF="${{ secrets.SUPABASE_PROJECT_REF }}"

          supabase link --project-ref "$SUPABASE_PROJECT_REF"
          supabase db push
        env:
          SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
          SUPABASE_PROJECT_REF: ${{ secrets.SUPABASE_PROJECT_REF }}
```

### Example 3: Combined Deployment

```yaml
name: Full Stack Deployment

on:
  release:
    types: [published]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Deploy DigitalOcean App
        uses: digitalocean/action-doctl@v2
        with:
          token: ${{ secrets.DO_ACCESS_TOKEN }}

      - run: |
          doctl apps create-deployment ${{ secrets.DO_APP_ID }} \
            --force-rebuild

  migrate-database:
    needs: deploy-backend
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Supabase Migration
        run: |
          # Install Supabase CLI
          curl -sL https://github.com/supabase/cli/releases/download/v1.123.4/supabase_1.123.4_linux_amd64.tar.gz | tar -xz
          sudo mv supabase /usr/local/bin

          # Apply migrations
          supabase link --project-ref "${{ secrets.SUPABASE_PROJECT_REF }}"
          supabase db push
        env:
          SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
          SUPABASE_PROJECT_REF: ${{ secrets.SUPABASE_PROJECT_REF }}

  verify-deployment:
    needs: [deploy-backend, migrate-database]
    runs-on: ubuntu-latest
    steps:
      - name: Health Check
        run: |
          curl -sf https://ade-ocr-backend-d9dru.ondigitalocean.app/health || exit 1
```

---

## Additional Resources

### Official Documentation

- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [DigitalOcean App Platform](https://docs.digitalocean.com/products/app-platform/)
- [DigitalOcean API](https://docs.digitalocean.com/reference/api/api-reference/)
- [Supabase Management API](https://supabase.com/docs/reference/api/introduction)
- [doctl CLI Reference](https://docs.digitalocean.com/reference/doctl/)
- [Supabase CLI Reference](https://supabase.com/docs/reference/cli/introduction)

### Project-Specific Files

- Deployment Specs: `/Users/tbwa/insightpulse-odoo/infra/do/`
- Workflows: `/Users/tbwa/insightpulse-odoo/.github/workflows/`
- Database Migrations: `/Users/tbwa/insightpulse-odoo/packages/db/sql/`
- Environment Constraints: `/Users/tbwa/insightpulse-odoo/CLAUDE.md`

### Support Contacts

- **DigitalOcean Support**: https://www.digitalocean.com/support
- **Supabase Support**: https://supabase.com/support
- **GitHub Support**: https://support.github.com

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2025-10-30 | 1.0.0 | Initial documentation |

---

## License

This documentation is part of the InsightPulse Odoo SaaS Parity Platform.
Copyright © 2025 InsightPulse AI. All rights reserved.
