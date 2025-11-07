// deno-lint-ignore-file no-explicit-any
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const odooBaseUrl = Deno.env.get("ODOO_BASE_URL")!;
const odooApiKey = Deno.env.get("ODOO_API_KEY")!;

Deno.serve(async (req) => {
  const supabase = createClient(supabaseUrl, supabaseKey, {
    auth: { persistSession: false },
  });

  try {
    const body = await req.json().catch(() => ({}));

    // Generate idempotency key if not provided
    const idempotencyKey = body.idempotency_key ||
      crypto.randomUUID();

    // Queue the sync request
    const { error: queueError } = await supabase
      .from("ops_webhook_queue")
      .insert([{
        topic: "odoo_sync",
        payload: body,
        idempotency_key: idempotencyKey,
      }]);

    // Ignore duplicate key errors (already queued)
    if (queueError && !queueError.message.includes("duplicate key")) {
      throw queueError;
    }

    // Fan out to Odoo immediately (fire-and-record)
    try {
      const response = await fetch(`${odooBaseUrl}/api/sync`, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          "Authorization": `Bearer ${odooApiKey}`,
        },
        body: JSON.stringify(body),
      });

      return new Response(
        JSON.stringify({
          ok: response.ok,
          status: response.status,
          idempotency_key: idempotencyKey,
        }),
        {
          status: response.ok ? 200 : 502,
          headers: { "content-type": "application/json" },
        }
      );
    } catch (e) {
      // Odoo unreachable, but queued for retry
      console.error("Odoo sync failed, queued for retry:", e);
      return new Response(
        JSON.stringify({
          ok: false,
          error: "Odoo unreachable, queued for retry",
          idempotency_key: idempotencyKey,
        }),
        {
          status: 202,
          headers: { "content-type": "application/json" },
        }
      );
    }
  } catch (e) {
    console.error("Odoo sync dispatcher error:", e);
    return new Response(
      JSON.stringify({ error: String(e) }),
      {
        status: 500,
        headers: { "content-type": "application/json" },
      }
    );
  }
});
