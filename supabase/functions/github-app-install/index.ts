// GitHub App Installation Edge Function
// Handles: /github-app-install/start and /github-app-install/callback
// Implements Linear-style direct GitHub App installation flow

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

    // Installation Start: Redirect to GitHub App installation page
    if (path.endsWith('/start') || path.endsWith('/install')) {
      return handleInstallStart();
    }

    // Installation Callback: Exchange installation_id for access token
    if (path.endsWith('/callback')) {
      return await handleInstallCallback(url);
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

/**
 * Redirect to GitHub App installation page
 * Linear-style: No custom UI, direct 302 to GitHub
 */
function handleInstallStart(): Response {
  const GITHUB_APP_NAME = Deno.env.get('GITHUB_APP_NAME') || 'pulser-hub';
  const POST_INSTALL_REDIRECT_URL = Deno.env.get('POST_INSTALL_REDIRECT_URL') || 'https://mcp.insightpulseai.net/callback';

  // Generate random state nonce for CSRF protection
  const state = Array.from(crypto.getRandomValues(new Uint8Array(16)))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('');

  // Build GitHub App installation URL
  const installUrl = new URL(`https://github.com/apps/${GITHUB_APP_NAME}/installations/select_target`);
  installUrl.searchParams.set('state', state);

  // Return redirect instruction (frontend will handle the 302)
  return new Response(
    JSON.stringify({
      redirect_url: installUrl.toString(),
      state: state
    }),
    {
      status: 200,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    }
  );
}

/**
 * Handle callback from GitHub after installation
 * Exchange installation_id for installation access token
 */
async function handleInstallCallback(url: URL): Promise<Response> {
  const installationId = url.searchParams.get('installation_id');
  const setupAction = url.searchParams.get('setup_action');
  const state = url.searchParams.get('state');

  if (!installationId) {
    return new Response(
      JSON.stringify({
        error: 'missing_installation_id',
        error_description: 'No installation_id received from GitHub'
      }),
      { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }

  // Validate environment variables
  const GITHUB_APP_ID = Deno.env.get('GITHUB_APP_ID');
  const GITHUB_PRIVATE_KEY = Deno.env.get('GITHUB_PRIVATE_KEY');

  if (!GITHUB_APP_ID || !GITHUB_PRIVATE_KEY) {
    return new Response(
      JSON.stringify({
        error: 'config_error',
        error_description: 'GitHub App credentials not configured'
      }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }

  console.log(`Processing installation callback for installation_id: ${installationId}`);

  try {
    // Generate JWT for GitHub App authentication
    const jwt = await generateJWT(GITHUB_APP_ID, GITHUB_PRIVATE_KEY);

    // Exchange installation_id for installation access token
    const tokenResponse = await fetch(
      `https://api.github.com/app/installations/${installationId}/access_tokens`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${jwt}`,
          'Accept': 'application/vnd.github+json',
          'X-GitHub-Api-Version': '2022-11-28',
        },
      }
    );

    if (!tokenResponse.ok) {
      const errorText = await tokenResponse.text();
      console.error('Token exchange failed:', errorText);
      return new Response(
        JSON.stringify({
          error: 'token_exchange_failed',
          error_description: 'Failed to exchange installation_id for token'
        }),
        { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    const tokenData = await tokenResponse.json();

    // Store installation mapping in Supabase
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    await supabase
      .from('github_installations')
      .upsert({
        installation_id: Number(installationId),
        account_login: tokenData.account?.login || null,
        account_type: tokenData.account?.type || null,
        permissions: tokenData.permissions || {},
        repository_selection: tokenData.repository_selection || 'all',
        installed_at: new Date().toISOString(),
        expires_at: tokenData.expires_at || null,
      }, {
        onConflict: 'installation_id'
      });

    console.log('Installation mapping stored successfully');

    // Return success (DO NOT store the token long-term - mint on demand)
    return new Response(
      JSON.stringify({
        success: true,
        installation_id: installationId,
        account: tokenData.account?.login,
        message: 'GitHub App installed successfully. Tokens will be minted on demand.'
      }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );

  } catch (error) {
    console.error('Installation callback error:', error);
    return new Response(
      JSON.stringify({
        error: 'callback_error',
        error_description: error.message
      }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
}

/**
 * Generate JWT for GitHub App authentication
 * JWT expires in 10 minutes (GitHub requirement)
 */
async function generateJWT(appId: string, privateKey: string): Promise<string> {
  // Normalize PEM format (replace escaped newlines)
  const pem = privateKey.replace(/\\n/g, '\n');

  // JWT claims
  const now = Math.floor(Date.now() / 1000);
  const payload = {
    iat: now - 60, // issued 60 seconds in the past (clock skew)
    exp: now + 600, // expires in 10 minutes
    iss: appId,
  };

  // Import private key for signing
  const keyData = pem.replace(/-----BEGIN RSA PRIVATE KEY-----/, '')
    .replace(/-----END RSA PRIVATE KEY-----/, '')
    .replace(/\s/g, '');

  const binaryKey = Uint8Array.from(atob(keyData), c => c.charCodeAt(0));

  const cryptoKey = await crypto.subtle.importKey(
    'pkcs8',
    binaryKey.buffer,
    {
      name: 'RSASSA-PKCS1-v1_5',
      hash: 'SHA-256',
    },
    false,
    ['sign']
  );

  // Create JWT header
  const header = {
    alg: 'RS256',
    typ: 'JWT',
  };

  // Encode header and payload
  const encodedHeader = base64UrlEncode(JSON.stringify(header));
  const encodedPayload = base64UrlEncode(JSON.stringify(payload));

  // Sign with private key
  const data = new TextEncoder().encode(`${encodedHeader}.${encodedPayload}`);
  const signature = await crypto.subtle.sign(
    'RSASSA-PKCS1-v1_5',
    cryptoKey,
    data
  );

  const encodedSignature = base64UrlEncode(signature);

  return `${encodedHeader}.${encodedPayload}.${encodedSignature}`;
}

/**
 * Base64 URL encode (RFC 4648)
 */
function base64UrlEncode(data: string | ArrayBuffer): string {
  let base64: string;

  if (typeof data === 'string') {
    base64 = btoa(data);
  } else {
    const bytes = new Uint8Array(data);
    base64 = btoa(String.fromCharCode(...bytes));
  }

  return base64
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=/g, '');
}
