-- Supabase Magic Link Authentication Setup
-- Purpose: Configure passwordless email authentication alongside Google OAuth
-- Project: spdtwktxdalcfigzeqrz (InsightPulse AI)
-- Last Updated: 2025-11-09
--
-- Prerequisites:
-- 1. Supabase project with Auth enabled
-- 2. SMTP configured in Supabase (Settings → Auth → SMTP Settings)
-- 3. Email templates configured

-- Enable magic link in Supabase Auth settings
-- This is done via Supabase Dashboard, not SQL:
-- 1. Go to Authentication → Providers → Email
-- 2. Enable "Enable Magic Link"
-- 3. Configure SMTP settings (Settings → Auth → SMTP Settings)

-- Create auth.users table extension for Odoo integration
-- This syncs Supabase Auth users with Odoo res.users table

CREATE TABLE IF NOT EXISTS public.auth_sync (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  supabase_user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
  odoo_user_id integer,
  email text NOT NULL,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  UNIQUE(supabase_user_id),
  UNIQUE(odoo_user_id)
);

-- Create index for fast lookups
CREATE INDEX IF NOT EXISTS idx_auth_sync_supabase_user ON public.auth_sync(supabase_user_id);
CREATE INDEX IF NOT EXISTS idx_auth_sync_odoo_user ON public.auth_sync(odoo_user_id);
CREATE INDEX IF NOT EXISTS idx_auth_sync_email ON public.auth_sync(email);

-- Enable Row Level Security
ALTER TABLE public.auth_sync ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only see their own sync record
CREATE POLICY "Users can view own auth sync" ON public.auth_sync
  FOR SELECT
  USING (auth.uid() = supabase_user_id);

-- RLS Policy: Service role can manage all records
CREATE POLICY "Service role can manage auth sync" ON public.auth_sync
  FOR ALL
  USING (auth.role() = 'service_role');

-- Function: Sync Supabase user to Odoo on magic link login
CREATE OR REPLACE FUNCTION public.sync_supabase_to_odoo()
RETURNS TRIGGER AS $$
DECLARE
  v_odoo_user_id integer;
BEGIN
  -- Check if user already synced
  SELECT odoo_user_id INTO v_odoo_user_id
  FROM public.auth_sync
  WHERE supabase_user_id = NEW.id;

  IF v_odoo_user_id IS NULL THEN
    -- Create Odoo user via RPC (requires Odoo RPC endpoint)
    -- This is a placeholder; actual implementation depends on Odoo RPC setup

    -- For now, just create sync record with NULL odoo_user_id
    -- Manual sync will happen on first Odoo login
    INSERT INTO public.auth_sync (supabase_user_id, email, odoo_user_id)
    VALUES (NEW.id, NEW.email, NULL)
    ON CONFLICT (supabase_user_id) DO NOTHING;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger: Sync user on magic link confirmation
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.sync_supabase_to_odoo();

-- Function: Get or create Odoo user from Supabase Auth
CREATE OR REPLACE FUNCTION public.get_odoo_user_for_supabase_user(p_supabase_user_id uuid)
RETURNS TABLE (
  odoo_user_id integer,
  email text,
  sync_status text
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    s.odoo_user_id,
    s.email,
    CASE
      WHEN s.odoo_user_id IS NULL THEN 'pending_sync'
      ELSE 'synced'
    END AS sync_status
  FROM public.auth_sync s
  WHERE s.supabase_user_id = p_supabase_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permissions
GRANT EXECUTE ON FUNCTION public.get_odoo_user_for_supabase_user(uuid) TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_odoo_user_for_supabase_user(uuid) TO service_role;

-- Email templates (configure in Supabase Dashboard → Auth → Email Templates)
-- Magic Link template example:
/*
Subject: Sign in to InsightPulse AI

<h2>Magic Link Login</h2>
<p>Click the link below to sign in to InsightPulse AI:</p>
<p><a href="{{ .ConfirmationURL }}">Sign in to InsightPulse AI</a></p>
<p>This link expires in 1 hour.</p>
<p>If you didn't request this, please ignore this email.</p>
*/

-- Verification query: Check magic link configuration
-- Run this after setup in Supabase Dashboard
/*
SELECT
  id,
  email,
  confirmed_at,
  email_confirmed_at,
  created_at
FROM auth.users
ORDER BY created_at DESC
LIMIT 10;

-- Check sync records
SELECT
  s.id,
  s.email,
  s.supabase_user_id,
  s.odoo_user_id,
  CASE
    WHEN s.odoo_user_id IS NULL THEN 'Pending Odoo sync'
    ELSE 'Synced with Odoo'
  END AS status,
  s.created_at
FROM public.auth_sync s
ORDER BY s.created_at DESC
LIMIT 10;
*/
