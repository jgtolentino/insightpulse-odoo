// Deno Edge Function: Odoo → Supabase Event Ingestion
// Endpoint: POST /functions/v1/odoo_event_ingest
// Purpose: Receive signed events from Odoo, verify HMAC, persist to audit_event

import { createClient } from "https://esm.sh/@supabase/supabase-js@2";
import { crypto } from "https://deno.land/std@0.224.0/crypto/mod.ts";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const EDGE_HMAC_SECRET = Deno.env.get("EDGE_HMAC_SECRET")!;

/**
 * Verify HMAC signature using timing-safe comparison
 */
function verifyHmac(raw: string, sig: string, secret: string): boolean {
  try {
    const keyData = new TextEncoder().encode(secret);
    const mac = crypto.subtle.signSync(
      "HMAC",
      crypto.subtle.importKeySync(
        "raw",
        keyData,
        { name: "HMAC", hash: "SHA-256" },
        false,
        ["sign"]
      ),
      new TextEncoder().encode(raw)
    );
    const hex = Array.from(new Uint8Array(mac))
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");

    return crypto.timingSafeEqual(
      new TextEncoder().encode(hex),
      new TextEncoder().encode(sig)
    );
  } catch (error) {
    console.error("HMAC verification error:", error);
    return false;
  }
}

Deno.serve(async (req) => {
  // CORS headers
  const corsHeaders = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "authorization, x-signature, content-type",
  };

  // Handle CORS preflight
  if (req.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders });
  }

  if (req.method !== "POST") {
    return new Response("Method Not Allowed", {
      status: 405,
      headers: { ...corsHeaders, "content-type": "text/plain" }
    });
  }

  try {
    // Get signature from header
    const signature = req.headers.get("x-signature") ?? "";
    const raw = await req.text();

    // Verify HMAC signature
    if (!verifyHmac(raw, signature, EDGE_HMAC_SECRET)) {
      console.error("Invalid signature");
      return new Response("Invalid signature", {
        status: 401,
        headers: { ...corsHeaders, "content-type": "text/plain" }
      });
    }

    // Parse body
    const body = JSON.parse(raw);

    // Validate required fields
    if (!body.event_type) {
      return new Response("Missing event_type", {
        status: 400,
        headers: { ...corsHeaders, "content-type": "text/plain" }
      });
    }

    // Create Supabase client
    const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);

    // Insert event into audit_event table
    const { error } = await supabase.from("audit_event").insert({
      source: "odoo",
      event_type: body.event_type,
      resource_id: String(body.resource_id ?? ""),
      payload: body.payload ?? {},
      correlation_id: body.correlation_id ?? undefined,
    });

    if (error) {
      console.error("Database insert error:", error);
      return new Response(error.message, {
        status: 500,
        headers: { ...corsHeaders, "content-type": "text/plain" }
      });
    }

    // Optional: enqueue follow-up actions to outbox
    // await supabase.from("odoo_action_outbox").insert({
    //   action: "follow_up_action",
    //   args: { event_id: body.event_type }
    // });

    console.log(`Event ingested: ${body.event_type} (resource: ${body.resource_id})`);

    return new Response(
      JSON.stringify({ ok: true, event_type: body.event_type }),
      { headers: { ...corsHeaders, "content-type": "application/json" } }
    );
  } catch (error) {
    console.error("Unexpected error:", error);
    return new Response(`Internal Server Error: ${error.message}`, {
      status: 500,
      headers: { ...corsHeaders, "content-type": "text/plain" }
    });
  }
});
