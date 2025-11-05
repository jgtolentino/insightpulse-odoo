# InsightPulse Expense MVP - Installation & Usage Guide

## Overview

The **InsightPulse Expense MVP** is a drop-in Odoo add-on that provides a Concur-style Travel & Expense (T&E) management system with:

- **Travel Requests** - Request approval for business travel
- **Cash Advances** - Request and track cash advances with liquidation
- **Expense Management** - Extend Odoo's `hr.expense` with OCR-powered receipt parsing
- **Mobile Receipt Capture** - PWA-friendly mobile interface for instant receipt capture
- **Admin Dashboard** - Real-time KPIs for T&E operations
- **Liquidation Tracking** - Track cash advance vs actual expenses

---

## Features

### 1. Mobile Receipt Capture
- **Route**: `/ip/mobile/receipt`
- **Camera Integration**: Uses `capture="environment"` to open phone camera directly
- **Instant OCR**: Automatically parses receipt on upload
- **PWA-Ready**: Add to Home Screen for native app feel

### 2. OCR Integration
- **Sync Mode**: Manual "Run OCR" button on expense form
- **Async Mode**: Optional webhook callback at `/ip/ocr/callback`
- **Fields Extracted**:
  - Total amount
  - Receipt date
  - Merchant name
  - Confidence scores
- **Wire-up**: Connects to your OCR inference service via System Parameters

### 3. Travel & Expense Workflow
```
Travel Request → Approval → Cash Advance → Release →
  Expenses (with OCR) → Liquidation → Balance Calculation
```

### 4. Admin Dashboard
**Menu**: `InsightPulse T&E → Admin Dashboard`

**KPIs**:
- Pending Approvals (expenses in submitted/reported state)
- Open Cash Advances (approved/released)
- Overdue Liquidations (draft/submitted)
- OCR Queue (new/queued expenses)

### 5. Security Groups
- **Employee**: Submit travel requests, cash advances, expenses
- **Approver**: Approve travel requests and cash advances
- **Finance**: Validate liquidations and journal entries

---

## Installation

### Prerequisites
- Odoo 19.x CE
- PostgreSQL 15+
- Docker & Docker Compose (recommended)
- Python 3.11+ (if running directly)

### Step 1: Deploy to Repository

The addon is already in your repo at `custom_addons/ip_expense_mvp/`. The following configurations have been applied:

**Docker Compose Changes**:
- `docker-compose.yml`: Added volume mount `./custom_addons:/mnt/custom-addons:ro`
- `docker-compose.prod.yml`: Added volume mount `./custom_addons:/mnt/custom-addons:ro`

**Odoo Configuration Changes**:
- `config/odoo/odoo.conf`: Added `/mnt/custom-addons` to `addons_path` (first position)
- `services/odoo/odoo.conf`: Added `/mnt/custom-addons` to `addons_path` (first position)

### Step 2: Restart Odoo

**Local Development**:
```bash
docker-compose down && docker-compose up -d
```

**Production**:
```bash
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

### Step 3: Install the Module

1. Navigate to **Settings → Apps → Update Apps List**
2. Search for **InsightPulse – Expense MVP (Mobile + Dashboard)**
3. Click **Install**

### Step 4: Configure OCR Endpoint

Navigate to **Settings → Technical → System Parameters** and add:

| Key | Value | Description |
|-----|-------|-------------|
| `ip_ai_inference_base_url` | `http://188.166.237.231:8100` | Your OCR inference service base URL |
| `ip_ai_inference_token` | `<optional>` | Bearer token if your OCR service requires authentication |

**Example**:
- Base URL: `http://mcp.insightpulseai.net`
- Token: Leave empty if no auth required

---

## Usage

### Mobile Receipt Capture

#### Setup PWA (Recommended)
1. Open `/ip/mobile/receipt` in Safari (iOS) or Chrome (Android)
2. Tap **Share → Add to Home Screen**
3. Icon appears on home screen with app name "InsightPulse T&E"

#### Capture Receipt
1. Tap **Receipt Image** → Opens camera
2. Take photo of receipt
3. (Optional) Enter title and amount
4. Tap **Upload & Parse**
5. OCR runs automatically
6. Redirects to expense form with parsed data

### Desktop Expense Entry

1. Navigate to **Expenses → My Expenses → Create**
2. Attach receipt image
3. Click **OCR** tab
4. Click **Run OCR** button
5. Parsed fields auto-fill:
   - `ocr_merchant` → Name field (if empty)
   - `total_amount` → Amount field
   - `ocr_date` → Receipt date
   - `ocr_confidence` → Confidence score

### Cash Advance Flow

#### Request Cash Advance
1. **Menu**: `InsightPulse T&E → Cash Advances → Create`
2. Fill fields:
   - Employee
   - Amount
   - Purpose
   - State: Draft
3. Submit for approval

#### Approve Cash Advance (Approver Role)
1. Open cash advance
2. Change state to **Approved**
3. Change state to **Released** when cash is disbursed

#### Liquidate Cash Advance
1. Create expenses linked to the cash advance (set `cash_advance_id` field)
2. **Menu**: `InsightPulse T&E → Liquidations → Create`
3. Select cash advance
4. Enter total spent
5. System calculates balance:
   - **Refund**: Total spent < Cash advance
   - **Collect**: Total spent > Cash advance

### Travel Request Flow

1. **Menu**: `InsightPulse T&E → Travel Requests → Create`
2. Fill fields:
   - Name
   - Employee
   - Destination
   - Date start/end
   - **No Car Service**: Check if employee doesn't need transport
   - State: Draft
3. Submit for approval
4. Approver changes state to **Approved**

### Admin Dashboard

**Menu**: `InsightPulse T&E → Admin Dashboard`

**Use Cases**:
- **Finance Manager**: Monitor pending approvals before month-end close
- **Approver**: Track backlog of travel requests and cash advances
- **Operations**: Monitor OCR queue for bottlenecks
- **Audit**: Track overdue liquidations for compliance

---

## OCR Integration Details

### Sync Mode (Default)

**Endpoint**: `POST {base_url}/v1/ocr/receipt-parse`

**Request**:
```bash
curl -X POST \
  http://188.166.237.231:8100/v1/ocr/receipt-parse \
  -H "Authorization: Bearer <token>" \
  -F "file=@receipt.jpg" \
  -F "external_id=hr.expense:123"
```

**Response Schema**:
```json
{
  "total_amount": {"value": 123.45, "confidence": 0.98},
  "date": {"value": "2025-11-05", "confidence": 0.95},
  "merchant_name": {"value": "Grab", "confidence": 0.92},
  "currency": {"value": "PHP", "confidence": 0.99}
}
```

### Async Mode (Optional)

**Use Case**: Long-running OCR (e.g., multi-page invoices, poor image quality)

**Webhook Endpoint**: `POST /ip/ocr/callback`

**Your OCR service should**:
1. Accept initial parse request
2. Return job ID immediately
3. Process async
4. Call back to webhook when done

**Callback Payload**:
```json
{
  "external_id": "hr.expense:123",
  "result": {
    "total_amount": {"value": 123.45, "confidence": 0.98},
    "date": {"value": "2025-11-05"},
    "merchant_name": {"value": "Grab"}
  }
}
```

**Odoo will**:
- Look up expense by `external_id`
- Apply OCR fields via `_apply_ocr_payload()`
- Update `ocr_status` to `parsed`

---

## Customization

### Add Per-Diem Categories

```python
# In Odoo shell or init script
Category = self.env['product.category'].create({
    'name': 'Per-Diem',
})

Product = self.env['product.product'].create({
    'name': 'Meal Allowance',
    'categ_id': Category.id,
    'list_price': 500.0,  # PHP 500/day
    'can_be_expensed': True,
})
```

### Wire Approval Policies

```python
# In custom_addons/ip_expense_mvp/models/cash_advance.py

def action_submit(self):
    if self.amount > 10000:
        # Send to Finance Manager
        approver = self.env.ref('hr.group_hr_manager')
    else:
        # Send to Department Manager
        approver = self.employee_id.parent_id.user_id
    self._send_approval_notification(approver)
```

### Add GL Account Links

```python
# Link expense categories to GL accounts
# Requires account_expense module or similar

ExpenseCategory = self.env['hr.expense.category']
Category = ExpenseCategory.create({
    'name': 'Transportation',
    'account_id': self.env.ref('account.account_expense_travel').id,
})
```

---

## Troubleshooting

### Module Not Appearing in Apps List

**Solution**:
1. Check `custom_addons/ip_expense_mvp/__manifest__.py` exists
2. Verify volume mount in `docker-compose.yml`:
   ```yaml
   volumes:
     - ./custom_addons:/mnt/custom-addons:ro
   ```
3. Check `addons_path` in Odoo config:
   ```ini
   addons_path = /mnt/custom-addons,...
   ```
4. Restart Odoo: `docker-compose restart odoo`
5. Update Apps List: **Settings → Apps → Update Apps List**

### OCR Button Not Working

**Error**: `System Parameter 'ip_ai_inference_base_url' is not set`

**Solution**:
1. **Settings → Technical → System Parameters → Create**
2. Key: `ip_ai_inference_base_url`
3. Value: `http://188.166.237.231:8100`

**Error**: `Attach a receipt image first before OCR`

**Solution**:
1. Ensure expense has at least one attachment with `mimetype` like `image/%`
2. Supported formats: JPG, PNG, PDF (if OCR service supports)

**Error**: `OCR endpoint returned 401 Unauthorized`

**Solution**:
1. Add `ip_ai_inference_token` System Parameter
2. Value: Your bearer token
3. OCR service will receive header: `Authorization: Bearer <token>`

### Mobile Capture Not Working

**Error**: Camera doesn't open on mobile

**Solution**:
1. Ensure HTTPS is enabled (camera API requires secure context)
2. For local testing, use `localhost` or `127.0.0.1` (exempt from HTTPS requirement)
3. Check browser permissions: Allow camera access

**Error**: Upload fails silently

**Solution**:
1. Check Odoo logs: `docker-compose logs -f odoo`
2. Look for errors in `/var/log/odoo/odoo.log`
3. Verify `ir.attachment` creation permissions

---

## Architecture

### File Structure

```
custom_addons/ip_expense_mvp/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   └── ocr.py              # /ip/mobile/receipt, /ip/ocr/callback
├── models/
│   ├── __init__.py
│   ├── expense_ocr.py      # Extends hr.expense with OCR
│   ├── cash_advance.py     # ip.cash.advance model
│   ├── travel_request.py   # ip.travel.request model
│   ├── liquidation.py      # ip.liquidation model
│   └── te_dashboard.py     # ip.te.dashboard (KPIs)
├── views/
│   ├── menu.xml            # Top-level menu structure
│   ├── expense_views.xml   # Expense form extensions + new model views
│   ├── templates.xml       # Mobile receipt capture HTML
│   └── admin_dashboard.xml # Dashboard KPI view
├── security/
│   └── ir.model.access.csv # Access rights
└── README.md
```

### Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│ Mobile/Desktop                                              │
│ ┌─────────────┐         ┌──────────────┐                   │
│ │ /ip/mobile  │────────▶│ hr.expense   │                   │
│ │ /receipt    │         │ (with image) │                   │
│ └─────────────┘         └──────┬───────┘                   │
│                                 │                            │
│                                 ▼                            │
│                         ┌──────────────┐                    │
│                         │ OCR Button   │                    │
│                         │ (action_run_ │                    │
│                         │  ocr)        │                    │
│                         └──────┬───────┘                    │
└────────────────────────────────┼───────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────┐
│ OCR Service (External)                                      │
│ POST {base_url}/v1/ocr/receipt-parse                        │
│ ┌──────────────────────────────────────┐                   │
│ │ PaddleOCR / Tesseract / Claude AI    │                   │
│ │ - Extract text                        │                   │
│ │ - Parse fields (amount, date, vendor)│                   │
│ │ - Return JSON                         │                   │
│ └──────────────┬───────────────────────┘                   │
└────────────────┼───────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ Odoo (Expense Model)                                        │
│ ┌──────────────────────────────────────┐                   │
│ │ _apply_ocr_payload()                 │                   │
│ │ - Map JSON → expense fields          │                   │
│ │ - Update ocr_status = "parsed"       │                   │
│ │ - Set ocr_confidence, ocr_merchant   │                   │
│ └──────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

### Database Schema

**New Tables**:
- `ip_cash_advance`: Cash advance requests
- `ip_travel_request`: Travel requests
- `ip_liquidation`: Liquidation records
- `ip_te_dashboard`: Transient model for KPIs (no persistence)

**Extended Tables**:
- `hr_expense`:
  - `ocr_status`: Selection (new, queued, parsed, error)
  - `ocr_confidence`: Float
  - `ocr_merchant`: Char
  - `ocr_date`: Date
  - `ocr_payload`: JSON
  - `ocr_job_id`: Char (for async tracking)
  - `cash_advance_id`: Many2one to `ip.cash.advance`

---

## Next Steps

### Phase 2 Enhancements (Future)

1. **Native Mobile App**
   - Expo wrapper around `/ip/mobile/receipt`
   - Offline mode with sync
   - Push notifications for approvals

2. **Advanced Liquidation**
   - Auto-match expenses to cash advances
   - Multi-currency support
   - GL journal entry automation

3. **BIR Compliance**
   - ATP validation on receipts
   - VAT computation
   - 1601-C / 2550Q integration

4. **Analytics**
   - Superset dashboards
   - Spending by category/employee/department
   - OCR accuracy tracking

5. **AI Features**
   - Duplicate receipt detection
   - Policy violation detection
   - Merchant categorization

---

## Support & Contributing

**Issues**: Report bugs at [github.com/jgtolentino/insightpulse-odoo/issues](https://github.com/jgtolentino/insightpulse-odoo/issues)

**Pull Requests**: Contributions welcome!

**License**: LGPL-3

**Author**: InsightPulseAI

**Version**: 0.1.0

---

## Changelog

### v0.1.0 (2025-11-05)
- Initial release
- Mobile receipt capture
- OCR integration (sync mode)
- Cash advance workflow
- Travel request workflow
- Liquidation tracking
- Admin dashboard with KPIs
- Security groups (Employee, Approver, Finance)
