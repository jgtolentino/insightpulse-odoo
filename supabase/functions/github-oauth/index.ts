// GitHub OAuth Edge Function
// Handles: /github/oauth/start and /github/oauth/callback

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

serve(async (req) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }

  try {
    const url = new URL(req.url);
    const path = url.pathname;

    // OAuth Start: Generate authorization URL
    if (path.endsWith('/start')) {
      return handleOAuthStart(url);
    }

    // OAuth Callback: Exchange code for access token
    if (path.endsWith('/callback')) {
      return await handleOAuthCallback(url);
    }

    return new Response(
      JSON.stringify({ error: 'Invalid endpoint' }),
      { status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );

  } catch (error) {
    console.error('Error:', error);
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});

function handleOAuthStart(url: URL): Response {
  const GITHUB_CLIENT_ID = Deno.env.get('GITHUB_CLIENT_ID');
  const redirectUri = url.searchParams.get('redirect_uri') || 'https://mcp.insightpulseai.net/callback';
  const scopes = url.searchParams.get('scopes') || 'repo,user,read:org';

  if (!GITHUB_CLIENT_ID) {
    return new Response(
      JSON.stringify({ error: 'GITHUB_CLIENT_ID not configured' }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }

  // Generate random 32-character state nonce for CSRF protection
  const state = Array.from(crypto.getRandomValues(new Uint8Array(16)))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('');

  const authUrl = new URL('https://github.com/login/oauth/authorize');
  authUrl.searchParams.set('client_id', GITHUB_CLIENT_ID);
  authUrl.searchParams.set('redirect_uri', redirectUri);
  authUrl.searchParams.set('scope', scopes);
  authUrl.searchParams.set('state', state);

  return new Response(
    JSON.stringify({
      authorization_url: authUrl.toString(),
      state: state
    }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  );
}

async function handleOAuthCallback(url: URL): Promise<Response> {
  const code = url.searchParams.get('code');
  const state = url.searchParams.get('state');
  const error = url.searchParams.get('error');
  const errorDescription = url.searchParams.get('error_description');

  // Handle OAuth errors
  if (error) {
    console.error('OAuth error:', error, errorDescription);
    return new Response(
      JSON.stringify({ error, error_description: errorDescription }),
      { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }

  // Validate code parameter
  if (!code || typeof code !== 'string') {
    return new Response(
      JSON.stringify({ error: 'no_code', error_description: 'No authorization code received' }),
      { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }

  const GITHUB_CLIENT_ID = Deno.env.get('GITHUB_CLIENT_ID');
  const GITHUB_CLIENT_SECRET = Deno.env.get('GITHUB_CLIENT_SECRET');

  if (!GITHUB_CLIENT_ID || !GITHUB_CLIENT_SECRET) {
    return new Response(
      JSON.stringify({ error: 'config_error', error_description: 'OAuth credentials not configured' }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }

  console.log('Exchanging OAuth code for access token');

  // Exchange code for access token
  const tokenResponse = await fetch('https://github.com/login/oauth/access_token', {
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      client_id: GITHUB_CLIENT_ID,
      client_secret: GITHUB_CLIENT_SECRET,
      code: code,
      ...(state && { state }),
    }),
  });

  if (!tokenResponse.ok) {
    const errorText = await tokenResponse.text();
    console.error('Token exchange failed:', errorText);
    return new Response(
      JSON.stringify({ error: 'token_exchange_failed', error_description: 'Failed to exchange code for token' }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }

  const tokenData = await tokenResponse.json();

  if (tokenData.error) {
    console.error('Token exchange error:', tokenData.error_description);
    return new Response(
      JSON.stringify({ error: tokenData.error, error_description: tokenData.error_description || 'Token exchange failed' }),
      { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }

  const accessToken = tokenData.access_token;

  if (!accessToken) {
    return new Response(
      JSON.stringify({ error: 'no_token', error_description: 'No access token received' }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }

  console.log('OAuth token exchange successful');

  // Optionally store token in Supabase (requires SUPABASE_SERVICE_ROLE_KEY)
  // const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
  // const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
  // const supabase = createClient(supabaseUrl, supabaseKey);
  // await supabase.from('github_tokens').insert({ access_token: accessToken, ... });

  return new Response(
    JSON.stringify({
      access_token: accessToken,
      token_type: tokenData.token_type || 'bearer',
      scope: tokenData.scope || ''
    }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  );
}
