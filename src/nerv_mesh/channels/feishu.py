"""Feishu bot channel — receives messages via webhook, replies via API."""

import json
import logging

import lark_oapi as lark
from lark_oapi.api.im.v1 import (
    CreateMessageRequest,
    CreateMessageRequestBody,
    P2ImMessageReceiveV1,
    ReplyMessageRequest,
    ReplyMessageRequestBody,
)

from nerv_mesh.config.models import FeishuConfig

logger = logging.getLogger(__name__)


class FeishuBot:
    """Manages Feishu client, event dispatch, and message replies."""

    def __init__(self, config: FeishuConfig):
        self.client = self._build_client(config)
        self.event_handler = self._build_event_handler(config)
        self._on_message_callback = None

    def on_message(self, callback):
        """Register a callback: async def callback(chat_id, user_id, text) -> str."""
        self._on_message_callback = callback
        return callback

    def get_event_handler(self) -> lark.EventDispatcherHandler:
        return self.event_handler

    async def reply_text(self, message_id: str, text: str) -> None:
        """Reply to a specific message with plain text."""
        body = ReplyMessageRequestBody.builder() \
            .msg_type("text") \
            .content(json.dumps({"text": text})) \
            .build()
        req = ReplyMessageRequest.builder() \
            .message_id(message_id) \
            .request_body(body) \
            .build()
        resp = self.client.im.v1.message.reply(req)
        if not resp.success():
            logger.error("Feishu reply failed: %s %s", resp.code, resp.msg)

    async def send_text(self, chat_id: str, text: str) -> None:
        """Send a message to a chat (group or direct)."""
        body = CreateMessageRequestBody.builder() \
            .msg_type("text") \
            .receive_id(chat_id) \
            .content(json.dumps({"text": text})) \
            .build()
        req = CreateMessageRequest.builder() \
            .receive_id_type("chat_id") \
            .request_body(body) \
            .build()
        resp = self.client.im.v1.message.create(req)
        if not resp.success():
            logger.error("Feishu send failed: %s %s", resp.code, resp.msg)

    # ── Private ───────────────────────────────────────────────────────────

    def _build_client(self, config: FeishuConfig) -> lark.Client:
        return lark.Client.builder() \
            .app_id(config.app_id) \
            .app_secret(config.app_secret) \
            .build()

    def _build_event_handler(self, config: FeishuConfig) -> lark.EventDispatcherHandler:
        return lark.EventDispatcherHandler.builder(
            config.encrypt_key,
            config.verification_token,
        ).register_p2_im_message_receive_v1(
            self._handle_message_event,
        ).build()

    def _handle_message_event(self, data: P2ImMessageReceiveV1) -> None:
        """Dispatch incoming message to registered callback."""
        if not self._on_message_callback:
            logger.warning("No message callback registered, ignoring event")
            return

        msg = data.event.message
        sender = data.event.sender
        text = self._extract_text(msg.content)

        logger.info("Feishu message from %s: %s", sender.sender_id.user_id, text[:50])

        import asyncio
        asyncio.create_task(
            self._dispatch(msg.message_id, msg.chat_id, sender.sender_id.user_id, text)
        )

    async def _dispatch(
        self, message_id: str, chat_id: str, user_id: str, text: str
    ) -> None:
        """Call the registered callback and reply."""
        try:
            response = await self._on_message_callback(chat_id, user_id, text)
            await self.reply_text(message_id, response)
        except Exception:
            logger.exception("Error processing Feishu message")
            await self.reply_text(message_id, "Processing error, please try again.")

    def _extract_text(self, content: str) -> str:
        """Extract plain text from Feishu message content JSON."""
        try:
            parsed = json.loads(content)
            return parsed.get("text", content)
        except (json.JSONDecodeError, TypeError):
            return content
