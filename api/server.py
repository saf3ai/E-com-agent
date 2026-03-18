import logging
import time
from typing import Any

import anyio
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from agent.main_agent import run_agent
from agent.settings import settings


logger = logging.getLogger("ecommerce_agent_api")
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))


class ChatRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    response: str
    latency_ms: int


app = FastAPI(title="Ecommerce Agent API", version="0.1.0")


@app.get("/", response_class=HTMLResponse)
async def index(_: Request) -> HTMLResponse:
    return HTMLResponse(
        content="<html><body><h1>Ecommerce Agent API</h1><p>Service is running.</p></body></html>"
    )


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz")
async def readyz() -> dict[str, str]:
    try:
        settings.validate_for_startup()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"status": "ready"}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    started = time.perf_counter()
    try:
        # ADK agent `run` is sync; run in a worker thread.
        response: Any = await anyio.to_thread.run_sync(run_agent, req.query)
        text = str(response)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Chat request failed")
        raise HTTPException(status_code=500, detail="Agent error") from exc

    latency_ms = int((time.perf_counter() - started) * 1000)
    return ChatResponse(response=text, latency_ms=latency_ms)

