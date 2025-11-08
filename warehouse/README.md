# Warehouse Views - T&E MVP

SQL views and materialized views for Supabase analytics warehouse.

## Files

- `views.sql` - Base expense fact view
- `mv_refresh.sql` - Materialized view for 7-day summary

## Deployment

```bash
psql "$POSTGRES_URL" -f warehouse/views.sql
psql "$POSTGRES_URL" -f warehouse/mv_refresh.sql
```

## Refresh Schedule

Set up hourly refresh:
```sql
SELECT cron.schedule(
    'refresh-expense-mv',
    '0 * * * *',
    $$REFRESH MATERIALIZED VIEW public.mv_expense_7d$$
);
```
