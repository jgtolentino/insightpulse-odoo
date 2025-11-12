// deno-lint-ignore-file no-explicit-any
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const BATCH_SIZE = 25;

interface WebhookJob {
  id: number;
  topic: string;
  payload: any;
  attempts: number;
}

/**
 * Route webhook to appropriate destination based on topic
 */
async function routeWebhook(topic: string, payload: any): Promise<void> {
  // Define routing rules based on topic patterns
  const routes: Record<string, string> = {
    // GitHub events → Odoo webhook endpoint
    "github.issue": "https://erp.insightpulseai.net/pulser_hub/github/issue",
    "github.pull_request": "https://erp.insightpulseai.net/pulser_hub/github/pr",

    // Security events → Security dashboard
    "security": "https://erp.insightpulseai.net/api/security/alert",

    // Invoice events → Accounting integrations
    "invoice": "https://erp.insightpulseai.net/api/alerts/invoice",

    // Ticket events → Notification service (Slack/Teams)
    "ticket": Deno.env.get("SLACK_WEBHOOK_URL") || "",

    // Workflow events → Notion sync
    "workflow": "https://api.notion.com/v1/pages",
  };

  // Find matching route (supports prefix matching)
  let destinationUrl = "";
  for (const [prefix, url] of Object.entries(routes)) {
    if (topic.startsWith(prefix)) {
      destinationUrl = url;
      break;
    }
  }

  // If no route found, log and skip
  if (!destinationUrl) {
    console.warn(`No route configured for topic: ${topic}`);
    return;
  }

  // Send webhook to destination
  const response = await fetch(destinationUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Webhook-Topic": topic,
      "X-Webhook-Source": "supabase-drain",
    },
    body: JSON.stringify({
      topic,
      timestamp: new Date().toISOString(),
      data: payload,
    }),
  });

  if (!response.ok) {
    throw new Error(
      `Webhook delivery failed: ${response.status} ${response.statusText}`
    );
  }
}

Deno.serve(async (_req) => {
  const supabase = createClient(supabaseUrl, supabaseKey, {
    auth: { persistSession: false },
  });

  try {
    // Fetch pending jobs
    const { data: jobs, error: fetchError } = await supabase
      .from("ops_webhook_queue")
      .select("*")
      .lte("next_run_at", new Date().toISOString())
      .eq("status", "pending")
      .order("next_run_at", { ascending: true })
      .limit(BATCH_SIZE);

    if (fetchError) throw fetchError;

    let done = 0;
    let failed = 0;

    for (const job of jobs ?? []) {
      // Mark as processing
      await supabase
        .from("ops_webhook_queue")
        .update({ status: "processing" })
        .eq("id", job.id);

      try {
        // Route webhook to destination based on topic
        await routeWebhook(job.topic, job.payload);

        // Mark as done
        await supabase
          .from("ops_webhook_queue")
          .update({
            status: "done",
            attempts: job.attempts + 1,
            error: null,
          })
          .eq("id", job.id);

        done++;
      } catch (e) {
        failed++;

        // Calculate exponential backoff (max 10 minutes)
        const delay = Math.min(
          2 ** Math.min(job.attempts + 1, 6) * 1000,
          10 * 60 * 1000
        );
        const nextRun = new Date(Date.now() + delay).toISOString();

        // Mark as pending with error and backoff
        await supabase
          .from("ops_webhook_queue")
          .update({
            status: "pending",
            attempts: job.attempts + 1,
            error: String(e),
            next_run_at: nextRun,
          })
          .eq("id", job.id);
      }
    }

    return new Response(
      JSON.stringify({
        processed: jobs?.length ?? 0,
        done,
        failed,
        ts: new Date().toISOString(),
      }),
      {
        status: 200,
        headers: { "content-type": "application/json" },
      }
    );
  } catch (e) {
    console.error("Drain webhooks error:", e);
    return new Response(
      JSON.stringify({ error: String(e) }),
      {
        status: 500,
        headers: { "content-type": "application/json" },
      }
    );
  }
});
