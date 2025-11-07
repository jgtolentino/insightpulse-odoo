# Skillsmith Integration - Unified AI/ML Pipeline

Complete integration between Skillsmith error mining and your existing AI/ML infrastructure.

## 🎯 Overview

Skillsmith integrates with:

1. **Knowledge Agent** - Odoo forum scraping (1000+ solved cases)
2. **Reinforcement Learning** - Confidence scoring and outcome tracking
3. **Small LLM Training** - TRM dataset enrichment
4. **Error Catalog** - Comprehensive taxonomy auto-sync
5. **Superset Dashboards** - Unified monitoring

## 🔗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  PRODUCTION ERRORS (Live System)                            │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   v
┌─────────────────────────────────────────────────────────────┐
│  SKILLSMITH MINER (Every 6h)                                │
│  • Normalizes & fingerprints                                │
│  • Mines top patterns                                       │
│  • Generates skill candidates                               │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   v
┌─────────────────────────────────────────────────────────────┐
│  HUMAN REVIEW & APPROVAL                                    │
│  • Review PR proposals                                      │
│  • Implement autopatch scripts                              │
│  • Move to skills/ directory                                │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   v
┌─────────────────────────────────────────────────────────────┐
│  INTEGRATION PIPELINE (Daily + after mining)                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 1. FEEDBACK LOOP (feedback_loop.py)                 │   │
│  │    • Query error_signatures before/after            │   │
│  │    • Calculate impact ratio                         │   │
│  │    • Update skill confidence                        │   │
│  │    • Log history                                    │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 2. TRM DATASET SYNC (trm_sync.py)                   │   │
│  │    • Convert approved skills → training examples    │   │
│  │    • Append to datasets/trm/erp_tasks.jsonl         │   │
│  │    • Deduplicate by fingerprint                     │   │
│  │    • Tag for retrieval                              │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 3. ERROR CATALOG SYNC (sync_catalog.py)             │   │
│  │    • Fetch live error_signatures                    │   │
│  │    • Update docs/error-codes.yaml                   │   │
│  │    • Link to active guardrails                      │   │
│  │    • Calculate coverage metrics                     │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 4. RETRAIN CHECK                                    │   │
│  │    • Count recent TRM additions                     │   │
│  │    • Create GitHub issue if threshold exceeded      │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   v
┌─────────────────────────────────────────────────────────────┐
│  MODEL RETRAINING (make retrain)                            │
│  • Trains small LLM on enriched dataset                     │
│  • Includes: Skillsmith + Forum + Manual examples           │
│  • Updates prediction weights                               │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   v
┌─────────────────────────────────────────────────────────────┐
│  MONITORING (Superset Dashboard)                            │
│  • Error trends (7d vs 30d)                                 │
│  • Skill effectiveness                                      │
│  • Training dataset growth                                  │
│  • Confidence distributions                                 │
│  • Coverage metrics                                         │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Setup Database Schema

```bash
# Deploy Skillsmith schema
make skills-db-setup

# Deploy integration views
make skills-dashboard-setup
```

### 2. Run Initial Integration

```bash
# Full pipeline
make skills-integrate

# Or step by step:
make skills-feedback       # Update confidence
make skills-sync-trm       # Sync to training dataset
make skills-sync-catalog   # Update error catalog
```

### 3. Import Superset Dashboard

```bash
# Via Superset UI:
# 1. Go to Dashboards → Import
# 2. Upload: superset/dashboards/skillsmith-unified-monitoring.json
# 3. Verify datasources connected

# Or via CLI:
superset import-dashboards -p superset/dashboards/skillsmith-unified-monitoring.json
```

### 4. Enable Automated Workflows

The following workflows run automatically:

- **Mining**: Every 6 hours (`.github/workflows/skillsmith.yml`)
- **Integration**: After mining + daily at 2 AM (`.github/workflows/skillsmith-integration.yml`)

No additional configuration needed once GitHub secrets are set.

## 📊 Integration Components

### 1. Feedback Loop (`feedback_loop.py`)

**Purpose**: Auto-update skill confidence based on real outcomes

**Logic**:
```python
# Calculate impact
expected_7d = hits_30d * (7 / 30)
impact_ratio = hits_7d / expected_7d

# Update confidence
if impact_ratio < 0.3:        # 70%+ reduction
    new_confidence = confidence * 1.3   # Boost
elif impact_ratio < 0.5:      # 50%+ reduction
    new_confidence = confidence * 1.15  # Small boost
elif impact_ratio > 1.5:      # Errors increased
    new_confidence = confidence * 0.8   # Reduce
elif impact_ratio > 0.9:      # Minimal impact
    new_confidence = confidence * 0.95  # Small reduce
```

**Output**: Updated `skills/*.yaml` with confidence history

### 2. TRM Dataset Sync (`trm_sync.py`)

**Purpose**: Enrich training dataset with production-validated patterns

**Format**:
```jsonl
{
  "id": "GR-ABCD1234",
  "source": "skillsmith-production",
  "kind": "guardrail",
  "task": "prevent_keyerror_in_sale_order",
  "input": {
    "error_pattern": "KeyError.*partner_id",
    "component": "odoo.addons.sale",
    "context": "pre_execution_check"
  },
  "output": {
    "action": "block",
    "message": "Prevented: KeyError in sale.order"
  },
  "metrics": {
    "hits_7d": 10,
    "impact_score": 15.5,
    "confidence": 0.85
  },
  "fingerprint": "00000000-0000-0000-0000-abc123",
  "tags": ["guardrail", "odoo", "sale", "keyerror"]
}
```

### 3. Error Catalog Sync (`sync_catalog.py`)

**Purpose**: Maintain living documentation synced with production

**Format** (`docs/error-codes.yaml`):
```yaml
errors:
  DB-001:
    title: "KeyError in sale.order"
    description: "Missing partner_id field"
    category: "validation"
    severity: "high"
    fingerprint: "00000000-0000-0000-0000-abc123"
    live_stats:
      hits_7d: 10
      hits_30d: 25
      last_seen: "2025-11-07T12:00:00Z"
      trend: "decreasing"
    active_guardrails:
      - skill_id: "GR-ABCD1234"
        name: "KeyError in sale.order"
        kind: "guardrail"
        confidence: 0.85
    example: "KeyError: 'partner_id' in <field> access"
```

### 4. Superset Dashboard

**Charts**:

1. **Error Trend** - Line chart (7d vs 30d)
2. **Skill Effectiveness** - Bar chart by type
3. **Top Error Patterns** - Pie chart
4. **Guardrail Coverage** - Gauge
5. **Training Dataset Growth** - Big number
6. **Skill Impact Timeline** - Mixed timeseries
7. **Knowledge Source Distribution** - Sunburst
8. **Confidence Distribution** - Histogram

**Auto-refresh**: Every 5 minutes

## 🔄 Workflow Examples

### Daily Operations

```bash
# Morning: Check dashboard
open http://localhost:8088/superset/dashboard/skillsmith-unified-monitoring

# Review new proposals (if mining ran)
ls skills/proposed/
cat skills/proposed/GR-*.yaml

# Approve and integrate
mv skills/proposed/GR-ABCD1234*.yaml skills/
make skills-integrate

# If retrain recommended
make retrain
```

### Manual Integration Run

```bash
# Full pipeline
make skills-integrate

# Output:
# [1/5] Enriching proposals with forum knowledge...
# [2/5] Updating confidence scores from outcomes...
#   ✓ Updated 15 skills (10 boosted, 5 reduced)
# [3/5] Syncing approved skills to training dataset...
#   ✓ Added 8 new training examples
# [4/5] Updating error catalog with live data...
#   ✓ Updated 20 entries, added 3 new
# [5/5] Checking if retraining needed...
#   ⚠️  Model retraining recommended (12 additions)
```

### Specific Component

```bash
# Update confidence only
make skills-feedback

# Sync to TRM only
make skills-sync-trm

# Update catalog only
make skills-sync-catalog
```

## 📈 Metrics & Monitoring

### Key Metrics

1. **Error Reduction Rate**
   - Formula: `(expected_7d - actual_7d) / expected_7d * 100`
   - Target: >50% for high-confidence skills

2. **Guardrail Coverage**
   - Formula: `covered_patterns / total_patterns * 100`
   - Target: >70%

3. **Confidence Score Distribution**
   - Mean: Should trend upward over time
   - Variance: Should decrease (skills stabilize)

4. **Training Dataset Growth**
   - Skillsmith contributions: Should be 30-50% of total
   - Forum contributions: 40-60%
   - Manual: 10-20%

### Dashboard Views

| View | Purpose | Update Frequency |
|------|---------|------------------|
| Error Trend | Detect spikes/patterns | 5 min |
| Skill Effectiveness | Validate interventions | Daily |
| Coverage | Identify gaps | Daily |
| Training Growth | Track learning progress | Weekly |

## 🧪 Testing Integration

```bash
# Test individual components
pytest tests/test_skillsmith_miner.py -v
pytest tests/test_db_fingerprint.py -v

# Test integration
python3 services/skillsmith/integrate.py --dry-run

# Test specific step
python3 services/skillsmith/feedback_loop.py
python3 services/skillsmith/trm_sync.py
python3 services/skillsmith/sync_catalog.py
```

## 🔧 Configuration

### Thresholds

Adjust in respective scripts:

```python
# feedback_loop.py
BOOST_THRESHOLD = 0.5      # Impact ratio for boost
REDUCE_THRESHOLD = 0.9     # Impact ratio for reduce

# trm_sync.py
# (No thresholds, syncs all approved)

# sync_catalog.py
MIN_HITS_7D = 1            # Minimum to include in catalog

# integrate.py
RETRAIN_THRESHOLD = 10     # TRM additions to trigger retrain
```

### Frequencies

Edit in `.github/workflows/`:

```yaml
# skillsmith.yml (mining)
schedule:
  - cron: "0 */6 * * *"  # Every 6 hours

# skillsmith-integration.yml
schedule:
  - cron: "0 2 * * *"    # Daily at 2 AM
```

## 🐛 Troubleshooting

### Integration fails with "no data"

**Cause**: No approved skills or error_signatures empty

**Fix**:
```bash
# Check error signatures
psql "$SUPABASE_DB_HOST" -c "SELECT COUNT(*) FROM error_signatures;"

# Check approved skills
ls -1 skills/*.yaml | wc -l

# Refresh materialized view
psql "$SUPABASE_DB_HOST" -c "REFRESH MATERIALIZED VIEW error_signatures;"
```

### Confidence not updating

**Cause**: Skills missing fingerprint field

**Fix**:
```bash
# Check skill structure
grep -A5 "match:" skills/GR-*.yaml

# Should have:
# match:
#   fingerprint: "00000000-0000-0000-0000-abc123"
```

### TRM duplicates

**Cause**: Fingerprint tracking failed

**Fix**:
```bash
# Check dataset for duplicates
cat datasets/trm/erp_tasks.jsonl | jq -r '.fingerprint' | sort | uniq -d

# Remove duplicates
cat datasets/trm/erp_tasks.jsonl | \
  jq -c '.' | \
  sort -u -t'"' -k4 > /tmp/deduped.jsonl
mv /tmp/deduped.jsonl datasets/trm/erp_tasks.jsonl
```

### Dashboard queries slow

**Cause**: Missing indexes

**Fix**:
```sql
-- Add recommended indexes
CREATE INDEX idx_error_signatures_hits
  ON error_signatures(hits_7d DESC);

CREATE INDEX idx_confidence_updates_timestamp
  ON confidence_updates(timestamp DESC);

CREATE INDEX idx_trm_dataset_approved
  ON trm_dataset(approved_at DESC);
```

## 📚 Related Documentation

- [Skillsmith Guide](./skillsmith-guide.md) - Core mining system
- [Error Catalog](./error-codes.yaml) - Live catalog
- [TRM Dataset Format](../datasets/trm/README.md) - Training format
- [Superset Dashboards](../superset/dashboards/README.md) - Monitoring

## 🤝 Contributing

To extend the integration:

1. **Add new feedback metric**: Edit `feedback_loop.py:_calculate_confidence_update()`
2. **Enrich TRM format**: Edit `trm_sync.py:_skill_to_training_example()`
3. **Add catalog category**: Edit `sync_catalog.py:_classify_error()`
4. **Add dashboard chart**: Edit `superset/dashboards/*.json`

## 📄 License

Part of InsightPulse Odoo - Enterprise SaaS Replacement Suite
