import os
import psycopg
import pathlib
import jinja2
import argparse
from psycopg.rows import dict_row
from slugify import slugify

TEMPLATES = pathlib.Path('skillsmith/templates')
OUT = pathlib.Path('skills/proposed')
OUT.mkdir(parents=True, exist_ok=True)

def pick_kind(msg):
    m = (msg or '').lower()
    return 'guardrail' if any(k in m for k in ['missing', 'invalid', 'manifest', 'xpath', 'permission']) else 'fixer'

def main(min_hits=2, top=50):
    with psycopg.connect(
        host=os.getenv('SUPABASE_DB_HOST'),
        dbname=os.getenv('SUPABASE_DB_NAME'),
        user=os.getenv('SUPABASE_DB_USER'),
        password=os.getenv('SUPABASE_DB_PASSWORD'),
        port=os.getenv('SUPABASE_DB_PORT'),
        row_factory=dict_row
    ) as conn:
        with conn.cursor() as cur:
            cur.execute('refresh materialized view public.error_signatures;')
            cur.execute(
                'select * from public.error_candidates where hits_7d >= %s order by impact_score desc limit %s',
                (min_hits, top)
            )
            rows = cur.fetchall()

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(TEMPLATES)))
    for r in rows:
        kind = pick_kind(r['norm_msg'])
        sid = (('GR' if kind == 'guardrail' else 'FX') + '-' + str(r['fp'])[:8]).upper()
        fname = f"{sid}_{slugify(r['component'])}.yaml"
        tpl = env.get_template('guardrail.yaml.j2' if kind == 'guardrail' else 'fixer.yaml.j2')
        OUT.joinpath(fname).write_text(tpl.render(
            id=sid,
            title=f"{r['kind']} in {r['component']}",
            component=r['component'],
            pattern=r['norm_msg'][:200],
            fingerprint=str(r['fp'])
        ))
        print('created', fname)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--min_hits', type=int, default=2)
    ap.add_argument('--top', type=int, default=50)
    a = ap.parse_args()
    main(a.min_hits, a.top)
