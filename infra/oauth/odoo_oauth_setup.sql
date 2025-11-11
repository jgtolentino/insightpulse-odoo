-- Google OAuth Provider Configuration for Odoo 18 CE
-- Purpose: Configure Google OAuth 2.0 authentication for InsightPulse AI
-- Last Updated: 2025-11-09
--
-- Prerequisites:
-- 1. Google OAuth Client ID and Secret created in GCP Console
-- 2. auth_oauth module installed in Odoo
-- 3. Replace placeholder values with actual credentials

-- Delete existing Google providers to avoid duplicates
DELETE FROM auth_oauth_provider WHERE name = 'Google';

-- Insert Google OAuth provider
-- Replace 'YOUR_GOOGLE_CLIENT_ID' and 'YOUR_GOOGLE_CLIENT_SECRET' with actual values
INSERT INTO auth_oauth_provider (
  name,
  client_id,
  auth_endpoint,
  scope,
  validation_endpoint,
  data_endpoint,
  enabled,
  css_class,
  body,
  sequence,
  create_uid,
  create_date,
  write_uid,
  write_date
) VALUES (
  'Google',
  'YOUR_GOOGLE_CLIENT_ID',  -- Replace with actual Client ID
  'https://accounts.google.com/o/oauth2/v2/auth',
  'openid email profile',
  'https://www.googleapis.com/oauth2/v1/tokeninfo',
  'https://www.googleapis.com/oauth2/v1/userinfo',
  true,
  'fa fa-google',
  'Sign in with Google',
  10,
  1,
  NOW(),
  1,
  NOW()
);

-- Configure OAuth data
-- This table stores OAuth-specific configuration like client secret
INSERT INTO auth_oauth_provider_data (
  provider_id,
  client_secret,
  create_uid,
  create_date,
  write_uid,
  write_date
) VALUES (
  (SELECT id FROM auth_oauth_provider WHERE name = 'Google' LIMIT 1),
  'YOUR_GOOGLE_CLIENT_SECRET',  -- Replace with actual Client Secret
  1,
  NOW(),
  1,
  NOW()
);

-- Verification query (run after setup)
-- SELECT
--   p.name AS provider,
--   p.enabled,
--   p.client_id,
--   p.auth_endpoint,
--   p.scope
-- FROM auth_oauth_provider p
-- WHERE p.name = 'Google';

-- Expected output:
--  provider | enabled |           client_id            |                  auth_endpoint                   |          scope
-- ----------+---------+--------------------------------+-------------------------------------------------+---------------------------
--  Google   | t       | YOUR_GOOGLE_CLIENT_ID          | https://accounts.google.com/o/oauth2/v2/auth    | openid email profile
