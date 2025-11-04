import os, subprocess, json
from fastapi import FastAPI, Request, Header, HTTPException
from pydantic import BaseModel

app = FastAPI(title="MCP Secure", version="1.0.0")
BEARER = os.getenv("MCP_BEARER","")

class ToolCall(BaseModel):
    name: str
    arguments: dict | None = None

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/mcp/catalog")
def catalog():
    return {
        "version":"1.0",
        "tools":[
            {
                "name":"git_diff",
                "description":"git status/diff",
                "input_schema":{
                    "type":"object",
                    "properties":{
                        "path":{"type":"string"}
                    }
                }
            },
            {
                "name":"odoo_ping",
                "description":"GET /web/login",
                "input_schema":{
                    "type":"object",
                    "properties":{
                        "url":{"type":"string"}
                    }
                }
            },
            {
                "name":"package_odoo",
                "description":"zip addon",
                "input_schema":{
                    "type":"object",
                    "properties":{
                        "module":{"type":"string"}
                    }
                }
            },
        ]
    }

def guard(auth):
    if not BEARER:
        raise HTTPException(500,"MCP_BEARER not set")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(401,"auth")
    if auth.removeprefix("Bearer ").strip()!=BEARER:
        raise HTTPException(401,"bad token")

@app.post("/mcp/tools/call")
async def call(req: Request, authorization: str | None = Header(None)):
    body = await req.body()
    guard(authorization)

    tc = ToolCall(**json.loads(body))
    args = tc.arguments or {}

    if tc.name=="git_diff":
        p=args.get("path",".")
        out=subprocess.run(
            ["bash","-lc",f"cd '{p}' && git status -sb && echo '---' && git diff --stat"],
            capture_output=True,
            text=True,
            timeout=60
        )
        return {"ok":True,"stdout":out.stdout,"stderr":out.stderr,"code":out.returncode}

    if tc.name=="odoo_ping":
        import requests
        url=args.get("url")
        r=requests.get(url,timeout=10)
        return {"ok":True,"status":r.status_code,"len":len(r.text)}

    if tc.name=="package_odoo":
        mod=args.get("module")
        os.makedirs("dist",exist_ok=True)
        out=subprocess.run(
            ["bash","-lc",f"zip -r dist/{mod}.zip odoo_addons/{mod} -x '*/__pycache__/*' '*.pyc'"],
            capture_output=True,
            text=True
        )
        return {"ok":out.returncode==0,"zip":f"dist/{mod}.zip","stderr":out.stderr}

    raise HTTPException(404,"unknown tool")
