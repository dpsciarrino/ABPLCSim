# api/main.py
#
# FastAPI application entry point.
# Registers all routers and middleware.
# Run locally with: uvicorn api.main:app --reload
#
# TODO: Wire up routers and middleware as each milestone is completed

import logging

logging.basicConfig(
    level=logging.DEBUG,     # show everything during development
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)

from fastapi import FastAPI

app = FastAPI(
    title="PLC Emulator",
    description="Software emulator for Allen-Bradley ControlLogix PLCs.",
    version="0.1.0",
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# ── Routers (uncomment as each milestone is completed) ────────────────────────
# from api.routes import auth, tags, program, scan
# app.include_router(auth.router,    prefix="/auth")
# app.include_router(tags.router,    prefix="/tags")
# app.include_router(program.router, prefix="/program")
# app.include_router(scan.router,    prefix="/scan")

