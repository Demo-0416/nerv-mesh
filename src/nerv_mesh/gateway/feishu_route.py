"""Feishu webhook route — mounted onto the gateway."""

import logging
import uuid

import lark_oapi as lark
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from langchain_core.messages import HumanMessage

from nerv_mesh.channels.feishu import FeishuBot
from nerv_mesh.config.models import FeishuConfig

from .deps import Runtime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/feishu")


def setup_feishu(rt: Runtime) -> APIRouter | None:
    """Wire up the Feishu bot to the agent and return the router.

    Returns None if Feishu is not configured (no app_id).
    """
    cfg: FeishuConfig = rt.config.feishu
    if not cfg.app_id:
        logger.info("Feishu not configured, skipping webhook route")
        return None

    bot = FeishuBot(cfg)

    @bot.on_message
    async def handle(chat_id: str, user_id: str, text: str) -> str:
        thread_id = f"feishu-{chat_id}-{uuid.uuid4().hex[:8]}"
        result = await rt.agent.ainvoke(
            {"messages": [HumanMessage(content=text)]},
            config={"configurable": {"thread_id": thread_id}},
        )
        return result["messages"][-1].content

    handler = bot.get_event_handler()

    @router.post("/webhook")
    async def feishu_webhook(request: Request):
        body = await request.body()
        raw = lark.RawRequest(uri=str(request.url), body=body, headers=dict(request.headers))
        resp = handler.do(raw)
        return JSONResponse(
            content=resp.to_dict() if hasattr(resp, "to_dict") else {"msg": "ok"},
            status_code=resp.status_code if hasattr(resp, "status_code") else 200,
        )

    return router
