import os, shutil, subprocess, re, json, hashlib, pathlib, time
from slugify import slugify

ROOT = pathlib.Path(os.getenv("GITTODOC_ROOT", ".")) / "docs" / "gittodoc"  # output root
CACHE = pathlib.Path(os.getenv("GITTODOC_CACHE", ".")) / ".gittodoc_cache"

def _slug_from_url(url: str) -> str:
  base = re.sub(r'^https?://(www\.)?github\.com/', '', url.strip()).strip('/')
  return slugify(base)

def _clone_or_update(url: str, dest: pathlib.Path) -> None:
  if dest.exists():
    # git fetch --all && reset --hard
    subprocess.run(["git","-C",str(dest),"fetch","--all"], check=True)
    subprocess.run(["git","-C",str(dest),"reset","--hard","origin/HEAD"], check=False)
  else:
    subprocess.run(["git","clone","--depth","1",url,str(dest)], check=True)

def _collect(repo_dir: pathlib.Path) -> dict:
  docs = []
  exts = {".md",".rst",".txt",".py",".js",".ts",".tsx",".xml",".yml",".yaml",".json"}
  for p in repo_dir.rglob("*"):
    if p.is_file() and p.suffix.lower() in exts and p.stat().st_size < 2_000_000:
      rel = p.relative_to(repo_dir).as_posix()
      try:
        text = p.read_text(errors="ignore")
      except Exception:
        continue
      docs.append({"path":rel,"size":p.stat().st_size,"text":text})
  return {"count":len(docs),"items":docs}

def _render_html(slug: str, dataset: dict, out_dir: pathlib.Path) -> None:
  out_dir.mkdir(parents=True, exist_ok=True)
  index = out_dir / "index.html"
  idx = out_dir / "index.json"
  idx.write_text(json.dumps(dataset, ensure_ascii=False))
  # minimal searchable page
  html = f"""<!doctype html>
<html><head><meta charset="utf-8"/><title>Gittodoc – {slug}</title>
<style>body{{font-family:ui-sans-serif,system-ui;margin:24px}}pre{{white-space:pre-wrap}}</style>
</head><body>
<h1>Gittodoc: {slug}</h1>
<input id="q" placeholder="Search…" style="padding:8px;width:60%"/>
<div id="r"></div>
<script>
let data=null;fetch('index.json').then(r=>r.json()).then(j=>{{data=j}});
document.getElementById('q').addEventListener('input',e=>{{
  const q=e.target.value.toLowerCase(); if(!data) return;
  const hits=(q?data.items.filter(x=>x.path.toLowerCase().includes(q)||x.text.toLowerCase().includes(q)) : []).slice(0,50);
  document.getElementById('r').innerHTML=hits.map(h=>`<details><summary>${{h.path}}</summary><pre>${{h.text.substring(0,4000)}}</pre></details>`).join('');
}});
</script>
</body></html>"""
  index.write_text(html)

def ingest(url: str) -> dict:
  slug = _slug_from_url(url)
  repo_cache = CACHE / slug
  docs_dir = ROOT / slug
  CACHE.mkdir(parents=True, exist_ok=True)
  _clone_or_update(url, repo_cache)
  dataset = _collect(repo_cache)
  meta = {"slug":slug,"url":url,"ts":int(time.time()),"files":dataset["count"]}
  _render_html(slug, dataset, docs_dir)
  (docs_dir/"meta.json").write_text(json.dumps(meta))
  return {"ok":True, "slug":slug, "docs_url": f"/gittodoc/{slug}/"}
