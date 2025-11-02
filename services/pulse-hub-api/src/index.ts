import express, { Request, Response } from 'express';
import { createClient } from '@supabase/supabase-js';
import crypto from 'crypto';
import 'dotenv/config';
import { env } from './env.js';

const app = express();
const PORT = env.PORT;

// Supabase client
const supabase = createClient(
  env.SUPABASE_URL,
  env.SUPABASE_SERVICE_ROLE_KEY
);

// Middleware
app.use(express.json());

// Health check endpoint
app.get('/health', (_req: Request, res: Response) => {
  res.json({ status: 'ok', service: 'pulse-hub-api', timestamp: new Date().toISOString() });
});

// GitHub webhook signature verification
function verifyGitHubSignature(payload: string, signature: string, secret: string): boolean {
  if (!signature) return false;

  const hmac = crypto.createHmac('sha256', secret);
  const digest = 'sha256=' + hmac.update(payload).digest('hex');

  return crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(digest));
}

// Webhook endpoint
app.post('/webhook', async (req: Request, res: Response) => {
  try {
    const signature = req.headers['x-hub-signature-256'] as string;
    const event = req.headers['x-github-event'] as string;
    const deliveryId = req.headers['x-github-delivery'] as string;

    // Verify webhook secret
    const webhookSecret = env.GITHUB_WEBHOOK_SECRET;
    const payload = JSON.stringify(req.body);

    if (webhookSecret && !verifyGitHubSignature(payload, signature, webhookSecret)) {
      console.error('Invalid webhook signature');
      return res.status(401).json({ error: 'Invalid signature' });
    }

    console.log(`Received GitHub event: ${event} (${deliveryId})`);

    // Store webhook event in Supabase
    const { error } = await supabase
      .from('github_webhooks')
      .insert({
        event_type: event,
        delivery_id: deliveryId,
        payload: req.body,
        received_at: new Date().toISOString()
      });

    if (error) {
      console.error('Failed to store webhook:', error);
    }

    // Process specific events
    switch (event) {
      case 'installation':
        await handleInstallation(req.body);
        break;
      case 'installation_repositories':
        await handleInstallationRepositories(req.body);
        break;
      case 'push':
        await handlePush(req.body);
        break;
      case 'pull_request':
        await handlePullRequest(req.body);
        break;
      case 'issues':
        await handleIssue(req.body);
        break;
      default:
        console.log(`Unhandled event type: ${event}`);
    }

    res.status(200).json({ received: true, event, deliveryId });
  } catch (error) {
    console.error('Webhook processing error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Event handlers
async function handleInstallation(payload: any) {
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

// Start server
app.listen(PORT, () => {
  console.log(`🚀 pulse-hub-api running on port ${PORT}`);
  console.log(`📍 Health check: http://localhost:${PORT}/health`);
  console.log(`📍 Webhook endpoint: http://localhost:${PORT}/webhook`);
});
