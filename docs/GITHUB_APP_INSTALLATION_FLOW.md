# GitHub App Installation Flow - Linear Style

This document describes the clean GitHub App installation flow that matches Linear's approach: direct redirect to GitHub without custom permission toggles.

## Architecture Overview

```
User clicks "Install GitHub App"
    ↓
Frontend calls /github-app-install/start
    ↓
302 Redirect to github.com/apps/pulser-hub/installations/select_target
    ↓
GitHub shows installation UI (account selection, permissions, sudo mode)
    ↓
GitHub redirects to callback with installation_id
    ↓
Backend calls /github-app-install/callback
    ↓
Exchange installation_id for installation access token (via JWT)
    ↓
Store installation_id in Supabase (NOT the token)
    ↓
Return success to frontend
    ↓
User sees success message
```

## Components

### 1. Supabase Edge Functions

#### `github-app-install/index.ts`
- **Endpoint**: `/github-app-install/start`
  - Generates state nonce for CSRF protection
  - Returns GitHub App installation URL
  - Frontend redirects user to GitHub

- **Endpoint**: `/github-app-install/callback`
  - Receives `installation_id` from GitHub
  - Validates state parameter (CSRF)
  - Generates JWT using App private key
  - Exchanges `installation_id` for installation access token
  - Stores installation mapping in Supabase (without token)
  - Returns success response

#### `github-mint-token/index.ts`
- **Endpoint**: `/github-mint-token?installation_id=123`
  - Mints fresh installation access token on demand
  - Validates installation exists in database
  - Generates JWT and calls GitHub API
  - Returns short-lived token (~1 hour expiry)
  - **Security**: Tokens are NEVER stored, only minted when needed

### 2. Database Schema

```sql
CREATE TABLE github_installations (
  id BIGSERIAL PRIMARY KEY,
  installation_id BIGINT UNIQUE NOT NULL,
  account_login TEXT,
  account_type TEXT,
  permissions JSONB DEFAULT '{}',
  repository_selection TEXT DEFAULT 'all',
  installed_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ,
  metadata JSONB DEFAULT '{}'
);
```

### 3. Frontend (Pulse Hub)

#### `config/github.ts`
- Configuration constants
- GitHub App name and ID
- API endpoint URLs
- Permission summary (for display only)

#### `components/PermissionSummary.tsx`
- Shows fixed permissions (non-toggleable)
- "Install GitHub App" button
- Calls `/start` endpoint and redirects to GitHub

#### `App.tsx`
- Handles callback from GitHub
- Validates state parameter (CSRF)
- Calls `/callback` endpoint to complete installation
- Shows success message

## Security Features

### 1. CSRF Protection
- State nonce generated on `/start`
- Stored in sessionStorage
- Validated on callback

### 2. Token Security
- Installation tokens are NEVER stored long-term
- Only `installation_id` is persisted in database
- Tokens minted on-demand with 1-hour expiry
- JWT authentication for GitHub App API calls

### 3. JWT Generation
- Generates App JWT with 10-minute expiry
- Uses RSA private key (RS256 algorithm)
- Clock skew tolerance (-60 seconds on `iat`)

## Environment Variables

### Supabase Edge Functions
```bash
GITHUB_APP_ID=2191216
GITHUB_APP_NAME=pulser-hub
GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----"
POST_INSTALL_REDIRECT_URL=https://mcp.insightpulseai.net/callback
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

### Pulse Hub Frontend
```bash
VITE_GITHUB_APP_NAME=pulser-hub
VITE_GITHUB_APP_ID=2191216
VITE_GITHUB_INSTALL_API=https://YOUR_PROJECT.supabase.co/functions/v1/github-app-install
VITE_GITHUB_MINT_TOKEN_API=https://YOUR_PROJECT.supabase.co/functions/v1/github-mint-token
```

## Deployment Steps

### 1. Set up GitHub App
```bash
# Verify app settings
gh api /apps/pulser-hub

# Expected:
# - App ID: 2191216
# - Permissions: Contents (R/W), Issues (R/W), PRs (R/W), Workflows (R/W)
# - Callback URL: https://mcp.insightpulseai.net/callback
```

### 2. Deploy Supabase Edge Functions
```bash
cd supabase

# Set secrets (run once)
supabase secrets set GITHUB_APP_ID=2191216
supabase secrets set GITHUB_APP_NAME=pulser-hub
supabase secrets set GITHUB_PRIVATE_KEY="$(cat ~/.github/apps/pulser-hub.pem)"
supabase secrets set POST_INSTALL_REDIRECT_URL=https://mcp.insightpulseai.net/callback

# Deploy functions
supabase functions deploy github-app-install
supabase functions deploy github-mint-token

# Test endpoints
curl https://YOUR_PROJECT.supabase.co/functions/v1/github-app-install/start
```

### 3. Run Database Migration
```bash
# Apply migration
supabase db push

# Or manually:
psql $POSTGRES_URL -f supabase/migrations/20251105_github_installations.sql
```

### 4. Deploy Pulse Hub Frontend
```bash
cd pulse-hub

# Set environment variables
cat > .env.local <<EOF
VITE_GITHUB_APP_NAME=pulser-hub
VITE_GITHUB_APP_ID=2191216
VITE_GITHUB_INSTALL_API=https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/github-app-install
VITE_GITHUB_MINT_TOKEN_API=https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/github-mint-token
EOF

# Build and deploy
npm run build
# Deploy dist/ to your hosting provider
```

## Usage Examples

### 1. User Installation Flow
```typescript
// Frontend: User clicks "Install GitHub App"
const response = await fetch(`${GITHUB_INSTALL_API}/start`);
const { redirect_url, state } = await response.json();

sessionStorage.setItem('github_app_state', state);
window.location.href = redirect_url; // Redirects to GitHub
```

### 2. Minting Tokens On-Demand
```typescript
// Service: Get fresh token when needed
const response = await fetch(
  `${GITHUB_MINT_TOKEN_API}?installation_id=12345678`
);
const { token, expires_at } = await response.json();

// Use token for GitHub API calls
const repos = await fetch('https://api.github.com/installation/repositories', {
  headers: {
    Authorization: `Bearer ${token}`,
    Accept: 'application/vnd.github+json',
  },
});
```

### 3. GitHub API Operations
```typescript
// Example: Create an issue
const createIssue = async (installationId: string, owner: string, repo: string) => {
  // Mint token
  const { token } = await mintToken(installationId);

  // Create issue
  const response = await fetch(
    `https://api.github.com/repos/${owner}/${repo}/issues`,
    {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: 'application/vnd.github+json',
      },
      body: JSON.stringify({
        title: 'New issue',
        body: 'Issue description',
      }),
    }
  );

  return response.json();
};
```

## Troubleshooting

### Installation fails with "Missing installation_id"
- Check that GitHub App callback URL matches your Supabase function URL
- Verify `POST_INSTALL_REDIRECT_URL` environment variable

### Token minting fails with "installation_not_found"
- Run database migration to create `github_installations` table
- Verify installation was stored during callback

### JWT generation fails
- Verify `GITHUB_PRIVATE_KEY` is properly escaped (`\n` for newlines)
- Check that private key matches the GitHub App
- Ensure App ID is correct

### CSRF validation fails
- Check that state parameter is being stored in sessionStorage
- Verify state is included in callback URL from GitHub
- Ensure state validation logic is correct

## Comparison: OAuth vs GitHub App

| Feature | OAuth (Old) | GitHub App (New) |
|---------|------------|------------------|
| **Permissions** | Runtime selection | Fixed in app settings |
| **Token lifetime** | No expiry | 1 hour (minted on demand) |
| **Granularity** | Broad scopes | Fine-grained permissions |
| **User experience** | Custom UI → GitHub | Direct to GitHub (Linear-style) |
| **Security** | Token stored long-term | Token minted on demand |
| **CSRF protection** | Manual state validation | Built-in state validation |

## References

- [GitHub Apps Documentation](https://docs.github.com/en/apps)
- [GitHub App Installation Flow](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/authenticating-as-a-github-app-installation)
- [Linear's GitHub Integration](https://linear.app/settings/integrations/github)

---

**Last Updated**: 2025-11-05
