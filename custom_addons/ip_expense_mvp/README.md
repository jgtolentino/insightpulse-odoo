# InsightPulse – Expense MVP

- Mobile capture at **/ip/mobile/receipt** (PWA-friendly).
- OCR button on `hr.expense` form → calls `ip_ai_inference_base_url` `/v1/ocr/receipt-parse`.
- Admin Dashboard (KPIs) under **InsightPulse T&E** menu.
- Cash Advance, Liquidation, Travel Request scaffolds with simple views.

## System Parameters
- `ip_ai_inference_base_url` (e.g., http://188.166.237.231:8100)
- `ip_ai_inference_token` (optional Bearer)
