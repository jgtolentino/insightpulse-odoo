#!/bin/bash
set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 OpenAI Cookbook Dev Container Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Upgrade pip
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip

# Install requirements if exists
if [ -f "requirements.txt" ]; then
    echo "📦 Installing requirements.txt..."
    pip install -r requirements.txt
fi

# Install development dependencies
echo "📦 Installing development tools..."
pip install \
    openai \
    nbformat \
    nbclient \
    jupyter \
    jupyterlab \
    black \
    flake8 \
    isort \
    pylint \
    pytest \
    pytest-cov \
    nbval \
    PyGithub

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x tools/*.py 2>/dev/null || true

# Configure git (optional, user can override)
echo "🔧 Configuring git..."
git config --global --add safe.directory /workspaces/*

# Show environment info
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Environment Ready!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Python: $(python --version)"
echo "Pip: $(pip --version | cut -d' ' -f2)"
echo "OpenAI SDK: $(pip show openai | grep Version | cut -d' ' -f2)"
echo ""

# Check for API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY not set."
    echo "   Set it in your local environment or .env file"
else
    echo "✅ OPENAI_API_KEY is set"
fi

echo ""
echo "Quick Start:"
echo "  - Run notebooks: jupyter lab --ip=0.0.0.0"
echo "  - Test structure: python tools/notebook_test_runner.py --mode structure"
echo "  - Validate metadata: python tools/notebook_metadata_validator.py"
echo "  - Generate index: python tools/generate_notebook_index.py"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
