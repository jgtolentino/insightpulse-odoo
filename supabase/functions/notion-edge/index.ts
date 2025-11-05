// Notion Edge Function - Sync Notion pages to Supabase
// Supports multiple assignees and task-specific properties

interface NotionPayload {
  notion_page_id: string;
  title?: string;
  is_task?: boolean;
  status?: string | null;
  priority?: number | null;
  due_at?: string | null;
  assignees?: string[] | null;
  external_metadata?: Record<string, any> | null;
  updated_by?: string | null;
}

const SUPABASE_URL = Deno.env.get('SUPABASE_URL')!;
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;

if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
  console.error('Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY environment variables');
}

Deno.serve(async (req: Request) => {
  try {
    if (req.method !== 'POST') {
      return new Response(JSON.stringify({ error: 'Method not allowed' }), { 
        status: 405, 
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const contentType = req.headers.get('content-type') || '';
    let payload: NotionPayload;

    if (contentType.includes('application/json')) {
      payload = await req.json();
    } else {
      return new Response(JSON.stringify({ error: 'Unsupported content type, use application/json' }), { 
        status: 415, 
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Basic validation
    if (!payload?.notion_page_id) {
      return new Response(JSON.stringify({ error: 'Missing notion_page_id' }), { 
        status: 400, 
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Normalize values
    const notion_page_id = String(payload.notion_page_id);
    const title = payload.title ?? null;
    const is_task = Boolean(payload.is_task ?? false);
    const status = payload.status ?? null;
    const priority = (payload.priority ?? null) !== null ? Number(payload.priority) : null;
    const due_at = payload.due_at ?? null;
    const assignees = Array.isArray(payload.assignees) ? payload.assignees : null;
    const external_metadata = payload.external_metadata ?? {};
    const updated_by = payload.updated_by ?? null;

    // Call Supabase RPC endpoint to upsert
    const rpcUrl = `${SUPABASE_URL}/rest/v1/rpc/upsert_notion_page`;
    const rpcBody = {
      p_notion_page_id: notion_page_id,
      p_title: title,
      p_is_task: is_task,
      p_status: status,
      p_priority: priority,
      p_due_at: due_at,
      p_assignees: assignees,
      p_external_metadata: external_metadata,
      p_updated_by: updated_by
    };

    const rpcResp = await fetch(rpcUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'apikey': SUPABASE_SERVICE_ROLE_KEY,
        'Authorization': `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
      },
      body: JSON.stringify(rpcBody),
    });

    const rpcText = await rpcResp.text();

    if (!rpcResp.ok) {
      console.error('RPC error', rpcResp.status, rpcText);
      return new Response(JSON.stringify({ error: 'Failed to upsert page', details: rpcText }), { 
        status: 500, 
        headers: { 'Content-Type': 'application/json' }
      });
    }

    return new Response(JSON.stringify({ ok: true, notion_page_id }), { 
      status: 200, 
      headers: { 'Content-Type': 'application/json' }
    });

  } catch (err) {
    console.error('Unhandled error', err);
    return new Response(JSON.stringify({ error: 'Internal server error' }), { 
      status: 500, 
      headers: { 'Content-Type': 'application/json' }
    });
  }
});
