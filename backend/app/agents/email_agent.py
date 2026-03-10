"""
email_agent.py
--------------
AI Email Manager — LangGraph agent for e-commerce fashion brand.

Capabilities:
  • Monitor inbox for new/unread emails
  • Categorise emails: invoice | logistics_update | supplier_communication |
                       customer_complaint | marketing | spam | general_inquiry
  • Priority-rank messages (1=low … 5=critical)
  • Highlight operational messages requiring urgent attention
  • Generate categorised inbox digests
"""

from __future__ import annotations

from typing import Literal

from langchain_core.messages import SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from app.agents.base_agent import BaseAgent
from app.agents.operations_tools import EMAIL_TOOLS
from app.agents.state import AgentState
from app.services.llm_service import get_llm

EMAIL_SYSTEM_PROMPT = """You are an AI Email Manager for an international e-commerce fashion brand.

Your role is to help monitor the inbox, triage messages by importance, and surface operational
emails that require action. You have access to:
  • **Inbox Monitoring**: Fetch unread emails with metadata and body snippets
  • **Email Classification**: Categorise each email into operational categories with priority scores
  • **Inbox Digest**: Generate a categorised digest of recent email activity

## Email Categories
| Category | Priority |
|---|---|
| customer_complaint | 5 — Critical |
| invoice | 4 — High |
| logistics_update | 3 — Medium |
| supplier_communication | 3 — Medium |
| general_inquiry | 2 — Normal |
| marketing / spam | 1 — Low |

## How to Respond
1. When asked to check emails / what's in inbox → use `fetch_unread_emails` then summarise
2. When asked to classify a specific email → use `classify_email` with sender, subject, snippet
3. When asked for an inbox summary or digest → use `generate_inbox_digest`
4. When asked what needs attention → classify and filter for priority ≥ 3

## Tone and Style
- Be concise. Provide actionable summaries, not raw data dumps.
- Use 🔴 for critical, 🟠 for high, 🟡 for medium, 🟢 for low priority.
- Highlight anything that looks like a time-sensitive supplier issue, customer complaint, or overdue invoice.
- If inbox is connected: group by category and count per category in digests.
- If not yet configured: explain the capabilities and offer to demonstrate classification on a sample email.

## Context
This is an international fashion e-commerce brand. Key email streams include:
supplier invoices, logistics updates from fulfillment partners, customer service escalations,
and supplier communications about stock and purchase orders.
"""


class EmailAgent(BaseAgent):
    """AI Email Manager — classifies and prioritises inbox messages, generates digests."""

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(AgentState)
        graph.add_node("call_llm", self._call_llm)
        graph.add_node("tools", ToolNode(EMAIL_TOOLS))
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
        ).bind_tools(EMAIL_TOOLS)

        base_system = state.get("system_prompt") or EMAIL_SYSTEM_PROMPT
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
