# Custom Module Inventory & Status

| Module Name | Technical Name | Status | Description |
| :--- | :--- | :--- | :--- |
| **IPAI Docs** | `ipai_docs` | ✅ Installed | Knowledge base, SOPs, and document management (Notion replacement). |
| **IPAI Docs Project** | `ipai_docs_project` | ✅ Installed | Integrates Docs with Projects/Tasks (Smart buttons, Auto-follow). |
| **IPAI Cash Advance** | `ipai_cash_advance` | ✅ Installed | Cash Advance requests and liquidation workflow (replaces `x_cash_advance`). |
| **IPAI Expense** | `ipai_expense` | ✅ Installed | Core expense management enhancements (PH travel, per diems). |
| **IPAI OCR Expense** | `ipai_ocr_expense` | ❌ Uninstalled | Receipt scanning and auto-extraction. |
| **IPAI Equipment** | `ipai_equipment` | ✅ Installed | Equipment booking and asset management (Cheqroom replacement). |
| **IPAI CE Cleaner** | `ipai_ce_cleaner` | ✅ Installed | UI cleanup, branding, and Enterprise upsell removal. |
| **IPAI Finance Monthly**| `ipai_finance_monthly_closing` | ✅ Installed | Structured month-end closing and BIR filing (Verified). |
| **IPAI Finance PPM** | `ipai_finance_ppm` | ✅ Installed | Finance Project Portfolio Management (Notion Parity). 2026 Engine Active. |
| **Legacy Cash Advance** | `x_cash_advance` | ❌ Missing/Broken | Legacy Studio module. **Must be uninstalled.** |
| **Legacy Expense Policy**| `x_expense_policy` | ❌ Missing/Broken | Legacy Studio module. **Must be uninstalled.** |
| **TBWA Spectra** | `tbwa_spectra_integration` | ✅ Installed | Integration with Spectra finance system (Standardized). |

## Action Items
1.  **Uninstall Legacy Modules**: Run the provided SQL script to remove `x_cash_advance`, `x_expense_policy`, and `ipai_finance_ssc`.
2.  **Restart Odoo**: Apply changes.
3.  **Install New Modules**: Activate `ipai_docs`, `ipai_docs_project`, and `ipai_cash_advance`.
