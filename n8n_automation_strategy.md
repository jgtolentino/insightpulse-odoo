# n8n Automation Strategy for Odoo CE

## Executive Summary
n8n is the "glue" that brings Enterprise-grade automation to Odoo CE. By leveraging Odoo's `xmlrpc` (External API) and `jsonrpc` interfaces, n8n can bypass the need for paid Odoo connectors and perform complex logic outside the monolith.

## 1. The Core Integration Pattern
The standard n8n "Odoo Node" is useful for basic CRUD, but limited for custom modules (`ipai_*`).
**The Pro Approach:** Use the **HTTP Request Node** in n8n to talk directly to Odoo's JSON-RPC endpoint (`/jsonrpc`).

### Why?
- **Custom Models:** Access `ipai.equipment.booking`, `ipai.doc`, etc. without waiting for n8n node updates.
- **Server Actions:** Trigger Odoo Server Actions (`ir.actions.server`) directly.
- **Performance:** Batch operations in Python (Server Action) and trigger them once from n8n.

## 2. High-Value Workflows

### A. AI Expense OCR Pipeline (`ipai_ocr_expense`)
**Goal:** Replace "Odoo Digitize" (paid) with n8n + OpenAI/Google Vision.
**Workflow:**
1.  **Trigger:** Email with attachment to `expenses@company.com` (IMAP Node).
2.  **Processing:**
    - Extract attachment.
    - Send to **OpenAI GPT-4o** (Vision) or **Google Cloud Vision** Node.
    - Prompt: "Extract total, date, vendor, tax from this receipt JSON."
3.  **Action:**
    - Call Odoo API: `create` record in `hr.expense`.
    - Attach original file to the record.
    - Set status to `draft` for review.

### B. Equipment Overdue Police (`ipai_equipment`)
**Goal:** Aggressive notification for unreturned gear (Cheqroom parity).
**Workflow:**
1.  **Trigger:** Webhook from Odoo (via `ir.cron` calling `requests.post()`).
    - *Note: We add a small python snippet in Odoo to ping n8n.*
2.  **Logic:**
    - n8n receives list of overdue bookings.
    - Lookup User's Slack ID or Phone Number.
3.  **Action:**
    - **Slack:** Send DM "Hey @user, return the Sony A7S3!"
    - **Twilio/WhatsApp:** Send SMS if > 24h overdue.
    - **Odoo:** Log activity "Nagged user via WhatsApp".

### C. Finance Sync (`tbwa_spectra_integration`)
**Goal:** Sync Journal Entries to legacy Spectra system.
**Workflow:**
1.  **Trigger:** Odoo Webhook on `account.move` state change to `posted`.
2.  **Transform:** Map Odoo GL accounts to Spectra Codes.
3.  **Action:**
    - POST to Spectra API (HTTP Request).
    - If success: Write `spectra_ref_id` back to Odoo.
    - If fail: Create Odoo Activity for Finance Manager "Sync Failed".

## 3. Recommended "Custom Nodes" / Tools

You don't need to write *code* nodes for n8n, you need **Composite Workflows**:

1.  **"Odoo Auth" Sub-workflow:**
    - Input: None.
    - Output: `session_id` or `uid`.
    - Handles authentication so you don't repeat it in every flow.

2.  **"Smart Alert" Sub-workflow:**
    - Input: `user_email`, `message`, `urgency`.
    - Logic: If urgency=High -> SMS; else -> Slack/Email.

## 4. Implementation Roadmap
1.  **Deploy n8n:** `docker run -d ... n8n`.
2.  **Connect Odoo:** Create credentials (API Key) in Odoo.
3.  **Build OCR Flow:** The highest ROI immediate win.
