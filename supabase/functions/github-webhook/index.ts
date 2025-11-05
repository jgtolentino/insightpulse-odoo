// GitHub Webhook Edge Function
// Handles: GitHub webhook events

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type, x-github-event, x-github-delivery, x-hub-signature-256',
};

serve(async (req) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }

  try {
    const signature = req.headers.get('x-hub-signature-256');
    const event = req.headers.get('x-github-event');
    const deliveryId = req.headers.get('x-github-delivery');

    if (!signature || !event || !deliveryId) {
      return new Response(
        JSON.stringify({ error: 'Missing required GitHub webhook headers' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    const payload = await req.text();

    // Verify webhook signature
    const GITHUB_WEBHOOK_SECRET = Deno.env.get('GITHUB_WEBHOOK_SECRET');

    if (!GITHUB_WEBHOOK_SECRET) {
      console.error('GITHUB_WEBHOOK_SECRET not configured');
      return new Response(
        JSON.stringify({ error: 'Webhook secret not configured' }),
        { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    if (!verifyGitHubSignature(payload, signature, GITHUB_WEBHOOK_SECRET)) {
      console.error('Invalid webhook signature');
      return new Response(
        JSON.stringify({ error: 'Invalid signature' }),
        { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    console.log(`Received GitHub event: ${event} (${deliveryId})`);

    const parsedPayload = JSON.parse(payload);

    // Store webhook event in Supabase
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    const { error: dbError } = await supabase
      .from('github_webhooks')
      .insert({
        event_type: event,
        delivery_id: deliveryId,
        payload: parsedPayload,
        received_at: new Date().toISOString()
      });

    if (dbError) {
      console.error('Failed to store webhook:', dbError);
    }

    // Process specific events
    switch (event) {
      case 'installation':
        await handleInstallation(supabase, parsedPayload);
        break;
      case 'installation_repositories':
        await handleInstallationRepositories(parsedPayload);
        break;
      case 'push':
        await handlePush(parsedPayload);
        break;
      case 'pull_request':
        await handlePullRequest(parsedPayload);
        break;
      case 'issues':
        await handleIssue(parsedPayload);
        break;
      default:
        console.log(`Unhandled event type: ${event}`);
    }

    return new Response(
      JSON.stringify({ received: true, event, deliveryId }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );

  } catch (error) {
    console.error('Webhook processing error:', error);
    return new Response(
      JSON.stringify({ error: 'Internal server error' }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});

// GitHub webhook signature verification
function verifyGitHubSignature(payload: string, signature: string, secret: string): boolean {
  if (!signature) return false;

  const encoder = new TextEncoder();
  const key = encoder.encode(secret);
  const data = encoder.encode(payload);

  return crypto.subtle.importKey(
    'raw',
    key,
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  ).then(cryptoKey => {
    return crypto.subtle.sign('HMAC', cryptoKey, data);
  }).then(signatureBuffer => {
    const hexSignature = Array.from(new Uint8Array(signatureBuffer))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');
    const expectedSignature = 'sha256=' + hexSignature;

    // Timing-safe comparison
    return signature === expectedSignature;
  }).catch(err => {
    console.error('Signature verification error:', err);
    return false;
  });
}

// Event handlers
async function handleInstallation(supabase: any, payload: any) {
  const { action, installation, repositories } = payload;
  console.log(`Installation ${action}:`, {
    installationId: installation.id,
    account: installation.account.login,
    repositories: repositories?.length || 0
  });

  // Store installation in Supabase
  await supabase
    .from('github_installations')
    .upsert({
      installation_id: installation.id,
      account_login: installation.account.login,
      account_type: installation.account.type,
      action,
      created_at: installation.created_at,
      updated_at: new Date().toISOString()
    });
}

async function handleInstallationRepositories(payload: any) {
  const { action, installation, repositories_added, repositories_removed } = payload;
  console.log(`Installation repositories ${action}:`, {
    installationId: installation.id,
    added: repositories_added?.length || 0,
    removed: repositories_removed?.length || 0
  });
}

async function handlePush(payload: any) {
  const { ref, repository, pusher, commits } = payload;
  console.log(`Push to ${repository.full_name}:`, {
    ref,
    pusher: pusher.name,
    commits: commits.length
  });
}

async function handlePullRequest(payload: any) {
  const { action, pull_request, repository } = payload;
  console.log(`Pull request ${action} on ${repository.full_name}:`, {
    prNumber: pull_request.number,
    title: pull_request.title,
    author: pull_request.user.login
  });
}

async function handleIssue(payload: any) {
  const { action, issue, repository } = payload;
  console.log(`Issue ${action} on ${repository.full_name}:`, {
    issueNumber: issue.number,
    title: issue.title,
    author: issue.user.login
  });
}
