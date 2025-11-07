# Gittodoc Service
Turn any GitHub repo into a shareable documentation link + lightweight search.
- POST /ingest?repo_url=https://github.com/owner/name → builds /gittodoc/{slug}/index.html
- GET  /gittodoc/{slug}/ → static docs
- GET  /search?q=fastapi               (repo discovery)
- GET  /search?q=router&repo=owner/name (code search)
