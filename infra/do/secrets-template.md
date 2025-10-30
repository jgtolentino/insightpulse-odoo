# GitHub Secrets Configuration

Add these secrets to your GitHub repository settings at:
`https://github.com/[your-org]/insightpulse-odoo/settings/secrets/actions`

## DigitalOcean Secrets

### DO_ACCESS_TOKEN
**Description**: DigitalOcean API token for App Platform deployments

**How to get**:
1. Go to https://cloud.digitalocean.com/account/api/tokens
2. Click "Generate New Token"
3. Name: `insightpulse-odoo-ci`
4. Scopes: Read and Write
5. Copy the token (you won't be able to see it again)

**Value**: `dop_v1_...` (your DigitalOcean API token)

---

### DO_APP_ID
**Description**: DigitalOcean App Platform app ID

**How to get**:
1. Create the app first using `doctl` or DigitalOcean Console
2. Get the app ID from the app URL or run:
   ```bash
   doctl apps list --format ID,Spec.Name
   ```

**Value**: `b1bb1b07-46a6-4bbb-85a2-e1e8c7f263b9` (example format)

---

## Supabase Database Secrets

### POSTGRES_HOST
**Description**: Supabase connection pooler host

**Format**: `aws-1-us-east-1.pooler.supabase.com`

**Value**: Your Supabase pooler hostname (found in Supabase project settings)

---

### POSTGRES_USER
**Description**: Database user

**Value**: `postgres` (default) or your custom database user

---

### POSTGRES_PASSWORD
**Description**: Database password

**Value**: Your Supabase database password (found in Supabase project settings)

---

## Odoo Secrets

### ODOO_ADMIN_PASSWORD
**Description**: Odoo master password for admin operations

**How to generate**:
```bash
# Generate a secure random password
openssl rand -base64 32
```

**Value**: A strong, randomly generated password

---

## Optional Secrets (for AI features)

### OPENAI_API_KEY
**Description**: OpenAI API key for AI-powered features (optional - use self-hosted Llama 3.2 instead for cost savings)

**Value**: `sk-...` (only if not using self-hosted AI)

**Note**: Not required for budget optimization. Use self-hosted Ollama with Llama 3.2 instead.

---

## Environment Variable Configuration

These secrets are automatically injected into the DigitalOcean App Platform environment by the `infra/do/odoo-saas-platform.yaml` spec.

### Verification

After adding secrets to GitHub, verify they're configured:

```bash
# List GitHub secrets (names only, not values)
gh secret list

# Test DigitalOcean access
doctl auth init --access-token "$DO_ACCESS_TOKEN"
doctl apps list

# Test app access
doctl apps get "$DO_APP_ID"
```

---

## Security Best Practices

1. **Never commit secrets to git**
2. **Rotate tokens regularly** (quarterly recommended)
3. **Use separate tokens** for different environments (dev/staging/prod)
4. **Limit token scopes** to minimum required permissions
5. **Enable 2FA** on DigitalOcean and GitHub accounts
6. **Monitor token usage** in DigitalOcean audit logs

---

## Troubleshooting

### "Secret not found" error
- Verify secret name matches exactly (case-sensitive)
- Check secret is added to the correct repository
- Ensure secret is available to the workflow (not environment-specific)

### "Invalid token" error
- Verify token hasn't expired
- Check token has correct permissions (read/write)
- Regenerate token if compromised

### "App not found" error
- Verify `DO_APP_ID` is correct
- Check token has access to the app
- Ensure app exists in DigitalOcean console
