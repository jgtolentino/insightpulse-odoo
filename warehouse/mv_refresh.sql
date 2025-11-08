-- Materialized view for 7-day expense summary
create materialized view if not exists public.mv_expense_7d as
select
    date_trunc('day', date) d,
    sum(amount) amt
from public.vw_expense_fact
where date > now() - interval '7 days'
group by 1;

-- Schedule this to refresh hourly via cron or pg_cron
-- SELECT cron.schedule('refresh-expense-mv', '0 * * * *', $$REFRESH MATERIALIZED VIEW public.mv_expense_7d$$);
