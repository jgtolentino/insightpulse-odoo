from fastapi import FastAPI

def create_app() -> FastAPI:  # factory avoids import-time crashes
    app = FastAPI(title="Pulser Hub MCP")

    @app.get("/healthz")
    def healthz():
        return {"ok": True}

    # TODO: include your MCP routes here (keep imports inside the function).
    # from .routes import router
    # app.include_router(router, prefix="/mcp")

    return app
