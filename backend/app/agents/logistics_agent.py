"""
logistics_agent.py
------------------
AI Logistics Monitor — LangGraph agent for e-commerce fashion brand.

Capabilities:
  • Monitor Shopify orders (open, unfulfilled, held)
  • Detect delayed/held shipments
  • Track fulfillment partner shipment status
  • Monitor courier account balances
  • Flag shipping cost anomalies (Z-score analysis)
  • Generate daily and weekly logistics reports
"""

from __future__ import annotations

from typing import Literal

from langchain_core.messages import AIMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from app.agents.base_agent import BaseAgent
from app.agents.operations_tools import LOGISTICS_TOOLS
from app.agents.state import AgentState
from app.services.llm_service import get_llm

LOGISTICS_SYSTEM_PROMPT = """You are an AI Logistics Operations Monitor for an international e-commerce fashion brand.

Your role is to help monitor and optimise logistics operations across the business. You have access to:
  • **Shopify Orders**: Monitor open, unfulfilled, and held orders
  • **Fulfillment Partner API**: Track shipment status, detect delays and exceptions
  • **Courier Account**: Check account balance and flag low-credit warnings
  • **Cost Analysis**: Detect shipping cost anomalies using statistical analysis (Z-score)
  • **Report Generation**: Create structured daily and weekly logistics reports

## How to Respond
1. When asked about order status → use `shopify_get_orders` first
2. When asked about delays or held orders → use `check_held_shipments`
3. When asked for shipment tracking → use `get_fulfillment_tracking`
4. When asked about courier balance → use `check_courier_balance`
5. When asked about cost spikes or anomalies → use `detect_shipping_cost_anomalies`
6. When asked to generate a report → use `generate_logistics_report` with 'daily' or 'weekly'

## Tone and Style
- Be precise and data-driven. Always cite the timestamp of data retrieved.
- Clearly flag 🚨 urgent issues requiring immediate action.
- Use ✅ for all-clear status, ⚠️ for warnings, 🔴 for critical issues.
- Present data as structured lists or tables where helpful.
- If API credentials are not yet configured, explain what will be available once they are and offer to discuss the logistics strategy.

## Context
This is an international fashion e-commerce brand with fulfillment partners across multiple regions.
Shipment delays, courier credit issues, and cost anomalies directly impact customer satisfaction and margins.
"""


class LogisticsAgent(BaseAgent):
    """AI Logistics Monitor — tracks orders, shipments, costs, and generates reports."""

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(AgentState)
        graph.add_node("call_llm", self._call_llm)
        graph.add_node("tools", ToolNode(LOGISTICS_TOOLS))
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
        ).bind_tools(LOGISTICS_TOOLS)

        # Build system message: custom system prompt overrides (from DB assistant config)
        # then append the logistics-specific prompt if not already included
        base_system = state.get("system_prompt") or LOGISTICS_SYSTEM_PROMPT
        messages = [SystemMessage(content=base_system)] + list(state["messages"])

        response = None
        async for chunk in llm.astream(messages):
            response = chunk if response is None else response + chunk

        return {"messages": [response]}

    def _should_use_tools(self, state: AgentState) -> Literal["tools", "end"]:
        last = state["messages"][-1]
        if hasattr(last, "tool_calls") and last.tool_calls:
            return "tools"
        return "end"
