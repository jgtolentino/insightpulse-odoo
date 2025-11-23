// Supabase Edge Function: closing-snapshot
// Purpose: Store Odoo monthly closing snapshots from n8n W101 workflow
// Triggered by: n8n cron (11 PM PHT daily)
// Target table: finance_closing_snapshots

import { serve } from "https://deno.land/std@0.224.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

// CORS headers for preflight requests
const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

serve(async (req: Request) => {
  // Handle CORS preflight requests
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  // Only accept POST requests
  if (req.method !== "POST") {
    return new Response(
      JSON.stringify({ error: "Method not allowed", allowed: ["POST"] }),
      {
        status: 405,
        headers: { ...corsHeaders, "Content-Type": "application/json" }
      }
    );
  }

  try {
    // Initialize Supabase client with service role key
    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    // Parse request body
    const body = await req.json().catch(() => ({}));
    console.log("Received payload:", JSON.stringify(body, null, 2));

    // Extract required fields
    const {
      source = "n8n",
      odoo_db,
      period_label,
      total_tasks,
      open_tasks,
      blocked_tasks,
      done_tasks,
      cluster_a_open = 0,
      cluster_b_open = 0,
      cluster_c_open = 0,
      cluster_d_open = 0,
    } = body;

    // Validate required fields
    if (!odoo_db || !period_label) {
      return new Response(
        JSON.stringify({
          error: "Missing required fields",
          required: ["odoo_db", "period_label"],
          received: Object.keys(body)
        }),
        {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" }
        }
      );
    }

    // Validate numeric fields
    const numericFields = {
      total_tasks,
      open_tasks,
      blocked_tasks,
      done_tasks,
      cluster_a_open,
      cluster_b_open,
      cluster_c_open,
      cluster_d_open,
    };

    for (const [key, value] of Object.entries(numericFields)) {
      if (value !== undefined && (typeof value !== "number" || isNaN(value))) {
        return new Response(
          JSON.stringify({
            error: `Invalid numeric field: ${key}`,
            value,
            expected: "number"
          }),
          {
            status: 400,
            headers: { ...corsHeaders, "Content-Type": "application/json" }
          }
        );
      }
    }

    // Insert snapshot into database
    const { data, error } = await supabase
      .from("finance_closing_snapshots")
      .insert({
        source,
        odoo_db,
        period_label,
        total_tasks: total_tasks ?? 0,
        open_tasks: open_tasks ?? 0,
        blocked_tasks: blocked_tasks ?? 0,
        done_tasks: done_tasks ?? 0,
        cluster_a_open,
        cluster_b_open,
        cluster_c_open,
        cluster_d_open,
        raw_payload: body,
      })
      .select();

    if (error) {
      console.error("Database insert error:", error);
      return new Response(
        JSON.stringify({
          error: "Database error",
          message: error.message,
          details: error.details,
          hint: error.hint
        }),
        {
          status: 500,
          headers: { ...corsHeaders, "Content-Type": "application/json" }
        }
      );
    }

    console.log("Snapshot inserted successfully:", data);

    // Return success response
    return new Response(
      JSON.stringify({
        status: "ok",
        message: "Closing snapshot saved successfully",
        snapshot_id: data?.[0]?.id,
        captured_at: data?.[0]?.captured_at,
        period_label,
        total_tasks: total_tasks ?? 0,
        open_tasks: open_tasks ?? 0,
        blocked_tasks: blocked_tasks ?? 0,
        done_tasks: done_tasks ?? 0
      }),
      {
        status: 200,
        headers: { ...corsHeaders, "Content-Type": "application/json" }
      }
    );

  } catch (e) {
    console.error("Function error:", e);
    return new Response(
      JSON.stringify({
        error: "Internal server error",
        message: e instanceof Error ? e.message : "Unknown error"
      }),
      {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" }
      }
    );
  }
});
