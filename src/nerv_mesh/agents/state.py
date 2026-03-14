"""Agent state definitions for LangGraph."""

from typing import Annotated

from langgraph.graph import MessagesState
from langgraph.managed import IsLastStep


class ThreadState(MessagesState):
    """Extended state carried through the agent graph.

    Inherits `messages` from MessagesState.
    Additional fields for nerv-mesh orchestration.
    """

    thread_id: str = ""
    is_last_step: Annotated[bool, IsLastStep] = False
