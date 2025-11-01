#!/usr/bin/env python3
import ast, datetime, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
ADDONS = ROOT / "custom_addons"
T = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
README = (ROOT/"templates/README.md.j2").read_text()
CHANGELOG = (ROOT/"templates/CHANGELOG.md.j2").read_text()
ADR = (ROOT/"templates/ADR.md.j2").read_text()
BEG, END = "<!-- AUTO:BEGIN README -->", "<!-- AUTO:END README -->"

def manifest(p): return ast.literal_eval(p.read_text(encoding="utf-8"))

def upsert_readme(d, ctx):
  p = d/"README.md"; new = f"{BEG}\n"+README.format(**ctx)+f"\n{END}\n"
  if p.exists():
    old = p.read_text(encoding="utf-8")
    if BEG in old and END in old:
      old = re.sub(f"{BEG}[\\s\\S]*?{END}", new, old, flags=re.M)
      p.write_text(old, encoding="utf-8")
      return
  p.write_text(new, encoding="utf-8")

def ensure(path, text):
  if not path.exists(): path.write_text(text, encoding="utf-8")

def main():
  for mod in sorted(ADDONS.iterdir()):
    man = mod/"__manifest__.py"
    if not man.exists(): continue
    m = manifest(man)
    ctx = {
      "module": mod.name, "name": m.get("name", mod.name),
      "version": m.get("version","0.0.0"), "summary": m.get("summary",""),
      "depends": ", ".join(m.get("depends",[])), "time": T
    }
    upsert_readme(mod, ctx)
    ensure(mod/"CHANGELOG.md", CHANGELOG.format(**ctx))
    adr_dir = ROOT/"docs"/"adr"; adr_dir.mkdir(parents=True, exist_ok=True)
    ensure(adr_dir/f"ADR-{datetime.datetime.utcnow():%Y%m%d}-{mod.name}.md", ADR.format(**ctx))
  print("[docgen] done")
if __name__=="__main__": main()
