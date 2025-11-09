#!/bin/bash
# Setup Missing GitHub Secrets
# Based on CI/CD Audit 2025-11-04
# Run this script to set all missing secrets for CI/CD workflows

set -e

echo "======================================"
echo "Setting Missing GitHub Secrets"
echo "======================================"
echo ""

# Critical Secrets for CI/CD
echo "📌 Setting DigitalOcean Secrets..."
gh secret set DO_APP_ID_SUPERSET --body '73af11cb-dab2-4cb1-9770-291c536531e6'
echo "✅ DO_APP_ID_SUPERSET set"

# Note: DIGITALOCEAN_ACCESS_TOKEN should be set by user with their actual token
echo "⚠️  DIGITALOCEAN_ACCESS_TOKEN - Please set manually with your actual token:"
echo "    gh secret set DIGITALOCEAN_ACCESS_TOKEN --body 'dop_v1_YOUR_TOKEN_HERE'"
echo ""

echo "📌 Setting Droplet Host Secrets..."
gh secret set ODOO_HOST --body '165.227.10.178'
echo "✅ ODOO_HOST set"

gh secret set OCR_HOST --body '188.166.237.231'
echo "✅ OCR_HOST set"

# SSH Keys and Users (requires user input)
echo ""
echo "📌 Setting SSH Secrets..."
echo "⚠️  ODOO_SSH_KEY - Please set with your SSH private key:"
echo "    gh secret set ODOO_SSH_KEY --body \"\$(cat ~/.ssh/id_rsa)\""
echo ""
echo "⚠️  OCR_SSH_KEY - Please set with your SSH private key:"
echo "    gh secret set OCR_SSH_KEY --body \"\$(cat ~/.ssh/id_rsa)\""
echo ""

gh secret set ODOO_SSH_USER --body 'root'
echo "✅ ODOO_SSH_USER set"

gh secret set OCR_SSH_USER --body 'root'
echo "✅ OCR_SSH_USER set"

# TLS/Certbot
echo ""
echo "📌 Setting TLS Secrets..."
gh secret set CERTBOT_EMAIL --body 'jgtolentino_rn@yahoo.com'
echo "✅ CERTBOT_EMAIL set"

# OpenAI API Key (requires user input)
echo ""
echo "📌 Setting API Keys..."
echo "⚠️  OPENAI_API_KEY - Please set manually with your actual API key:"
echo "    gh secret set OPENAI_API_KEY --body 'sk-YOUR_KEY_HERE'"
echo ""

# Optional: Slack/Discord Webhooks
echo "📌 Optional Notification Secrets..."
echo "💡 SLACK_WEBHOOK - Set if you want Slack notifications:"
echo "    gh secret set SLACK_WEBHOOK --body 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'"
echo ""
echo "💡 DISCORD_WEBHOOK - Set if you want Discord notifications:"
echo "    gh secret set DISCORD_WEBHOOK --body 'https://discord.com/api/webhooks/YOUR/WEBHOOK/URL'"
echo ""

echo "======================================"
echo "✅ Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Set the secrets marked with ⚠️ manually (sensitive data)"
echo "2. Run: gh workflow run superset-postgres-guard.yml"
echo "3. Monitor: gh run watch"
echo ""
