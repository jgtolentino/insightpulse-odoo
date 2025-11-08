// deno-lint-ignore-file no-explicit-any
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const odooBaseUrl = Deno.env.get("ODOO_BASE_URL")!;
const odooApiKey = Deno.env.get("ODOO_API_KEY")!;

Deno.serve(async (_req) => {
  const supabase = createClient(supabaseUrl, supabaseKey, {
    auth: { persistSession: false },
  });

  try {
    // 1. Simulate order creation via Odoo
    const orderResponse = await fetch(`${odooBaseUrl}/synthetics/create_order`, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "Authorization": `Bearer ${odooApiKey}`,
      },
      body: JSON.stringify({
        sku: "SYNTH-TEST-001",
        qty: 1,
        timestamp: new Date().toISOString(),
      }),
    });

    if (!orderResponse.ok) {
      throw new Error(`Odoo order creation failed: ${orderResponse.status}`);
    }

    const order = await orderResponse.json();

    // 2. Record success heartbeat
    await supabase.from("ops_heartbeats").insert([{
      source: "synthetic_order_flow",
      status: "ok",
      meta: {
        order_id: order.id,
        timestamp: new Date().toISOString(),
      },
    }]);

    return new Response(
      JSON.stringify({
        ok: true,
        order_id: order.id,
        ts: new Date().toISOString(),
      }),
      {
        status: 200,
        headers: { "content-type": "application/json" },
      }
    );
  } catch (e) {
    console.error("Synthetic order flow error:", e);

    // Record failure heartbeat
    await supabase.from("ops_heartbeats").insert([{
      source: "synthetic_order_flow",
      status: "fail",
      meta: {
        error: String(e),
        timestamp: new Date().toISOString(),
      },
    }]);

    return new Response(
      JSON.stringify({ ok: false, error: String(e) }),
      {
        status: 500,
        headers: { "content-type": "application/json" },
      }
    );
  }
});
