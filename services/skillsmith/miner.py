#!/usr/bin/env python3
"""
Skillsmith Miner: Mine error patterns and generate skill candidates
"""
import os, json, pathlib, psycopg, jinja2, argparse, datetime
from psycopg.rows import dict_row

try:
    from slugify import slugify as _slug
    def slug(s): return _slug(s, separator='-')[:40]
except ImportError:
    # fallback if slugify not installed
    import re
    def slug(s): return re.sub(r'[^a-z0-9]+', '-', s.lower())[:40].strip('-')

# Template loader
TEMPLATES_DIR = pathlib.Path(__file__).parent / "templates"
TEMPLATES = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=False,
)

OUT_DIR = pathlib.Path("skills/proposed")

def pick_kind(row):
    """
    Heuristic: determine if error should be guardrail or fixer
    - guardrails: prevent bad input/config (KeyError, Missing, Invalid)
    - fixers: autopatch known issues (ImportError, Template override)
    """
    msg = (row["norm_msg"] or "").lower()
    if any(k in msg for k in ["manifest", "xpath", "missing", "invalid", "forbidden", "permission", "keyerror", "valueerror"]):
        return "guardrail"
    return "fixer"

def main(min_hits:int=3, top:int=20):
    """Mine error signatures and generate skill candidates"""
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # DB connection from env vars
    db_config = {
        'host': os.getenv('SUPABASE_DB_HOST'),
        'dbname': os.getenv('SUPABASE_DB_NAME'),
        'user': os.getenv('SUPABASE_DB_USER'),
        'password': os.getenv('SUPABASE_DB_PASSWORD'),
        'port': os.getenv('SUPABASE_DB_PORT', '5432'),
    }

    with psycopg.connect(**db_config, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            # Refresh materialized view
            cur.execute("refresh materialized view public.error_signatures;")
            conn.commit()

            # Get top candidates
            cur.execute("""
                select * from public.error_candidates
                where hits_7d >= %s
                order by impact_score desc
                limit %s
            """, (min_hits, top))
            rows = cur.fetchall()

    print(f"Found {len(rows)} error candidates (≥{min_hits} hits in 7d)")

    created = []
    for r in rows:
        kind = pick_kind(r)
        title = f"{r['kind']} in {r['component']}"
        sid = f"{'GR' if kind=='guardrail' else 'FX'}-{str(r['fp'])[:8].upper()}"
        fname = f"{sid}_{slug(title)}.yaml"

        ctx = {
            "id": sid,
            "title": title,
            "component": r["component"],
            "pattern": r["norm_msg"][:240],
            "fingerprint": str(r["fp"]),
            "hits_7d": r["hits_7d"],
            "hits_30d": r["hits_30d"],
            "impact_score": round(float(r.get("impact_score", 0)), 2),
            "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        }

        tpl = TEMPLATES.get_template(f"{kind}.yaml.j2")
        content = tpl.render(**ctx)

        out_path = OUT_DIR / fname
        out_path.write_text(content, encoding="utf-8")
        created.append(fname)
        print(f"  ✓ {fname}")

    summary = {
        "created": created,
        "count": len(created),
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }
    print(json.dumps(summary, indent=2))
    return summary

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Mine error patterns and generate skill candidates")
    ap.add_argument("--min_hits", type=int, default=3, help="Minimum hits in 7d to qualify")
    ap.add_argument("--top", type=int, default=20, help="Max candidates to generate")
    args = ap.parse_args()
    main(args.min_hits, args.top)
