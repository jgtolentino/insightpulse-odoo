import os, sys, time, requests, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
SEED = ROOT / "seed_repos.txt"

# Base API endpoint; override via env if needed
BASE = os.getenv("GITTODOC_API", "https://insightpulseai.net/gittodoc/api")
INGEST = f"{BASE.rstrip('/')}/ingest"

def iter_repos(path: pathlib.Path):
    for line in path.read_text().splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        yield s

def ingest(repo_url: str):
    try:
        r = requests.post(INGEST, params={"repo_url": repo_url}, timeout=120)
        ok = r.ok
        return ok, (r.json() if ok else {"status": r.status_code, "text": r.text[:400]})
    except Exception as e:
        return False, {"error": str(e)}

def main():
    had_err = False
    for repo in iter_repos(SEED):
        print(f"==> ingest {repo}")
        ok, payload = ingest(repo)
        if ok:
            print(f"    OK -> {payload.get('docs_url')}")
        else:
            had_err = True
            print(f"    ERR -> {payload}")
        # Be polite to GitHub and our service
        time.sleep(float(os.getenv("GITTODOC_INGEST_DELAY", "2.0")))
    sys.exit(1 if had_err else 0)

if __name__ == "__main__":
    if not SEED.exists():
        print(f"Missing seed list: {SEED}")
        sys.exit(1)
    main()
