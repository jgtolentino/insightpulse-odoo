import { createClient } from "@supabase/supabase-js";

type Env = {
  SUPABASE_URL: string;
  SUPABASE_SERVICE_ROLE_KEY: string;

  ODOO_URL: string;
  ODOO_DB: string;
  ODOO_USERNAME: string;
  ODOO_PASSWORD: string;

  LOCK_ID?: string;
};

function env(): Env {
  const get = (k: string) => {
    const v = Deno.env.get(k);
    if (!v) throw new Error(`Missing env ${k}`);
    return v;
  };
  return {
    SUPABASE_URL: get("SUPABASE_URL"),
    SUPABASE_SERVICE_ROLE_KEY: get("SUPABASE_SERVICE_ROLE_KEY"),
    ODOO_URL: get("ODOO_URL"),
    ODOO_DB: get("ODOO_DB"),
    ODOO_USERNAME: get("ODOO_USERNAME"),
    ODOO_PASSWORD: get("ODOO_PASSWORD"),
    LOCK_ID: Deno.env.get("LOCK_ID") ?? "odoo-sync",
  };
}

async function odooJsonRpc(odooUrl: string, path: string, params: any, cookie?: string) {
  const res = await fetch(`${odooUrl}${path}`, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      ...(cookie ? { "cookie": cookie } : {}),
    },
    body: JSON.stringify({
      jsonrpc: "2.0",
      method: "call",
      params,
      id: Math.floor(Math.random() * 1e9),
    }),
  });

  const setCookie = res.headers.get("set-cookie") ?? "";
  const data = await res.json();
  if (data.error) throw new Error(`Odoo RPC error: ${JSON.stringify(data.error)}`);
  return { data: data.result, setCookie };
}

async function odooLogin(odooUrl: string, db: string, login: string, password: string) {
  const { data, setCookie } = await odooJsonRpc(odooUrl, "/web/session/authenticate", { db, login, password });
  const cookie = setCookie.split(";")[0]; // session_id=...
  if (!cookie) throw new Error("Missing Odoo session cookie");
  return { uid: data.uid as number, cookie };
}

async function odooSearchRead(
  odooUrl: string,
  cookie: string,
  model: string,
  domain: any[],
  fields: string[],
  limit: number,
  offset: number
) {
  const { data } = await odooJsonRpc(
    odooUrl,
    "/web/dataset/call_kw",
    { model, method: "search_read", args: [domain], kwargs: { fields, limit, offset, order: "id asc" } },
    cookie
  );
  return data as any[];
}

async function odooWrite(odooUrl: string, cookie: string, model: string, ids: number[], values: Record<string, any>) {
  const { data } = await odooJsonRpc(
    odooUrl,
    "/web/dataset/call_kw",
    { model, method: "write", args: [ids, values], kwargs: {} },
    cookie
  );
  return data as boolean;
}

async function odooCreate(odooUrl: string, cookie: string, model: string, values: Record<string, any>) {
  const { data } = await odooJsonRpc(
    odooUrl,
    "/web/dataset/call_kw",
    { model, method: "create", args: [values], kwargs: {} },
    cookie
  );
  return data as number;
}

function json(res: any, status = 200) {
  return new Response(JSON.stringify(res, null, 2), { status, headers: { "content-type": "application/json" } });
}

function nowIso() {
  return new Date().toISOString();
}

function addSeconds(sec: number) {
  return new Date(Date.now() + sec * 1000).toISOString();
}

// Model mapping (extend later)
function mapOdooToSbRow(model: string, rec: any) {
  if (model === "res.partner") {
    return {
      odoo_id: rec.id,
      name: rec.name ?? null,
      email: rec.email ?? null,
      phone: rec.phone ?? null,
      write_date: rec.write_date ? new Date(rec.write_date) : null,
      raw: rec,
      synced_at: nowIso(),
    };
  }
  throw new Error(`Unsupported model for odoo_to_sb: ${model}`);
}

async function applyOutboxToOdoo(odooUrl: string, cookie: string, item: any, sb: any) {
  const model = item.model as string;
  const op = item.operation as string;
  const p = item.payload ?? {};

  if (model === "res.partner" && op === "upsert") {
    const name = p.name ?? "Unnamed";
    const email = p.email ?? false;
    const phone = p.phone ?? false;

    if (p.odoo_id && Number(p.odoo_id) > 0) {
      await odooWrite(odooUrl, cookie, "res.partner", [Number(p.odoo_id)], { name, email, phone });
    } else {
      const newId = await odooCreate(odooUrl, cookie, "res.partner", { name, email, phone, is_company: true });
      await sb.from("odoo_partners").upsert(
        {
          odoo_id: newId,
          name,
          email: email === false ? null : email,
          phone: phone === false ? null : phone,
          raw: { created_via: "sb_to_odoo", ...p, id: newId },
          synced_at: nowIso(),
        },
        { onConflict: "odoo_id" }
      );
    }
    return;
  }

  throw new Error(`Unsupported outbox operation: ${model}:${op}`);
}

Deno.serve(async (req) => {
  const E = env();
  const sb = createClient(E.SUPABASE_URL, E.SUPABASE_SERVICE_ROLE_KEY);

  try {
    const url = new URL(req.url);
    const mode = url.searchParams.get("mode") ?? "both";
    const model = url.searchParams.get("model") ?? "res.partner";

    // Load config + checkpoint
    const cfgKeyPull = `odoo_to_sb:${model}`;
    const cfgKeyPush = `sb_to_odoo:${model}`;

    const cfgPull = await sb.from("ops.odoo_sync_config").select("value").eq("key", cfgKeyPull).maybeSingle();
    const cfgPush = await sb.from("ops.odoo_sync_config").select("value").eq("key", cfgKeyPush).maybeSingle();

    const pullCfg = cfgPull.data?.value ?? { domain: [], fields: ["id"], page_size: 200 };
    const pushCfg = cfgPush.data?.value ?? { max_batch: 50, max_attempts: 5, base_backoff_seconds: 10 };

    const cp = await sb.from("ops.odoo_sync_checkpoints").select("cursor").eq("key", cfgKeyPull).maybeSingle();
    const offset = Number(cp.data?.cursor?.offset ?? 0);
    const pageSize = Number(pullCfg.page_size ?? 200);

    const { cookie } = await odooLogin(E.ODOO_URL, E.ODOO_DB, E.ODOO_USERNAME, E.ODOO_PASSWORD);

    const result: Record<string, any> = { mode, model };

    // Pull (paginated)
    if (mode === "odoo_to_sb" || mode === "both") {
      const domain = pullCfg.domain ?? [];
      const fields = pullCfg.fields ?? ["id"];

      const rows = await odooSearchRead(E.ODOO_URL, cookie, model, domain, fields, pageSize, offset);
      const mapped = rows.map((r) => mapOdooToSbRow(model, r));

      // Upsert (model-specific table)
      if (model === "res.partner") {
        const up = await sb.from("odoo_partners").upsert(mapped, { onConflict: "odoo_id" });
        if (up.error) throw up.error;
      } else {
        throw new Error(`No target table mapping for model ${model}`);
      }

      // Update checkpoint
      const newOffset = rows.length < pageSize ? 0 : offset + rows.length; // loop back after finishing page run
      await sb.from("ops.odoo_sync_checkpoints")
        .upsert({ key: cfgKeyPull, cursor: { offset: newOffset }, updated_at: nowIso() }, { onConflict: "key" });

      result.odoo_to_sb = { fetched: rows.length, upserted: mapped.length, offset, next_offset: newOffset, page_size: pageSize };
    }

    // Push (outbox with backoff)
    if (mode === "sb_to_odoo" || mode === "both") {
      const maxBatch = Number(pushCfg.max_batch ?? 50);
      const maxAttempts = Number(pushCfg.max_attempts ?? 5);
      const baseBackoff = Number(pushCfg.base_backoff_seconds ?? 10);

      // Fetch candidates (queued + due)
      const { data: batch, error: batchErr } = await sb
        .from("ops.odoo_outbox")
        .select("*")
        .eq("status", "queued")
        .lte("next_run_at", nowIso())
        .order("created_at", { ascending: true })
        .limit(maxBatch);

      if (batchErr) throw batchErr;

      let processed = 0;
      let failed = 0;
      let skipped = 0;

      for (const item of batch ?? []) {
        // Lock
        const lock = await sb.from("ops.odoo_outbox")
          .update({ status: "processing", locked_at: nowIso(), locked_by: E.LOCK_ID, attempts: (item.attempts ?? 0) + 1 })
          .eq("id", item.id)
          .eq("status", "queued")
          .select("id,attempts")
          .maybeSingle();

        if (lock.error || !lock.data) { skipped++; continue; }

        try {
          await applyOutboxToOdoo(E.ODOO_URL, cookie, item, sb);
          await sb.from("ops.odoo_outbox").update({ status: "done", last_error: null }).eq("id", item.id);
          processed++;
        } catch (e) {
          const attempts = Number(lock.data.attempts ?? 1);
          const err = String(e?.message ?? e);

          if (attempts >= maxAttempts) {
            await sb.from("ops.odoo_outbox")
              .update({ status: "failed", last_error: err })
              .eq("id", item.id);
          } else {
            const backoff = baseBackoff * Math.pow(2, Math.min(attempts - 1, 6)); // cap exponent
            await sb.from("ops.odoo_outbox")
              .update({ status: "queued", last_error: err, next_run_at: addSeconds(backoff) })
              .eq("id", item.id);
          }
          failed++;
        }
      }

      result.sb_to_odoo = { scanned: (batch ?? []).length, processed, failed, skipped, max_batch: maxBatch, max_attempts: maxAttempts };
    }

    return json({ ok: true, result });
  } catch (e) {
    return json({ ok: false, error: String(e?.message ?? e) }, 500);
  }
});
