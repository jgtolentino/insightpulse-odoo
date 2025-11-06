// Supabase Edge Function: notify-odoo
// Mints a signed URL for the uploaded receipt and notifies Odoo to pull it
// Triggered after successful file upload to Supabase Storage

import { serve } from "https://deno.land/std@0.224.0/http/server.ts";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const ODOO_BASE_URL = Deno.env.get("ODOO_BASE_URL") || "https://insightpulseai.net";
const ODOO_API_TOKEN = Deno.env.get("ODOO_API_TOKEN")!;

interface NotifyRequest {
  file_path: string;
  user_id: string;
  file_name: string;
  mime_type: string;
  file_size: number;
}

serve(async (req) => {
  try {
    // Parse request body
    const { file_path, user_id, file_name, mime_type, file_size }: NotifyRequest = await req.json();

    console.log(`[notify-odoo] Processing upload: ${file_name} by user ${user_id}`);

    // Step 1: Mint signed URL (15-minute TTL)
    const signRes = await fetch(
      `${SUPABASE_URL}/storage/v1/object/sign/receipts/${file_path}`,
      {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ expiresIn: 900 }), // 15 minutes
      }
    );

    if (!signRes.ok) {
      const errorText = await signRes.text();
      throw new Error(`Failed to sign URL: ${signRes.status} ${errorText}`);
    }

    const { signedURL } = await signRes.json();
    console.log(`[notify-odoo] Signed URL created (15-min TTL)`);

    // Step 2: Insert receipt metadata into Supabase
    const insertRes = await fetch(`${SUPABASE_URL}/rest/v1/receipts`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
        "Content-Type": "application/json",
        "Prefer": "return=representation",
      },
      body: JSON.stringify({
        user_id,
        file_path,
        file_name,
        mime_type,
        file_size,
        status: "processing",
      }),
    });

    if (!insertRes.ok) {
      const errorText = await insertRes.text();
      throw new Error(`Failed to insert receipt: ${insertRes.status} ${errorText}`);
    }

    const receipt = await insertRes.json();
    console.log(`[notify-odoo] Receipt metadata saved: ${receipt[0].id}`);

    // Step 3: Notify Odoo to pull the file
    const odooRes = await fetch(`${ODOO_BASE_URL}/api/v1/receipts/pull`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${ODOO_API_TOKEN}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        file_url: signedURL,
        user_id,
        receipt_id: receipt[0].id,
        file_name,
        mime_type,
        file_size,
      }),
    });

    if (!odooRes.ok) {
      const errorText = await odooRes.text();
      console.error(`[notify-odoo] Odoo notification failed: ${odooRes.status} ${errorText}`);

      // Update receipt status to failed
      await fetch(`${SUPABASE_URL}/rest/v1/receipts?id=eq.${receipt[0].id}`, {
        method: "PATCH",
        headers: {
          "Authorization": `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          status: "failed",
          error_message: `Odoo notification failed: ${odooRes.status} ${errorText}`,
        }),
      });

      throw new Error(`Odoo notification failed: ${odooRes.status} ${errorText}`);
    }

    const odooResult = await odooRes.json();
    console.log(`[notify-odoo] Odoo notified successfully. Expense ID: ${odooResult.expense_id}`);

    // Step 4: Update receipt status to completed
    await fetch(`${SUPABASE_URL}/rest/v1/receipts?id=eq.${receipt[0].id}`, {
      method: "PATCH",
      headers: {
        "Authorization": `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        status: "completed",
        odoo_expense_id: odooResult.expense_id,
      }),
    });

    console.log(`[notify-odoo] Workflow complete!`);

    return new Response(
      JSON.stringify({
        success: true,
        receipt_id: receipt[0].id,
        odoo_expense_id: odooResult.expense_id,
        signed_url_expires_in: "15 minutes",
      }),
      {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }
    );
  } catch (error) {
    console.error("[notify-odoo] Error:", error);
    return new Response(
      JSON.stringify({
        success: false,
        error: error.message,
      }),
      {
        status: 500,
        headers: { "Content-Type": "application/json" },
      }
    );
  }
});
