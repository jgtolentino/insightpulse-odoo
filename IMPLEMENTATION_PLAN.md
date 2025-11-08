# InsightPulse Expense Management - Implementation Roadmap

**Created**: 2025-11-08
**Status**: In Progress
**Phases**: 3 (Today → Option C → Option A+B)

---

## 🎯 Implementation Phases

### **Phase 1: TODAY - Infrastructure Fix** ⚡ (30 minutes)

**Goal**: Make custom modules visible in Odoo Apps

**Tasks**:
- [x] Create odoo.conf with addons_path
- [x] Update docker-compose.yml to mount config
- [x] Create deployment script (fix-odoo-apps.sh)
- [ ] Deploy to production (165.227.10.178)
- [ ] Verify custom modules appear in Apps UI

**Commands**:
```bash
cd /home/user/insightpulse-odoo
./scripts/fix-odoo-apps.sh
```

**Success Criteria**:
- ✅ Custom modules visible at: https://erp.insightpulseai.net/web#action=base.open_module_tree
- ✅ Can install: ip_expense_mvp, pulser_webhook, ipai_mattermost_bridge

---

### **Phase 2: TODAY - Payment Methods (Option C)** 💰 (1-2 hours)

**Goal**: Configure Philippine payment methods in existing Odoo

**Tasks**:
- [x] Create payment methods configuration script
- [ ] Set up Philippine Chart of Accounts
- [ ] Configure Company vs Employee payment methods
- [ ] Create expense journals (EMPEX, COMPEX)
- [ ] Set up bank accounts (BPI/BDO/Metrobank)

**Chart of Accounts**:
```
1010.01 - Cash on Hand - Petty Cash
1010.02 - Company Credit Card
1020.01 - Bank - BPI
1020.02 - Bank - BDO
1020.03 - Bank - Metrobank
2010.01 - Expenses Payable
5010.01 - Travel & Transportation
5010.02 - Representation Expense
5010.03 - Communication Expense
5010.04 - Meals & Entertainment
5010.05 - Fuel & Oil
```

**Payment Methods**:

*Company-Paid (Non-reimbursable)*:
- Bank Transfer (BPI/BDO/Metrobank)
- Company Credit Card
- Company Debit Card
- Check Payment
- E-Wallet (GCash/PayMaya)

*Employee-Paid (Reimbursable)*:
- Cash Advance
- Employee Credit Card
- Employee Cash
- Reimbursement via Payroll

**Commands**:
```bash
./scripts/configure-payment-methods.sh
```

**Success Criteria**:
- ✅ Payment methods dropdown in expense form
- ✅ Two journals: EMPEX (employee), COMPEX (company)
- ✅ Philippine COA visible in Accounting
- ✅ Can create expense with payment method

---

### **Phase 3A: NEXT - Enhance ip_expense_mvp (Option B)** 🔧 (4-8 hours)

**Goal**: Add BIR compliance and enhanced features to existing MVP

**Enhancements**:

**1. BIR Compliance Module**:
```python
# custom_addons/ip_expense_mvp/models/bir_validation.py
class BIRExpenseValidation(models.Model):
    _inherit = 'hr.expense'

    # TIN validation (XXX-XXX-XXX-XXX)
    bir_tin = fields.Char("TIN", size=15)
    bir_or_number = fields.Char("Official Receipt No.")
    bir_vat_amount = fields.Float("VAT Amount (12%)")
    bir_compliant = fields.Boolean(compute='_compute_bir_compliant')
```

**2. Payment Methods Integration**:
```python
payment_method = fields.Selection([
    ('bank_transfer', 'Bank Transfer'),
    ('company_card', 'Company Credit Card'),
    ('employee_card', 'Employee Credit Card'),
    ('cash', 'Cash'),
    ('gcash', 'GCash'),
], string="Payment Method")

expense_type = fields.Selection([
    ('employee', 'Employee-Paid (Reimbursable)'),
    ('company', 'Company-Paid (Non-reimbursable)'),
], default='employee')
```

**3. Enhanced OCR**:
- TIN extraction from receipts
- OR number recognition
- VAT calculation validation
- Merchant verification

**Files to Modify**:
```
custom_addons/ip_expense_mvp/
├── models/
│   ├── bir_validation.py (NEW)
│   ├── expense_ocr.py (ENHANCE)
│   └── payment_methods.py (NEW)
├── views/
│   └── expense_views.xml (UPDATE - add BIR fields)
└── __manifest__.py (UPDATE version to 0.2.0)
```

**Success Criteria**:
- ✅ BIR TIN validation on save
- ✅ VAT auto-calculation (12%)
- ✅ Payment method dropdown works
- ✅ Company vs Employee expense routing
- ✅ OR number required for expenses > ₱1,000

---

### **Phase 3B: LATER - Full Solution (Option A)** ⚙️ (8-16 hours)

**Goal**: Complete BIR-compliant expense management system

**New Module**: `insightpulse_expense_ocr`

**Features**:

**1. Self-Hosted PaddleOCR Integration**:
```python
# Integrate with https://ocr.insightpulseai.net
- Receipt parsing with 95%+ accuracy
- BIR form recognition (1601-C, 2550Q)
- Confidence scoring
- Manual review queue for low-confidence
```

**2. Multi-Level Approval Workflows**:
```
Employee → Team Lead → Finance Manager → CFO
Thresholds:
- < ₱5,000: Auto-approve
- ₱5,000 - ₱20,000: Team Lead
- ₱20,000 - ₱50,000: Finance Manager
- > ₱50,000: CFO
```

**3. Email-to-Expense**:
```
Email: expenses@insightpulseai.net
- Auto-extract attachments
- Run OCR
- Create draft expense
- Notify employee
```

**4. BIR Forms Automation**:
```python
- Generate 1601-C (Withholding Tax)
- Generate 2550Q (Quarterly VAT)
- Export to BIR EFPS format
- Audit trail for compliance
```

**5. Analytics Dashboard**:
```
- Expense trends by category
- Top spenders
- Compliance rate
- Approval bottlenecks
- Cost center allocation
```

**Module Structure**:
```
custom_addons/insightpulse_expense_ocr/
├── __manifest__.py
├── models/
│   ├── expense_bir.py (BIR compliance)
│   ├── expense_approval.py (workflow)
│   ├── expense_ocr.py (PaddleOCR integration)
│   ├── payment_method.py (payment routing)
│   └── bir_forms.py (form generation)
├── views/
│   ├── expense_views.xml
│   ├── approval_views.xml
│   ├── dashboard.xml
│   └── bir_forms_views.xml
├── wizard/
│   ├── expense_import.py
│   └── bir_export.py
├── data/
│   ├── approval_workflow.xml
│   └── email_templates.xml
└── controllers/
    ├── email_ingestion.py
    └── mobile_api.py
```

**Docker Services**:
```yaml
# Add to docker-compose.yml
services:
  paddleocr:
    image: paddlepaddle/paddleocr:latest-gpu
    ports:
      - "8866:8866"
    environment:
      - USE_GPU=true
    volumes:
      - ./paddleocr/models:/models
```

**Success Criteria**:
- ✅ 95%+ OCR accuracy on Philippine receipts
- ✅ BIR 1601-C export working
- ✅ Email-to-expense processing
- ✅ Multi-level approval enforced
- ✅ Dashboard showing KPIs
- ✅ Mobile PWA at /ip/mobile/receipt

---

## 📊 Cost Savings Breakdown

| Component | Enterprise Cost | InsightPulse Cost | Annual Savings |
|-----------|----------------|-------------------|----------------|
| Odoo License (12 users) | $4,728 | $0 | $4,728 |
| OCR/Digitization | $348 | $0 (self-hosted) | $348 |
| Expense Cards (Stripe) | $600 | $0 (bank integration) | $600 |
| Hosting | Included | $240 (DO droplet) | - |
| **Total** | **$5,676** | **$240** | **$5,436 (95.8%)** |

---

## 🗓️ Timeline

| Phase | Duration | Start | End | Status |
|-------|----------|-------|-----|--------|
| Phase 1: Fix Apps | 30 mins | Today | Today | 🟢 Ready |
| Phase 2: Payment Methods | 2 hours | Today | Today | 🟢 Ready |
| Phase 3A: Enhance MVP | 4-8 hours | Next | +1 week | 🟡 Planned |
| Phase 3B: Full Solution | 8-16 hours | Next | +2 weeks | 🟡 Planned |

---

## 🚀 Deployment Checklist

### Phase 1 (TODAY)
```bash
[ ] 1. Deploy Odoo config fix
       cd /home/user/insightpulse-odoo
       ./scripts/fix-odoo-apps.sh

[ ] 2. Verify modules visible
       https://erp.insightpulseai.net/web#action=base.open_module_tree

[ ] 3. Install custom modules
       - Install ip_expense_mvp
       - Install pulser_webhook
       - Install ipai_mattermost_bridge

[ ] 4. Verify installation
       Menu → InsightPulse T&E (should appear)
```

### Phase 2 (TODAY)
```bash
[ ] 1. Configure payment methods
       ./scripts/configure-payment-methods.sh

[ ] 2. Verify COA
       Accounting → Configuration → Chart of Accounts
       (Should see 1010.01, 1020.01, etc.)

[ ] 3. Verify journals
       Accounting → Configuration → Journals
       (Should see EMPEX, COMPEX)

[ ] 4. Test expense creation
       HR → Expenses → New
       (Payment method dropdown should work)
```

### Phase 3A (NEXT WEEK)
```bash
[ ] 1. Enhance ip_expense_mvp
       - Add BIR validation models
       - Update views with BIR fields
       - Integrate payment methods
       - Update version to 0.2.0

[ ] 2. Deploy to production
       git commit && git push
       ssh root@165.227.10.178
       cd /opt/insightpulse-odoo
       git pull && docker-compose restart odoo

[ ] 3. Test BIR validation
       - Create expense with TIN
       - Verify VAT calculation
       - Check OR number requirement
```

### Phase 3B (LATER)
```bash
[ ] 1. Create insightpulse_expense_ocr module
[ ] 2. Integrate PaddleOCR service
[ ] 3. Set up email ingestion
[ ] 4. Configure approval workflows
[ ] 5. Deploy BIR forms generator
[ ] 6. Build analytics dashboard
[ ] 7. Full integration testing
[ ] 8. Production deployment
```

---

## 🔧 Technical Notes

### OAuth Configuration

**Google OAuth Client ID**: `813089342312-sgk0lv3chvdcsaqb5o5hj2jv2jco1gai.apps.googleusercontent.com`

**Usage**: (Please clarify - where should this be integrated?)
- [ ] Landing page SSO?
- [ ] Odoo Google Sign-In?
- [ ] Mobile PWA authentication?
- [ ] Other?

### Environment Variables

Add to `.env`:
```bash
# Phase 3B additions
PADDLE_OCR_URL=http://localhost:8866
BIR_EFPS_API_KEY=your_efps_key_here
EXPENSE_EMAIL=expenses@insightpulseai.net
GOOGLE_OAUTH_CLIENT_ID=813089342312-sgk0lv3chvdcsaqb5o5hj2jv2jco1gai.apps.googleusercontent.com
```

### Database Schema Changes

**Phase 2 (Option C)**:
- Chart of Accounts entries
- Journal entries
- System parameters for payment methods

**Phase 3A (Option B)**:
- BIR fields on hr.expense
- Payment method selection
- Expense type (employee/company)

**Phase 3B (Option A)**:
- Approval workflow tables
- OCR confidence scores
- BIR forms archive
- Email ingestion logs

---

## 📞 Support & Documentation

**Primary Contact**: jake@insightpulseai.net
**GitHub**: https://github.com/jgtolentino/insightpulse-odoo
**Documentation**: See FIX_ODOO_APPS.md for current phase

**Key URLs**:
- Odoo ERP: https://erp.insightpulseai.net
- OCR Service: https://ocr.insightpulseai.net
- Mattermost: https://chat.insightpulseai.net
- n8n: https://n8n.insightpulseai.net

---

## ✅ Next Immediate Action

**Run these commands NOW**:

```bash
cd /home/user/insightpulse-odoo

# Phase 1: Fix Odoo apps
./scripts/fix-odoo-apps.sh

# Wait for Odoo to restart (~2 minutes)

# Phase 2: Configure payment methods
./scripts/configure-payment-methods.sh
```

**After completion**, you'll have:
✅ Custom modules visible in Odoo
✅ Payment methods configured
✅ Philippine Chart of Accounts
✅ Ready for expense tracking with payment method selection

**Then proceed to Phase 3A/3B** as planned.
