// GitHub App Token Minting Service
// Mints short-lived installation access tokens on demand
// NEVER stores tokens - only installation_id is persisted

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
    const installationId = url.searchParams.get('installation_id');

    if (!installationId) {
      return new Response(
        JSON.stringify({
          error: 'missing_installation_id',
          error_description: 'installation_id parameter is required'
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

    // Verify installation exists in database
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    const { data: installation, error: dbError } = await supabase
      .from('github_installations')
      .select('*')
      .eq('installation_id', Number(installationId))
      .single();

    if (dbError || !installation) {
      return new Response(
        JSON.stringify({
          error: 'installation_not_found',
          error_description: 'Installation not found in database. Please install the app first.'
        }),
        { status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    console.log(`Minting token for installation_id: ${installationId}`);

    // Generate JWT for GitHub App authentication
    const jwt = await generateJWT(GITHUB_APP_ID, GITHUB_PRIVATE_KEY);

    // Mint installation access token
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
      console.error('Token minting failed:', errorText);
      return new Response(
        JSON.stringify({
          error: 'token_mint_failed',
          error_description: 'Failed to mint installation access token'
        }),
        { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    const tokenData = await tokenResponse.json();

    console.log('Token minted successfully');

    // Return token (expires in ~1 hour by default)
    return new Response(
      JSON.stringify({
        token: tokenData.token,
        expires_at: tokenData.expires_at,
        permissions: tokenData.permissions,
        repository_selection: tokenData.repository_selection,
      }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );

  } catch (error) {
    console.error('Token minting error:', error);
    return new Response(
      JSON.stringify({
        error: 'mint_error',
        error_description: error.message
      }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});

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
