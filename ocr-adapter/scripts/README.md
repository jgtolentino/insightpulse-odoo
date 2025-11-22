# Receipt OCR Test Harness

Automated quality testing for InsightPulse OCR service.

## Purpose

Test OCR accuracy against known ground truth receipts to:
- Measure field-wise extraction accuracy (vendor, date, total, currency)
- Track performance over time (duration metrics)
- Identify weak spots (vendor-specific, receipt type-specific)
- Guide adapter normalization improvements

## Setup

### 1. Install Dependencies

```bash
pip install httpx tabulate
```

### 2. Prepare Test Data

**Directory structure:**
```
test_receipts/
├── jollibee_001.jpg
├── 711_receipt.jpg
├── max_restaurant.jpg
├── sm_supermarket.jpg
└── crumpled_receipt.jpg
```

**Ground truth CSV** (`ground_truth.csv`):
```csv
file_name,vendor,date,total,currency
jollibee_001.jpg,Jollibee,2025-11-15,345.50,PHP
711_receipt.jpg,7-Eleven,2025-11-18,89.00,PHP
max_restaurant.jpg,Max's Restaurant,2025-11-20,1250.00,PHP
sm_supermarket.jpg,SM Supermarket,2025-11-19,2345.75,PHP
crumpled_receipt.jpg,Unknown Store,2025-11-17,125.50,PHP
```

**Tips for ground truth data:**
- Use diverse receipt types (fast food, restaurant, supermarket, convenience store)
- Include edge cases (crumpled, low contrast, long itemized receipts)
- BIR-style official receipts with OR numbers
- Mix of clean and "real world" receipts

## Usage

### Basic Test Run

```bash
python test-harness.py \
  --images ./test_receipts \
  --ground-truth ground_truth.csv \
  --api-url https://ocr.insightpulseai.net/api/expense/ocr \
  --api-key 282e6543652de3e969d43293e934f6f84557ab767132bcd2fd37c76289ff703e
```

### Local Development (OCR adapter)

```bash
python test-harness.py \
  --images ./test_receipts \
  --ground-truth ground_truth.csv \
  --api-url http://localhost:8001/api/expense/ocr \
  --api-key dev-key-insecure
```

### Options

- `--images`: Directory containing receipt images (required)
- `--ground-truth`: CSV file with expected values (required)
- `--api-url`: OCR API endpoint (required)
- `--api-key`: API key for authentication (optional)
- `--timeout`: Request timeout in seconds (default: 30)

## Output

### Console Report

```
📊 OCR Test Harness Report
================================================================================

**Overall Performance:**
  Total Tests: 5
  Fully Successful: 4 (80.0%)
  Average Duration: 2534ms

**Field-wise Accuracy:**
Field           Correct    Accuracy
--------------  ---------  ----------
Vendor          4/5        80.0%
Date            5/5        100.0%
Total (exact)   4/5        80.0%
Total (±1 peso) 5/5        100.0%
Currency        5/5        100.0%

**Per-Vendor Performance:**
Vendor            Count    Correct    Accuracy
----------------  -------  ---------  ----------
Jollibee          1        1/1        100.0%
7-Eleven          1        1/1        100.0%
Max's Restaurant  1        1/1        100.0%
SM Supermarket    1        0/1        0.0%

**Failed/Partial Results (1):**
File                    Issues
----------------------  --------------------------------------------------
sm_supermarket.jpg      vendor: 'SM Store' ≠ 'SM Supermarket'; total: 2345.00 ≠ 2345.75
```

### JSON Report

Detailed results saved to `ocr_test_report.json`:

```json
{
  "summary": {
    "total_tests": 5,
    "successful": 4,
    "avg_duration_ms": 2534,
    "vendor_accuracy": 0.8,
    "date_accuracy": 1.0,
    "total_exact_accuracy": 0.8,
    "total_close_accuracy": 1.0,
    "currency_accuracy": 1.0
  },
  "per_vendor": {
    "Jollibee": {"total": 1, "correct": 1},
    "7-Eleven": {"total": 1, "correct": 1},
    "Max's Restaurant": {"total": 1, "correct": 1},
    "SM Supermarket": {"total": 1, "correct": 0}
  },
  "detailed_results": [...]
}
```

## Interpreting Results

### Success Criteria

**Fully Successful**: All 4 fields correct (vendor, date, total, currency)

**Partial Success**: Some fields correct, marked as ⚠️

**Failed**: OCR error or most fields incorrect

### Accuracy Metrics

- **Exact Match**: String/number matches exactly
- **Close Enough**: For totals, ±1 peso tolerance (handles rounding)
- **Per-Vendor**: Track accuracy by merchant to identify problem vendors

### Performance

- **Duration**: Time from request to response (ms)
- **Average Duration**: Mean across all tests
- **Target**: P95 < 30,000ms (30 seconds)

## Using Results

### Improve Adapter Normalization

Failed tests indicate where `normalize_ocr_response()` in `main.py` needs tuning:

**Example: SM Supermarket vendor extraction**
```python
# Before
if "merchant_name" in data:
    result["merchant_name"] = data["merchant_name"]

# After (add normalization)
if "merchant_name" in data:
    vendor = data["merchant_name"]
    # Handle common variants
    if "SM Store" in vendor:
        vendor = "SM Supermarket"
    result["merchant_name"] = vendor
```

### Track Quality Over Time

Run harness after each adapter improvement:

```bash
# Baseline
python test-harness.py ... > baseline_report.txt

# After improvements
python test-harness.py ... > improved_report.txt

# Compare
diff baseline_report.txt improved_report.txt
```

### Identify Edge Cases

Low accuracy for specific vendors or receipt types indicates:
- Need better OCR model training data
- Adapter normalization gaps
- Upstream OCR service limitations

**Priority order:**
1. Fix high-volume vendors first (Jollibee, 7-Eleven, etc.)
2. Then fix common receipt formats (BIR official receipts)
3. Finally address edge cases (crumpled, low contrast)

## Best Practices

1. **Start Small**: 5-10 receipts to establish baseline
2. **Diverse Set**: Mix of common vendors and edge cases
3. **Real Receipts**: Use actual PH receipts, not mock data
4. **Regular Testing**: Run after every adapter change
5. **Version Control**: Commit ground truth CSV with git
6. **Document Failures**: Note why specific receipts fail

## Next Steps

After establishing baseline quality:

1. **Add UX guardrails** in Odoo (proposed values, confidence thresholds)
2. **n8n monitoring** (daily accuracy summaries, alert on regression)
3. **Agent skill** ("Expense OCR QA bot" for low-confidence review)
4. **Iterative improvement** (PH-specific fields, line items, VAT handling)

All improvements happen in adapter `normalize_ocr_response()` - no Odoo changes needed.
