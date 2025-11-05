-- GitHub App Installations Table
-- Stores installation_id mapping for GitHub Apps (not the tokens)
-- Tokens are minted on demand for security

CREATE TABLE IF NOT EXISTS github_installations (
  id BIGSERIAL PRIMARY KEY,
  installation_id BIGINT UNIQUE NOT NULL,
  account_login TEXT,
  account_type TEXT, -- 'User' or 'Organization'
  permissions JSONB DEFAULT '{}',
  repository_selection TEXT DEFAULT 'all', -- 'all' or 'selected'
  installed_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ, -- if applicable
  metadata JSONB DEFAULT '{}'
);

-- Index for quick lookups
CREATE INDEX IF NOT EXISTS idx_github_installations_installation_id
  ON github_installations(installation_id);

CREATE INDEX IF NOT EXISTS idx_github_installations_account_login
  ON github_installations(account_login);

-- Update timestamp automatically
CREATE OR REPLACE FUNCTION update_github_installations_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER github_installations_updated_at
  BEFORE UPDATE ON github_installations
  FOR EACH ROW
  EXECUTE FUNCTION update_github_installations_updated_at();

-- Add comment
COMMENT ON TABLE github_installations IS 'GitHub App installation mappings. Tokens are NOT stored here - they are minted on demand for security.';
