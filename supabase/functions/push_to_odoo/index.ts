// Deno Edge Function: Supabase → Odoo Action Push
// Endpoint: POST /functions/v1/push_to_odoo
// Purpose: Apply actions in Odoo via signed HTTP calls to custom controllers

import { crypto } from "https://deno.land/std@0.224.0/crypto/mod.ts";

const ODOO_BASE_URL = Deno.env.get("ODOO_BASE_URL")!;
const ODOO_API_TOKEN = Deno.env.get("ODOO_API_TOKEN")!;
const EDGE_HMAC_SECRET = Deno.env.get("EDGE_HMAC_SECRET")!;

/**
 * Generate HMAC-SHA256 signature for payload
 */
async function hmac(content: string, secret: string): Promise<string> {
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const sig = await crypto.subtle.sign(
    "HMAC",
    key,
    new TextEncoder().encode(content)
  );
  return Array.from(new Uint8Array(sig))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

Deno.serve(async (req) => {
  // CORS headers
  const corsHeaders = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "authorization, content-type",
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
    // Parse request body
    const body = await req.json();

    // Validate required fields
    if (!body.action) {
      return new Response("Missing action", {
        status: 400,
        headers: { ...corsHeaders, "content-type": "text/plain" }
      });
    }

    const payload = JSON.stringify(body);

    // Sign payload with HMAC
    const sig = await hmac(payload, EDGE_HMAC_SECRET);

    // Forward to Odoo custom controller
    const odooUrl = `${ODOO_BASE_URL}/api/agent/apply`;
    console.log(`Calling Odoo: ${odooUrl} with action: ${body.action}`);

    const res = await fetch(odooUrl, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-api-key": ODOO_API_TOKEN,
        "x-signature": sig,
      },
      body: payload,
    });

    const text = await res.text();

    // Log response
    console.log(`Odoo response (${res.status}): ${text.substring(0, 200)}`);

    // Return Odoo's response
    return new Response(text, {
      status: res.status,
      headers: { ...corsHeaders, "content-type": "application/json" }
    });
  } catch (error) {
    console.error("Unexpected error:", error);
    return new Response(`Internal Server Error: ${error.message}`, {
      status: 500,
      headers: { ...corsHeaders, "content-type": "text/plain" }
    });
  }
});
