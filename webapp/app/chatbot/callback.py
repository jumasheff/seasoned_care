"""Callback handlers used in the app."""
from typing import Any, Dict, List
import json

from langchain.callbacks.base import AsyncCallbackHandler

from .schemas import ChatResponse


class StreamingLLMCallbackHandler(AsyncCallbackHandler):
    """Callback handler for streaming LLM responses."""

    def __init__(self, consumer):
        self.consumer = consumer

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        resp = ChatResponse(username="bot", message=token, type="stream")
        await self.consumer.send(text_data=json.dumps(resp.dict()))


class QuestionGenCallbackHandler(AsyncCallbackHandler):
    """Callback handler for question generation."""

    def __init__(self, consumer):
        self.consumer = consumer

    async def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Run when LLM starts running."""
        resp = ChatResponse(
            username="bot", message="Synthesizing question...", type="info"
        )
        await self.consumer.send(text_data=json.dumps(resp.dict()))
