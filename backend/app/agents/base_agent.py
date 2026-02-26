from abc import ABC, abstractmethod
from typing import AsyncIterator

from langgraph.graph import StateGraph

from app.agents.state import AgentState


class BaseAgent(ABC):
    """Abstract base for all LangGraph agents."""

    def __init__(self) -> None:
        self._graph = self._build_graph()

    @abstractmethod
    def _build_graph(self) -> StateGraph:
        ...

    async def astream_events(
        self, state: AgentState, version: str = "v2"
    ) -> AsyncIterator[dict]:
        async for event in self._graph.astream_events(state, version=version):
            yield event

    async def ainvoke(self, state: AgentState) -> AgentState:
        return await self._graph.ainvoke(state)
