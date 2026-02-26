from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    context: list[str]          # RAG-retrieved text chunks
    session_id: str
    user_id: str
    workspace_id: str
    provider: str
    model: str
    system_prompt: str
