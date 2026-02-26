from typing import Literal

from langchain_core.messages import AIMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from app.agents.base_agent import BaseAgent
from app.agents.state import AgentState
from app.agents.tools import ALL_TOOLS
from app.services.llm_service import get_llm


class ChatAgent(BaseAgent):
    """General-purpose chat agent with optional tool use."""

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(AgentState)
        graph.add_node("call_llm", self._call_llm)
        graph.add_node("tools", ToolNode(ALL_TOOLS))
        graph.add_edge(START, "call_llm")
        graph.add_conditional_edges(
            "call_llm",
            self._should_use_tools,
            {"tools": "tools", "end": END},
        )
        graph.add_edge("tools", "call_llm")
        return graph.compile()

    async def _call_llm(self, state: AgentState) -> dict:
        llm = get_llm(
            provider=state.get("provider"),
            model=state.get("model"),
            streaming=True,
        ).bind_tools(ALL_TOOLS)

        messages = list(state["messages"])
        if state.get("system_prompt"):
            messages = [SystemMessage(content=state["system_prompt"])] + messages

        # Use astream to ensure on_chat_model_stream events are triggered
        response = None
        async for chunk in llm.astream(messages):
            if response is None:
                response = chunk
            else:
                response += chunk

        return {"messages": [response]}

    def _should_use_tools(self, state: AgentState) -> Literal["tools", "end"]:
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return "end"
