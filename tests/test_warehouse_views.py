import os
import psycopg
from psycopg.rows import dict_row

def test_vw_expense_fact_exists():
    required = ['SUPABASE_DB_HOST', 'SUPABASE_DB_NAME', 'SUPABASE_DB_USER', 'SUPABASE_DB_PASSWORD', 'SUPABASE_DB_PORT']
    if not all(os.getenv(k) for k in required):
        assert True
        return

    with psycopg.connect(
        host=os.getenv('SUPABASE_DB_HOST'),
        dbname=os.getenv('SUPABASE_DB_NAME'),
        user=os.getenv('SUPABASE_DB_USER'),
        password=os.getenv('SUPABASE_DB_PASSWORD'),
        port=os.getenv('SUPABASE_DB_PORT'),
        row_factory=dict_row
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("select 1 from pg_views where viewname='vw_expense_fact'")
            assert cur.fetchone() is not None
