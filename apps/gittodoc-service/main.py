from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from gittodoc.utils import ingest as do_ingest, ROOT as DOC_ROOT
from gittodoc.github_search import search_repos, search_code

app = FastAPI(title="Gittodoc Service")

@app.get("/health")
def health(): return {"ok": True}

@app.post("/ingest")
def ingest(repo_url: str = Query(..., description="https://github.com/owner/name")):
    res = do_ingest(repo_url)
    return JSONResponse(res)

@app.get("/search")
def search(q: str, repo: str | None = None, per_page: int = 5):
    if repo:
        return search_code(q, repo, per_page=per_page)
    return search_repos(q, per_page=per_page)

# Serve static docs at /gittodoc/{slug}/
DOC_ROOT.mkdir(parents=True, exist_ok=True)
app.mount("/gittodoc", StaticFiles(directory=str(DOC_ROOT), html=True), name="gittodoc")
