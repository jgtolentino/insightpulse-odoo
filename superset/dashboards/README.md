# Superset Dashboards

Auto-generated dashboards for Skillsmith unified monitoring.

## Available Dashboards

### skillsmith-unified-monitoring.json

Complete monitoring dashboard showing:

1. **Error Trends** - Live production error frequencies (7d vs 30d rolling)
2. **Skill Effectiveness** - Confidence scores and impact metrics by type
3. **Top Error Patterns** - Distribution by category
4. **Guardrail Coverage** - % of patterns covered by active skills
5. **Training Dataset Growth** - Total examples in TRM dataset
6. **Skill Impact Timeline** - Before/after error rates
7. **Knowledge Source Distribution** - Training examples by source
8. **Confidence Distribution** - Score histogram

## Setup

### 1. Create Supporting Views

Run the SQL script to create necessary database views:

```bash
psql "$SUPABASE_DB_HOST" -U "$SUPABASE_DB_USER" -d "$SUPABASE_DB_NAME" \
  -f superset/sql/skillsmith-views.sql
```

### 2. Import Dashboard

```bash
# Using Superset CLI
superset import-dashboards -p superset/dashboards/skillsmith-unified-monitoring.json

# Or via UI:
# 1. Go to Superset → Dashboards → Import
# 2. Upload skillsmith-unified-monitoring.json
# 3. Verify all datasets connected
```

### 3. Configure Refresh

The dashboard auto-refreshes every 5 minutes. Adjust in dashboard settings if needed.

## Data Sources

The dashboard queries these sources:

| Source | Type | Description |
|--------|------|-------------|
| `error_signatures` | Materialized View | Aggregated error patterns (30d) |
| `error_candidates` | View | Top patterns by impact score |
| `skills` | Table/View | Skill metadata and confidence |
| `confidence_history` | Table | Confidence score updates over time |
| `trm_dataset` | Table | Training dataset entries |
| `error_catalog` | Table/File | Error catalog with guardrail links |

## Filters

Available dashboard filters:

- **Time Range**: Defaults to 30 days
- **Error Kind**: Filter by error type (KeyError, ValueError, etc.)
- **Component**: Filter by Odoo component

## Metrics Explained

### Error Metrics
- **hits_7d**: Error occurrences in last 7 days
- **hits_30d**: Error occurrences in last 30 days
- **impact_score**: Weighted score (7d × 0.7 + 30d × 0.3)

### Skill Metrics
- **confidence**: Skill effectiveness (0.0 - 1.0)
- **coverage_pct**: % of errors with active guardrails
- **avg_confidence**: Average confidence by skill type

### Training Metrics
- **total_examples**: Count of training dataset entries
- **source_distribution**: Examples by source (skillsmith/forum/manual)

## Customization

Edit the JSON to:

1. **Add charts**: Append to `charts` array
2. **Modify layout**: Update `position_json` coordinates
3. **Change colors**: Modify `metadata.color_scheme`
4. **Add filters**: Append to `native_filters` array

## Troubleshooting

### No data showing

1. Check database views exist:
   ```sql
   SELECT * FROM error_signatures LIMIT 1;
   ```

2. Verify refresh schedule:
   ```sql
   SELECT matviewname, last_refresh
   FROM pg_matviews
   WHERE matviewname = 'error_signatures';
   ```

3. Check Superset database connection

### Slow queries

1. Add indexes:
   ```sql
   CREATE INDEX idx_error_signatures_hits
   ON error_signatures(hits_7d DESC);
   ```

2. Limit time range in filters

3. Increase dashboard cache timeout

## Related

- [Skillsmith Guide](../../docs/skillsmith-guide.md)
- [Error Catalog](../../docs/error-codes.yaml)
- [Integration Pipeline](../../services/skillsmith/integrate.py)
