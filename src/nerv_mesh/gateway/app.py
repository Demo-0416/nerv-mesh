"""FastAPI application factory for the nerv-mesh gateway."""

import json
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessageChunk, HumanMessage
from pydantic import BaseModel

from nerv_mesh.config.models import AppConfig

from .deps import Runtime, create_runtime

_runtime: Runtime | None = None


def create_app(config: AppConfig) -> FastAPI:
    """Build a FastAPI app wired to the agent runtime."""

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        global _runtime  # noqa: PLW0603
        _runtime = create_runtime(config)
        _mount_feishu(_app, _runtime)
        yield
        _runtime = None

    app = FastAPI(title="nerv-mesh Gateway", version="0.1.0", lifespan=lifespan)
    _register_routes(app)
    return app


def _mount_feishu(app: FastAPI, rt: Runtime) -> None:
    """Conditionally attach Feishu webhook route."""
    from .feishu_route import setup_feishu

    feishu_router = setup_feishu(rt)
    if feishu_router:
        app.include_router(feishu_router)


# ── Request / Response schemas ────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None


# ── Route registration ────────────────────────────────────────────────────

def _register_routes(app: FastAPI) -> None:
    app.add_api_route("/api/chat", _chat, methods=["POST"])
    app.add_api_route("/api/chat/stream", _chat_stream, methods=["POST"])
    app.add_api_route("/api/skills", _list_skills, methods=["GET"])
    app.add_api_route("/api/config/models", _list_models, methods=["GET"])
    app.add_api_route("/api/health", _health, methods=["GET"])


# ── Handlers ──────────────────────────────────────────────────────────────

async def _health():
    return {"status": "ok"}


async def _list_models():
    assert _runtime
    return {
        name: {"model": m.model, "provider": m.provider}
        for name, m in _runtime.config.models.items()
    }


async def _list_skills():
    assert _runtime
    return _runtime.skills.list_skills()


async def _chat(req: ChatRequest):
    """Non-streaming chat: returns full response."""
    assert _runtime
    thread_id = req.thread_id or str(uuid.uuid4())
    result = await _runtime.agent.ainvoke(
        {"messages": [HumanMessage(content=req.message)]},
        config={"configurable": {"thread_id": thread_id}},
    )
    last = result["messages"][-1]
    return {"thread_id": thread_id, "response": last.content}


async def _chat_stream(req: ChatRequest):
    """SSE streaming chat."""
    assert _runtime
    thread_id = req.thread_id or str(uuid.uuid4())

    async def event_generator():
        async for event in _runtime.agent.astream_events(
            {"messages": [HumanMessage(content=req.message)]},
            config={"configurable": {"thread_id": thread_id}},
            version="v2",
        ):
            chunk = _format_sse_event(event)
            if chunk:
                yield chunk
        yield f"data: {json.dumps({'type': 'done', 'thread_id': thread_id})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


def _format_sse_event(event: dict) -> str | None:
    """Convert a LangGraph stream event to an SSE data line."""
    kind = event["event"]

    if kind == "on_chat_model_stream":
        chunk = event["data"].get("chunk")
        if isinstance(chunk, AIMessageChunk) and chunk.content:
            payload = {"type": "token", "content": chunk.content}
            return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

    elif kind == "on_tool_start":
        payload = {"type": "tool_start", "name": event.get("name", "")}
        return f"data: {json.dumps(payload)}\n\n"

    elif kind == "on_tool_end":
        output = str(event["data"].get("output", ""))
        payload = {"type": "tool_end", "output": output[:500]}
        return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

    return None
