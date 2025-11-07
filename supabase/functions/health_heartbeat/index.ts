// deno-lint-ignore-file no-explicit-any
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

Deno.serve(async (req) => {
  try {
    const { source = "edge", status = "ok", meta = {} } = await req.json().catch(() => ({}));

    const supabase = createClient(supabaseUrl, supabaseKey, {
      auth: { persistSession: false },
    });

    const { error } = await supabase
      .from("ops_heartbeats")
      .insert([{ source, status, meta }]);

    if (error) throw error;

    return new Response(
      JSON.stringify({ ok: true, ts: new Date().toISOString() }),
      {
        status: 200,
        headers: { "content-type": "application/json" },
      }
    );
  } catch (e) {
    console.error("Heartbeat error:", e);
    return new Response(
      JSON.stringify({ ok: false, error: String(e) }),
      {
        status: 500,
        headers: { "content-type": "application/json" },
      }
    );
  }
});
