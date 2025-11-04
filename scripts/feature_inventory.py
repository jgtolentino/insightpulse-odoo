#!/usr/bin/env python3
import os, ast, json, pathlib, re
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
# Scan multiple addon directories
ADDON_DIRS = [
    ROOT / 'odoo_addons',
    ROOT / 'addons',
    ROOT / 'custom_addons',
]
OUT = ROOT / 'docs' / 'feature-inventory.md'

# optional DB status via PG_DSN env var (e.g. postgresql://user:pass@host:5432/odoo)
pg_status = {}
PG_DSN = os.getenv('PG_DSN')
if PG_DSN:
    try:
        import psycopg2
        with psycopg2.connect(PG_DSN) as conn, conn.cursor() as cur:
            cur.execute("select name, state, latest_version from ir_module_module")
            for name, state, ver in cur.fetchall():
                pg_status[name] = { 'state': state, 'db_version': ver }
    except Exception as e:
        pg_status['__error__'] = str(e)

rows = []
for addon_dir in ADDON_DIRS:
    if not addon_dir.exists():
        continue
    for manifest in addon_dir.rglob('__manifest__.py'):
        modpath = manifest.parent
        rel = modpath.relative_to(ROOT).as_posix()
        tech = modpath.name
        src = 'Custom'
        if '/oca/' in rel: src = 'OCA'
        if '/odoo/' in rel or 'Odoo S.A.' in rel: src = 'Official'
        try:
            data = ast.literal_eval(manifest.read_text())
        except Exception:
            data = {}
        rows.append({
            'module': tech,
            'source': src,
            'path': rel,
            'name': data.get('name') or tech,
            'version': data.get('version',''),
            'summary': data.get('summary',''),
            'depends': ','.join(data.get('depends',[]) or []),
            'license': data.get('license',''),
            'state': pg_status.get(tech, {}).get('state','unknown'),
        })

rows.sort(key=lambda r: (r['source'], r['module']))

OUT.parent.mkdir(parents=True, exist_ok=True)
with OUT.open('w', encoding='utf-8') as f:
    f.write(f"# Feature Inventory\nGenerated: {datetime.now(timezone.utc).isoformat()}Z\n\n")
    if '__error__' in pg_status:
        f.write(f"> DB status unavailable: {pg_status['__error__']}\n\n")
    f.write('| Module | Source | Version | State | Summary | Depends | Path |\n')
    f.write('|---|---|---|---|---|---|---|\n')
    for r in rows:
        f.write(f"| {r['module']} | {r['source']} | {r['version']} | {r['state']} | {r['summary'].replace('|','/')} | {r['depends']} | {r['path']} |\n")
print(f'Wrote {OUT}')
