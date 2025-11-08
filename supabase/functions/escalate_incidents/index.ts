// deno-lint-ignore-file no-explicit-any
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const slackWebhook = Deno.env.get("SLACK_WEBHOOK_URL")!;

Deno.serve(async (_req) => {
  const supabase = createClient(supabaseUrl, supabaseKey, {
    auth: { persistSession: false },
  });

  try {
    // Fetch open incidents
    const { data: incidents, error } = await supabase
      .from("ops_incidents")
      .select("*")
      .eq("status", "open")
      .order("created_at", { ascending: false })
      .limit(10);

    if (error) throw error;

    if (!incidents || incidents.length === 0) {
      return new Response(
        JSON.stringify({ notified: 0, message: "No open incidents" }),
        {
          status: 200,
          headers: { "content-type": "application/json" },
        }
      );
    }

    // Send to Slack
    let notified = 0;
    for (const inc of incidents) {
      const payload = {
        text: `🚨 ${inc.sev} Incident: ${inc.title}`,
        blocks: [
          {
            type: "section",
            text: {
              type: "mrkdwn",
              text: `*${inc.sev}*: ${inc.title}\n\`\`\`${JSON.stringify(inc.details, null, 2)}\`\`\``,
            },
          },
          {
            type: "context",
            elements: [
              {
                type: "mrkdwn",
                text: `ID: ${inc.id} | Created: ${inc.created_at}`,
              },
            ],
          },
        ],
      };

      const response = await fetch(slackWebhook, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        notified++;

        // Mark as acknowledged
        await supabase
          .from("ops_incidents")
          .update({ status: "ack", acknowledged_at: new Date().toISOString() })
          .eq("id", inc.id);
      }
    }

    return new Response(
      JSON.stringify({ notified, total: incidents.length }),
      {
        status: 200,
        headers: { "content-type": "application/json" },
      }
    );
  } catch (e) {
    console.error("Escalate incidents error:", e);
    return new Response(
      JSON.stringify({ error: String(e) }),
      {
        status: 500,
        headers: { "content-type": "application/json" },
      }
    );
  }
});
