from fastapi import FastAPI, HTTPException
import httpx, os

app = FastAPI(title="Skill Hub", version="1.0.0")
MCP_BASE = os.getenv("MCP_BASE","http://127.0.0.1:8001")

@app.get("/skills/catalog")
async def catalog():
    async with httpx.AsyncClient(timeout=15) as cl:
        r = await cl.get(f"{MCP_BASE}/mcp/catalog")
        r.raise_for_status()
        tools = r.json().get("tools",[])
        skills = [
            {
                "name": f"mcp.{t['name']}",
                "kind":"mcp",
                "description":t.get("description",""),
                "input_schema":t.get("input_schema",{})
            }
            for t in tools
        ]
        return {"skills": skills}

@app.post("/skills/call")
async def call(body: dict):
    name = body.get("name")
    args = body.get("arguments",{})

    if not name or not name.startswith("mcp."):
        raise HTTPException(400,"use mcp.<tool>")

    tool = name.split(".",1)[1]

    async with httpx.AsyncClient(timeout=60) as cl:
        r = await cl.post(
            f"{MCP_BASE}/mcp/tools/call",
            json={"name": tool, "arguments": args}
        )
        return {
            "ok": r.status_code==200,
            "data": r.json() if r.content else None
        }
