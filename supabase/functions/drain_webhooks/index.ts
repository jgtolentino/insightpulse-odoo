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
        // TODO: Route by job.topic to actual destinations
        // For now, just simulate processing
        await new Promise((resolve) => setTimeout(resolve, 50));

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
