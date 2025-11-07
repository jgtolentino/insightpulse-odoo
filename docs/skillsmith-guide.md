# Skillsmith - Auto-Skill Builder

Skillsmith is an automated system that mines error patterns from production logs and generates skill candidates that either prevent known errors (guardrails) or automatically fix known issues (fixers).

## 🎯 Overview

### The Problem

Production systems generate errors. Many errors are recurring patterns that could be:
- **Prevented** with validation guardrails
- **Auto-fixed** with automated patches

Traditional approaches require manual analysis and implementation.

### The Solution

Skillsmith automates the entire lifecycle:

1. **Ingest** → Errors flow into `agent_errors` table
2. **Normalize** → Strip volatile data (UUIDs, timestamps, IDs)
3. **Fingerprint** → Generate stable signatures for clustering
4. **Mine** → Identify top patterns by frequency and recency
5. **Generate** → Create skill YAML candidates (guardrails/fixers)
6. **Propose** → Open PR for review
7. **Approve** → Human review and approval
8. **Deploy** → Activate in production
9. **Learn** → Track outcomes and adjust confidence

## 🏗️ Architecture

```
┌─────────────────┐
│  Production     │
│  Errors         │
└────────┬────────┘
         │
         v
┌─────────────────────────────────────┐
│  Collector Service                  │
│  - Normalizes error text            │
│  - Generates fingerprints           │
│  - Stores in agent_errors table     │
└────────┬────────────────────────────┘
         │
         v
┌─────────────────────────────────────┐
│  Database (Supabase)                │
│  - error_signatures (MV)            │
│  - error_candidates (View)          │
│  - Aggregates by fingerprint        │
└────────┬────────────────────────────┘
         │
         v
┌─────────────────────────────────────┐
│  Miner (runs every 6h)              │
│  - Queries error_candidates         │
│  - Picks top N by impact score      │
│  - Generates YAML files             │
└────────┬────────────────────────────┘
         │
         v
┌─────────────────────────────────────┐
│  PR Automation                      │
│  - Creates branch                   │
│  - Commits proposals                │
│  - Opens GitHub PR                  │
└────────┬────────────────────────────┘
         │
         v
┌─────────────────────────────────────┐
│  Human Review                       │
│  - Reviews patterns                 │
│  - Tests in sandbox                 │
│  - Approves skills                  │
└────────┬────────────────────────────┘
         │
         v
┌─────────────────────────────────────┐
│  Deployment                         │
│  - Move to skills/ directory        │
│  - Set status: approved             │
│  - Run: make retrain                │
└─────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Setup Database Schema

```bash
make skills-db-setup
```

This creates:
- `normalize_error_message()` function
- `error_fingerprint()` function
- `error_signatures` materialized view
- `error_candidates` view

### 2. Start Collecting Errors

The collector service automatically normalizes and fingerprints errors:

```python
from services.collector.main import ingest_error

event = {
    "error": "KeyError: 'partner_id'",
    "component": "odoo.addons.sale",
    "tags": ["odoo", "sale"]
}

result = ingest_error(event)
# Result includes: norm_error, fingerprint, ts
```

### 3. Mine Error Patterns

Run manually or wait for automated schedule:

```bash
make skills-mine
```

This generates proposals in `skills/proposed/`

### 4. Review Proposals

Check the PR that was automatically created, or run locally:

```bash
ls skills/proposed/
cat skills/proposed/GR-*.yaml
```

### 5. Approve Skills

For guardrails:

```bash
mv skills/proposed/GR-ABCD1234*.yaml skills/
sed -i 's/status: proposed/status: approved/' skills/GR-*.yaml
make retrain
```

For fixers:

```bash
# 1. Implement autopatch
cat > autopatches/fx-abcd1234.py <<'PY'
def apply(repo_dir: str) -> bool:
    # Your fix here
    return True
PY

# 2. Test
pytest tests/test_autopatches.py

# 3. Approve
mv skills/proposed/FX-*.yaml skills/
sed -i 's/status: proposed/status: approved/' skills/FX-*.yaml
sed -i 's/dry_run: true/dry_run: false/' skills/FX-*.yaml
make retrain
```

## 📊 Database Schema

### Tables

#### `agent_errors`

```sql
create table public.agent_errors (
    id bigserial primary key,
    ts timestamptz default now(),
    error text,
    component text,
    tags text[],
    norm_error text,
    fingerprint uuid
);
```

### Functions

#### `normalize_error_message(txt text) → text`

Strips volatile parts:
- UUIDs → `<uuid>`
- Epoch timestamps → `<epoch>`
- Large integers → `<int>`
- ISO timestamps → `<ts>`

```sql
select normalize_error_message('KeyError: 123456 at 2025-11-07T10:00:00Z');
-- Result: KeyError: <int> at <ts>
```

#### `error_fingerprint(type, component, msg) → uuid`

Generates stable fingerprint:

```sql
select error_fingerprint('KeyError', 'sale.order', 'KeyError: partner_id 123');
-- Result: 00000000-0000-0000-0000-abc123def456
```

### Views

#### `error_signatures` (Materialized View)

Aggregates errors by fingerprint:

```sql
select * from error_signatures
where hits_7d > 2
order by impact_score desc
limit 10;
```

Columns:
- `fp`: Fingerprint (UUID)
- `component`: Error component
- `kind`: Error type (KeyError, ValueError, etc.)
- `norm_msg`: Normalized message
- `hits_30d`: Count in 30 days
- `hits_7d`: Count in 7 days
- `tags`: Aggregated tags

#### `error_candidates` (View)

Top candidates with impact scoring:

```sql
select * from error_candidates
where hits_7d >= 3
order by impact_score desc;
```

Impact score: `hits_7d × 0.7 + hits_30d × 0.3`

## 🤖 Automated Mining

### GitHub Actions Workflow

`.github/workflows/skillsmith.yml` runs every 6 hours:

1. Refreshes `error_signatures` materialized view
2. Queries top candidates
3. Generates YAML files in `skills/proposed/`
4. Creates branch and commits
5. Opens PR with summary

### Configuration

Adjust thresholds:

```yaml
# .github/workflows/skillsmith.yml
on:
  workflow_dispatch:
    inputs:
      min_hits:
        default: '2'    # Minimum in 7 days
      top_n:
        default: '50'   # Max candidates
```

## 📝 Skill Format

### Guardrail Example

```yaml
id: GR-ABCD1234
name: "KeyError in sale.order"
kind: guardrail
status: proposed

match:
  component: "odoo.addons.sale"
  message_regex: "KeyError.*partner_id"
  fingerprint: "00000000-0000-0000-0000-abc123def456"

action:
  type: "block"
  message: "Prevented: KeyError in sale.order"

metadata:
  hits_7d: 10
  hits_30d: 25
  impact_score: 15.5
  auto_generated: true
```

### Fixer Example

```yaml
id: FX-ABCD1234
name: "ImportError in custom module"
kind: fixer
status: proposed

match:
  component: "odoo.addons.custom"
  message_regex: "ImportError.*missing_module"
  fingerprint: "00000000-0000-0000-0000-xyz789abc012"

action:
  type: "autopatch"
  script: "autopatches/fx-abcd1234.py"
  dry_run: true

metadata:
  hits_7d: 8
  hits_30d: 20
  impact_score: 12.4
  auto_generated: true
```

## 🧪 Testing

### Test Database Functions

```bash
pytest tests/test_db_fingerprint.py -v
```

Tests:
- Normalization logic
- Fingerprint stability
- View existence
- Sample data processing

### Test Miner

```bash
pytest tests/test_skillsmith_miner.py -v
```

Tests:
- Pattern classification (guardrail vs fixer)
- Template rendering
- Output file generation
- Error handling

## 📈 Monitoring

### Check Mining Activity

```bash
# View recent runs
ls -lt .github/workflows/skillsmith-*.log

# Check proposals
ls -1 skills/proposed/

# Database stats
psql "$SUPABASE_DB_HOST" -c "
  select count(*) as total_errors,
         count(distinct fingerprint) as unique_patterns
  from agent_errors
  where ts > now() - interval '7 days'
"
```

### Metrics to Track

1. **Error volume**: Total errors per day
2. **Pattern diversity**: Unique fingerprints
3. **Skill proposals**: Generated per week
4. **Approval rate**: Approved / proposed
5. **Impact**: Errors prevented by guardrails
6. **Fix rate**: Errors auto-fixed by fixers

## 🔧 Customization

### Adjust Pattern Matching

Edit heuristic in `services/skillsmith/miner.py`:

```python
def pick_kind(row):
    msg = (row["norm_msg"] or "").lower()

    # Add your custom rules
    if "custom_pattern" in msg:
        return "guardrail"

    if any(k in msg for k in ["manifest", "xpath"]):
        return "guardrail"

    return "fixer"
```

### Custom Templates

Edit Jinja2 templates in `services/skillsmith/templates/`:

- `guardrail.yaml.j2`
- `fixer.yaml.j2`

### Scoring Algorithm

Adjust impact scoring in SQL view:

```sql
-- Current: 70% weight on last 7d, 30% on last 30d
(hits_7d*0.7 + hits_30d*0.3) as impact_score

-- Example: Equal weight
(hits_7d*0.5 + hits_30d*0.5) as impact_score
```

## 🐛 Troubleshooting

### No candidates generated

**Check thresholds:**
```bash
python3 services/skillsmith/miner.py --min_hits 1 --top 100
```

**Check database:**
```sql
select * from error_candidates limit 10;
```

### Database connection errors

**Verify env vars:**
```bash
echo $SUPABASE_DB_HOST
echo $SUPABASE_DB_USER
# etc.
```

**Test connection:**
```bash
psql "$SUPABASE_DB_HOST" -U "$SUPABASE_DB_USER" -c "select version()"
```

### Template rendering errors

**Check templates exist:**
```bash
ls services/skillsmith/templates/
```

**Test template:**
```python
from services.skillsmith import miner
tpl = miner.TEMPLATES.get_template("guardrail.yaml.j2")
print(tpl.render(id="TEST", title="Test", ...))
```

## 📚 Further Reading

- [Error Mining Techniques](./error-mining.md)
- [Autopatch Best Practices](../autopatches/README.md)
- [Skill Approval Workflow](../skills/proposed/README.md)
- [Makefile Reference](../Makefile) - Search for `skills-*`

## 🤝 Contributing

To improve Skillsmith:

1. Add new pattern detection heuristics
2. Improve normalization logic
3. Create template variants
4. Add new test cases
5. Document edge cases
6. Share autopatch examples

## 📄 License

Part of InsightPulse Odoo - Enterprise SaaS Replacement Suite
