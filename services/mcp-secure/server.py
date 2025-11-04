import os, subprocess, json, secrets
from fastapi import FastAPI, Request, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

app = FastAPI(title="MCP Secure", version="1.1.0")

# ---- Config via env ----
BEARER = os.getenv("MCP_BEARER", "")
BASIC_USER = os.getenv("MCP_BASIC_USER", "")
BASIC_PASS = os.getenv("MCP_BASIC_PASS", "")
ALLOW_IPS = [x.strip() for x in os.getenv("MCP_ALLOW_IPS", "").split(",") if x.strip()]
CORS_ORIGINS = [x.strip() for x in os.getenv("CORS_ORIGINS", "https://mcp.insightpulseai.net,https://erp.insightpulseai.net").split(",")]

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBasic()

class ToolCall(BaseModel):
    name: str
    arguments: dict | None = None

@app.get("/health")
def health(): return {"ok": True}

@app.get("/mcp/catalog")
def catalog():
    return {"version":"1.0","tools":[
        {"name":"git_diff","description":"git status/diff","input_schema":{"type":"object","properties":{"path":{"type":"string"}}}},
        {"name":"odoo_ping","description":"GET /web/login","input_schema":{"type":"object","properties":{"url":{"type":"string"}}}},
        {"name":"package_odoo","description":"zip addon","input_schema":{"type":"object","properties":{"module":{"type":"string"}}}},
    ]}

def ip_ok(req: Request) -> bool:
    return (not ALLOW_IPS) or (req.client and req.client.host in ALLOW_IPS)

def basic_ok(creds: HTTPBasicCredentials | None) -> bool:
    if not BASIC_USER or not BASIC_PASS or not creds: return False
    return (creds.username == BASIC_USER) and secrets.compare_digest(creds.password, BASIC_PASS)

def bearer_ok(authorization: str | None) -> bool:
    if not BEARER: return False
    return bool(authorization and authorization.startswith("Bearer ") and authorization.removeprefix("Bearer ").strip() == BEARER)

def guard(req: Request, authorization: str | None, creds: HTTPBasicCredentials | None):
    if not ip_ok(req):
        raise HTTPException(403, "IP not allowed")
    if not (bearer_ok(authorization) or basic_ok(creds)):
        # Challenge for Basic so browsers can prompt credentials
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.post("/mcp/tools/call")
async def call(req: Request,
               authorization: str | None = Header(None),
               creds: HTTPBasicCredentials = Depends(security)):
    guard(req, authorization, creds)
    tc = ToolCall(**(await req.json())); args = tc.arguments or {}
    if tc.name=="git_diff":
        p=args.get("path",".")
        out=subprocess.run(["bash","-lc",f"cd '{p}' && git status -sb && echo '---' && git diff --stat"],capture_output=True,text=True,timeout=60)
        return {"ok":True,"stdout":out.stdout,"stderr":out.stderr,"code":out.returncode}
    if tc.name=="odoo_ping":
        import requests; url=args.get("url"); r=requests.get(url,timeout=10)
        return {"ok":True,"status":r.status_code,"len":len(r.text)}
    if tc.name=="package_odoo":
        mod=args.get("module"); os.makedirs("dist",exist_ok=True)
        out=subprocess.run(["bash","-lc",f"zip -r dist/{mod}.zip odoo_addons/{mod} -x '*/__pycache__/*' '*.pyc'"],capture_output=True,text=True)
        return {"ok":out.returncode==0,"zip":f"dist/{mod}.zip","stderr":out.stderr}
    raise HTTPException(404,"unknown tool")
