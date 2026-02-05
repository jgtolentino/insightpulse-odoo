# GitHub Actions Workflows Development

**Skill ID:** `github-actions-workflows`
**Version:** 1.0.0
**Category:** GitHub Developer Program, CI/CD, Automation
**Expertise Level:** Expert

---

## 🎯 Purpose

This skill enables AI agents to design and implement production-grade GitHub Actions workflows for CI/CD, automation, and DevOps tasks, following best practices for performance, security, and maintainability.

### Key Capabilities
- Multi-job workflow orchestration
- Matrix builds and parallel execution
- Reusable workflows and composite actions
- Custom actions development (Docker, JavaScript, Composite)
- Secrets and environment management
- Deployment strategies (blue-green, canary, rolling)
- Workflow security and OIDC authentication

---

## 🧠 Core Competencies

### 1. Advanced Workflow Architecture

#### Multi-Stage CI/CD Pipeline
```yaml
# .github/workflows/ci-cd-pipeline.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: write
  pull-requests: write
  actions: read
  id-token: write  # For OIDC authentication

env:
  NODE_VERSION: '18'
  PYTHON_VERSION: '3.11'

jobs:
  # Stage 1: Code Quality
  lint:
    name: Code Quality Checks
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install flake8 black mypy

      - name: Run linters
        run: |
          flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
          black . --check
          mypy . --strict

  # Stage 2: Testing
  test:
    name: Test Suite
    runs-on: ubuntu-latest
    needs: lint
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
        os: [ubuntu-latest, macos-latest, windows-latest]
      fail-fast: false

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests with coverage
        run: |
          pytest tests/ -v --cov=. --cov-report=xml

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml
          flags: unittests
          name: ${{ matrix.os }}-${{ matrix.python-version }}

  # Stage 3: Security Scanning
  security:
    name: Security Scanning
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results.sarif'

      - name: Check for secrets
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD

  # Stage 4: Build
  build:
    name: Build Application
    runs-on: ubuntu-latest
    needs: [test, security]
    outputs:
      version: ${{ steps.version.outputs.version }}

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for versioning

      - name: Generate version
        id: version
        run: |
          VERSION=$(git describe --tags --always --dirty)
          echo "version=$VERSION" >> $GITHUB_OUTPUT
          echo "Building version: $VERSION"

      - name: Build Docker image
        run: |
          docker build \
            --tag ghcr.io/${{ github.repository }}:${{ steps.version.outputs.version }} \
            --tag ghcr.io/${{ github.repository }}:latest \
            --build-arg VERSION=${{ steps.version.outputs.version }} \
            .

      - name: Save Docker image
        run: |
          docker save ghcr.io/${{ github.repository }}:${{ steps.version.outputs.version }} | gzip > image.tar.gz

      - name: Upload build artifact
        uses: actions/upload-artifact@v4
        with:
          name: docker-image
          path: image.tar.gz
          retention-days: 7

  # Stage 5: Deploy to Staging
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/develop'
    environment:
      name: staging
      url: https://staging.insightpulseai.net

    steps:
      - uses: actions/checkout@v4

      - name: Download build artifact
        uses: actions/download-artifact@v4
        with:
          name: docker-image

      - name: Load Docker image
        run: |
          docker load < image.tar.gz

      - name: Configure DigitalOcean CLI
        uses: digitalocean/action-doctl@v2
        with:
          token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}

      - name: Deploy to staging
        run: |
          doctl apps create-deployment ${{ secrets.STAGING_APP_ID }}

      - name: Wait for deployment
        run: |
          for i in {1..12}; do
            status=$(doctl apps get ${{ secrets.STAGING_APP_ID }} --format Phase --no-header)
            echo "Deployment status: $status"
            if [ "$status" = "ACTIVE" ]; then
              echo "✅ Deployment successful"
              exit 0
            fi
            sleep 10
          done
          echo "❌ Deployment timeout"
          exit 1

      - name: Run smoke tests
        run: |
          make deploy-smoke ENDPOINT=https://staging.insightpulseai.net

  # Stage 6: Deploy to Production
  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    environment:
      name: production
      url: https://insightpulseai.net

    steps:
      - uses: actions/checkout@v4

      - name: Download build artifact
        uses: actions/download-artifact@v4
        with:
          name: docker-image

      - name: Load Docker image
        run: |
          docker load < image.tar.gz

      - name: Push to GitHub Container Registry
        run: |
          echo ${{ secrets.GITHUB_TOKEN }} | docker login ghcr.io -u ${{ github.actor }} --password-stdin
          docker push ghcr.io/${{ github.repository }}:${{ needs.build.outputs.version }}
          docker push ghcr.io/${{ github.repository }}:latest

      - name: Deploy to production
        uses: digitalocean/action-doctl@v2
        with:
          token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}
        env:
          VERSION: ${{ needs.build.outputs.version }}

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        if: startsWith(github.ref, 'refs/tags/')
        with:
          files: |
            CHANGELOG.md
            LICENSE
          generate_release_notes: true
```

### 2. Reusable Workflows

#### Shared Deployment Workflow
```yaml
# .github/workflows/deploy-reusable.yml
name: Reusable Deploy Workflow

on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
        description: 'Environment to deploy to (staging, production)'
      version:
        required: true
        type: string
        description: 'Version to deploy'
      app_id:
        required: true
        type: string
        description: 'DigitalOcean App ID'
    secrets:
      digitalocean_token:
        required: true
      slack_webhook:
        required: false
    outputs:
      deployment_url:
        description: 'URL of deployed application'
        value: ${{ jobs.deploy.outputs.url }}

jobs:
  deploy:
    name: Deploy to ${{ inputs.environment }}
    runs-on: ubuntu-latest
    environment:
      name: ${{ inputs.environment }}
    outputs:
      url: ${{ steps.deploy.outputs.url }}

    steps:
      - uses: actions/checkout@v4

      - name: Configure DigitalOcean CLI
        uses: digitalocean/action-doctl@v2
        with:
          token: ${{ secrets.digitalocean_token }}

      - name: Deploy application
        id: deploy
        run: |
          doctl apps create-deployment ${{ inputs.app_id }}
          url=$(doctl apps get ${{ inputs.app_id }} --format DefaultIngress --no-header)
          echo "url=$url" >> $GITHUB_OUTPUT

      - name: Notify Slack
        if: secrets.slack_webhook != ''
        run: |
          curl -X POST ${{ secrets.slack_webhook }} \
            -H 'Content-Type: application/json' \
            -d '{
              "text": "🚀 Deployed ${{ inputs.version }} to ${{ inputs.environment }}",
              "blocks": [{
                "type": "section",
                "text": {
                  "type": "mrkdwn",
                  "text": "*Deployment Successful*\n• Environment: `${{ inputs.environment }}`\n• Version: `${{ inputs.version }}`\n• URL: <${{ steps.deploy.outputs.url }}>"
                }
              }]
            }'
```

#### Using Reusable Workflow
```yaml
# .github/workflows/production-deploy.yml
name: Production Deployment

on:
  release:
    types: [published]

jobs:
  deploy-prod:
    uses: ./.github/workflows/deploy-reusable.yml
    with:
      environment: production
      version: ${{ github.event.release.tag_name }}
      app_id: ${{ vars.PRODUCTION_APP_ID }}
    secrets:
      digitalocean_token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}
      slack_webhook: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### 3. Custom Composite Actions

#### Setup Python Environment Action
```yaml
# .github/actions/setup-python-env/action.yml
name: Setup Python Environment
description: 'Sets up Python with caching and installs dependencies'

inputs:
  python-version:
    description: 'Python version to use'
    required: false
    default: '3.11'
  cache-key-suffix:
    description: 'Additional suffix for cache key'
    required: false
    default: ''
  install-dev:
    description: 'Install development dependencies'
    required: false
    default: 'false'

outputs:
  python-version:
    description: 'Installed Python version'
    value: ${{ steps.setup.outputs.python-version }}
  cache-hit:
    description: 'Whether cache was hit'
    value: ${{ steps.cache.outputs.cache-hit }}

runs:
  using: composite
  steps:
    - name: Setup Python
      id: setup
      uses: actions/setup-python@v5
      with:
        python-version: ${{ inputs.python-version }}

    - name: Get pip cache dir
      id: pip-cache
      shell: bash
      run: |
        echo "dir=$(pip cache dir)" >> $GITHUB_OUTPUT

    - name: Cache pip dependencies
      id: cache
      uses: actions/cache@v4
      with:
        path: ${{ steps.pip-cache.outputs.dir }}
        key: ${{ runner.os }}-pip-${{ inputs.python-version }}-${{ hashFiles('**/requirements*.txt') }}-${{ inputs.cache-key-suffix }}
        restore-keys: |
          ${{ runner.os }}-pip-${{ inputs.python-version }}-
          ${{ runner.os }}-pip-

    - name: Install dependencies
      shell: bash
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        if [ "${{ inputs.install-dev }}" = "true" ]; then
          pip install -r requirements-dev.txt
        fi
```

#### Usage
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python environment
        uses: ./.github/actions/setup-python-env
        with:
          python-version: '3.11'
          install-dev: 'true'

      - name: Run tests
        run: pytest
```

### 4. Docker Container Actions

#### Custom Python Linter Action
```dockerfile
# .github/actions/python-linter/Dockerfile
FROM python:3.11-slim

RUN pip install --no-cache-dir flake8 black mypy pylint

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
```

```bash
# .github/actions/python-linter/entrypoint.sh
#!/bin/bash
set -e

echo "🔍 Running Python linters..."

# Run flake8
echo "Running flake8..."
flake8 . --count --statistics || exit_code=$?

# Run black
echo "Running black..."
black . --check || exit_code=$?

# Run mypy
echo "Running mypy..."
mypy . || exit_code=$?

# Run pylint
echo "Running pylint..."
pylint **/*.py --exit-zero --score=y || exit_code=$?

if [ "${exit_code}" -ne 0 ]; then
  echo "❌ Linting failed"
  exit ${exit_code}
fi

echo "✅ All linters passed"
```

```yaml
# .github/actions/python-linter/action.yml
name: Python Linter
description: 'Runs comprehensive Python linting'

inputs:
  path:
    description: 'Path to Python code'
    required: false
    default: '.'

runs:
  using: docker
  image: Dockerfile
  args:
    - ${{ inputs.path }}
```

### 5. Advanced Patterns

#### Conditional Job Execution
```yaml
# .github/workflows/smart-ci.yml
name: Smart CI

on: [push, pull_request]

jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      backend: ${{ steps.filter.outputs.backend }}
      frontend: ${{ steps.filter.outputs.frontend }}
      docs: ${{ steps.filter.outputs.docs }}
    steps:
      - uses: actions/checkout@v4

      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            backend:
              - 'apps/**/*.py'
              - 'requirements*.txt'
            frontend:
              - 'frontend/**/*.{js,jsx,ts,tsx}'
              - 'package*.json'
            docs:
              - 'docs/**/*.md'
              - '*.md'

  test-backend:
    needs: detect-changes
    if: needs.detect-changes.outputs.backend == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pytest tests/

  test-frontend:
    needs: detect-changes
    if: needs.detect-changes.outputs.frontend == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm test

  build-docs:
    needs: detect-changes
    if: needs.detect-changes.outputs.docs == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make docs
```

#### Dynamic Matrix from JSON
```yaml
# .github/workflows/dynamic-matrix.yml
name: Dynamic Matrix Testing

on: [push]

jobs:
  generate-matrix:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.set-matrix.outputs.matrix }}
    steps:
      - uses: actions/checkout@v4

      - name: Generate test matrix
        id: set-matrix
        run: |
          # Read matrix configuration from file
          matrix=$(cat .github/test-matrix.json | jq -c .)
          echo "matrix=$matrix" >> $GITHUB_OUTPUT

  test:
    needs: generate-matrix
    runs-on: ${{ matrix.os }}
    strategy:
      matrix: ${{ fromJson(needs.generate-matrix.outputs.matrix) }}
    steps:
      - uses: actions/checkout@v4
      - run: echo "Testing on ${{ matrix.os }} with Python ${{ matrix.python }}"
```

```json
// .github/test-matrix.json
{
  "include": [
    {"os": "ubuntu-latest", "python": "3.10"},
    {"os": "ubuntu-latest", "python": "3.11"},
    {"os": "macos-latest", "python": "3.11"},
    {"os": "windows-latest", "python": "3.11"}
  ]
}
```

---

## ✅ Validation Criteria

### Workflow Quality
- ✅ Execution time <15 minutes for CI pipeline
- ✅ Proper job dependencies (no unnecessary blocking)
- ✅ Artifact cleanup (retention < 30 days)
- ✅ Secrets never logged or exposed
- ✅ Idempotent steps (can be safely retried)

### Performance Optimization
- ✅ Caching enabled for dependencies
- ✅ Parallel job execution where possible
- ✅ Matrix builds for cross-platform testing
- ✅ Conditional execution based on file changes

---

## 🎯 Usage Examples

### Example 1: Monorepo Selective Testing
```yaml
name: Monorepo CI

on: [push]

jobs:
  changes:
    runs-on: ubuntu-latest
    outputs:
      packages: ${{ steps.filter.outputs.changes }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            package1:
              - 'packages/package1/**'
            package2:
              - 'packages/package2/**'

  test:
    needs: changes
    if: needs.changes.outputs.packages != '[]'
    strategy:
      matrix:
        package: ${{ fromJson(needs.changes.outputs.packages) }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: cd packages/${{ matrix.package }} && npm test
```

### Example 2: Automated Dependency Updates
```yaml
name: Update Dependencies

on:
  schedule:
    - cron: '0 0 * * 1'  # Every Monday
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Update Python dependencies
        run: |
          pip install pip-tools
          pip-compile --upgrade requirements.in

      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v6
        with:
          commit-message: 'chore: Update Python dependencies'
          title: 'chore: Weekly dependency updates'
          body: |
            Automated dependency updates for this week.

            Please review changes and merge if CI passes.
          branch: deps/weekly-update
          labels: dependencies
```

---

## 📊 Success Metrics

### CI/CD Performance
- **Pipeline Duration**: <10 min (95th percentile)
- **Success Rate**: >98%
- **Deployment Frequency**: 10+ per day
- **Mean Time to Recovery**: <5 minutes

### Cost Optimization
- **Monthly Actions Minutes**: <2000 (within free tier)
- **Artifact Storage**: <500 MB
- **Cache Hit Rate**: >80%

---

## 🔗 Related Skills
- `automation-devops-expert` - DevOps automation
- `github-api-integration` - GitHub API usage
- `github-apps-development` - GitHub Apps

---

## 📚 References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Reusable Workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
- [Custom Actions](https://docs.github.com/en/actions/creating-actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

---

**Maintained by:** InsightPulse AI Team
**License:** AGPL-3.0
