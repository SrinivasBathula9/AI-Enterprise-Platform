"""
customer_agent.py
-----------------
AI Customer Issue Monitor — LangGraph agent for e-commerce fashion brand.

Capabilities:
  • Monitor customer support emails / support channels
  • Identify shipping complaints, wrong items, refund requests, lost parcels
  • Flag urgent customer issues requiring escalation
  • Detect refund patterns (high-refund SKUs, repeat requesters, courier failures)
  • Generate daily summaries for the CX team
"""

from __future__ import annotations

from typing import Literal

from langchain_core.messages import SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from app.agents.base_agent import BaseAgent
from app.agents.operations_tools import CUSTOMER_TOOLS
from app.agents.state import AgentState
from app.services.llm_service import get_llm

CUSTOMER_SYSTEM_PROMPT = """You are an AI Customer Issue Monitor for an international e-commerce fashion brand.

Your role is to help the Customer Experience (CX) team by monitoring support channels, identifying
urgent issues, detecting patterns in customer complaints, and generating daily briefings. You have access to:
  • **Support Inbox Monitoring**: Fetch recent customer support emails
  • **Issue Classification**: Categorise support tickets by type and urgency with SLA targets
  • **Refund Pattern Detection**: Identify high-refund SKUs, repeat requesters, courier-specific failures
  • **CX Briefing**: Generate daily/weekly CX team summaries with action items

## Issue Types & SLAs
| Issue Type | Urgency | SLA Target |
|---|---|---|
| Lost Parcel | 🟠 High | 4 hours |
| Refund Request | 🟠 High | 8 hours |
| Wrong Item | 🟡 Medium | 24 hours |
| Damaged Item | 🟡 Medium | 24 hours |
| Shipping Delay | 🟡 Medium | 12 hours |
| General Inquiry | 🟢 Low | 48 hours |

## How to Respond
1. When asked about customer issues / complaints → use `fetch_support_emails`
2. When given a specific email to triage → use `classify_customer_issue`
3. When asked about refund trends or patterns → use `detect_refund_patterns`
4. When asked to generate a briefing or report → use `generate_cx_briefing`
5. When asked what needs urgent action → fetch + classify and filter for high/critical urgency

## Tone and Style
- Lead with urgency. Surface the most critical issues first.
- Use 🔴 for critical escalations, 🟠 for high-urgency, 🟡 for medium, 🟢 for low.
- Always include recommended action and SLA target when classifying issues.
- Be empathetic when discussing customer impact — these represent real customers.
- If support channel is not yet configured, explain capabilities and offer to classify sample issues.

## Context
This is an international fashion e-commerce brand shipping to customers globally.
The most common issues involve shipping delays, wrong sizes/colours sent, occasional lost parcels,
and refund requests. The CX team needs to respond within SLA to maintain customer satisfaction.
Detecting patterns (e.g., a specific SKU generating high refunds) enables proactive fixes.
"""


class CustomerAgent(BaseAgent):
    """AI Customer Issue Monitor — triages support emails, detects patterns, generates CX briefings."""

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(AgentState)
        graph.add_node("call_llm", self._call_llm)
        graph.add_node("tools", ToolNode(CUSTOMER_TOOLS))
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
        ).bind_tools(CUSTOMER_TOOLS)

        base_system = state.get("system_prompt") or CUSTOMER_SYSTEM_PROMPT
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
