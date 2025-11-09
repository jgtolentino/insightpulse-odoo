# Quick Start Guide

## 1. Install Dependencies

```bash
cd tools/openai-cookbook-automation
pip install -r requirements.txt
```

## 2. Verify Installation

```bash
# Check scripts are executable
ls -la scripts/*.py

# Test help messages
python scripts/notebook_test_runner.py --help
python scripts/notebook_metadata_validator.py --help
python scripts/generate_notebook_index.py --help
```

## 3. Run Your First Test

### Option A: Structure Test (No API Key Required)

```bash
# Test notebooks in examples directory
python scripts/notebook_test_runner.py \
  --mode structure \
  --pattern "examples/**/*.ipynb"
```

### Option B: Metadata Validation

```bash
# Validate notebook metadata
python scripts/notebook_metadata_validator.py \
  --pattern "examples/**/*.ipynb"
```

### Option C: Generate Index

```bash
# Generate searchable index
python scripts/generate_notebook_index.py
```

## 4. (Optional) Run Smoke Tests

**Requires `OPENAI_API_KEY`**

```bash
export OPENAI_API_KEY="sk-..."

python scripts/notebook_test_runner.py \
  --mode smoke \
  --pattern "examples/**/*.ipynb" \
  --timeout 300
```

## 5. Apply to OpenAI Cookbook Fork

```bash
# 1. Fork and clone OpenAI Cookbook
gh repo fork openai/openai-cookbook --clone
cd openai-cookbook

# 2. Copy automation files
cp -r /path/to/insightpulse-odoo/tools/openai-cookbook-automation/scripts ./tools/
cp -r /path/to/insightpulse-odoo/tools/openai-cookbook-automation/workflows/* .github/workflows/
cp /path/to/insightpulse-odoo/tools/openai-cookbook-automation/templates/pull_request_template.md .github/
mkdir -p .github/ISSUE_TEMPLATE
cp /path/to/insightpulse-odoo/tools/openai-cookbook-automation/templates/*.yml .github/ISSUE_TEMPLATE/
cp -r /path/to/insightpulse-odoo/tools/openai-cookbook-automation/devcontainer .devcontainer

# 3. Install dependencies
pip install -r /path/to/insightpulse-odoo/tools/openai-cookbook-automation/requirements.txt

# 4. Test locally
python tools/notebook_test_runner.py --mode structure

# 5. Commit and push
git checkout -b feat/notebook-automation
git add .
git commit -m "ci: add notebook automation suite"
git push origin feat/notebook-automation

# 6. Create PR
gh pr create --title "Add Comprehensive Notebook Automation" \
  --body "See docs/OPENAI_COOKBOOK_IMPROVEMENTS.md for details"
```

## 6. Using Dev Container

If you use VS Code or GitHub Codespaces:

```bash
# Copy dev container to target repo
cp -r devcontainer /path/to/target-repo/.devcontainer

# Open in VS Code
code /path/to/target-repo

# Command Palette → "Dev Containers: Reopen in Container"
# Wait for setup (~2-3 minutes)
# Everything is pre-installed!
```

## Common Issues

### Import Error: nbformat not found

```bash
pip install nbformat nbclient jupyter
```

### Permission Denied

```bash
chmod +x scripts/*.py
```

### API Key Not Working

```bash
# Verify key is set
echo $OPENAI_API_KEY

# If empty, set it
export OPENAI_API_KEY="sk-..."
```

## Next Steps

- Read full [README.md](README.md)
- Review [OpenAI Cookbook Improvements Plan](../../../docs/OPENAI_COOKBOOK_IMPROVEMENTS.md)
- Check example workflow: [notebook-ci.yml](workflows/notebook-ci.yml)
- See PR template: [pull_request_template.md](templates/pull_request_template.md)
