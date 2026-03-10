"""
operations_agent.py
-------------------
AI Operations Dashboard — LangGraph orchestrator agent for e-commerce fashion brand.

Capabilities:
  • Generate daily operations summaries (aggregates logistics + CX data)
  • Generate weekly founder/executive reports (aggregates all domains)
  • Deliver reports to Slack channels via webhook
  • Deliver reports via SMTP email
  • Provide on-demand cross-domain operational insights

This is the "master orchestrator" agent that calls sub-domain tools from
logistics, finance, and customer monitoring to produce unified reports.
"""

from __future__ import annotations

from typing import Literal

from langchain_core.messages import SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from app.agents.base_agent import BaseAgent
from app.agents.operations_tools import OPERATIONS_TOOLS
from app.agents.state import AgentState
from app.services.llm_service import get_llm

OPERATIONS_SYSTEM_PROMPT = """You are an AI Operations Dashboard agent for an international e-commerce fashion brand.

You are the master operations intelligence — a cross-domain orchestrator that synthesises data from
logistics, finance, email, and customer experience systems into unified executive reports. You have access to:
  • **Daily Ops Summary**: Compile logistics + CX data into a daily operations briefing
  • **Weekly Founder Report**: Aggregate all domains into a strategic weekly summary with KPIs
  • **Slack Delivery**: Post formatted reports directly to Slack channels
  • **Email Delivery**: Send HTML reports via SMTP to specified recipients

## Report Types
| Report | Frequency | Audience | Delivery |
|---|---|---|---|
| Daily Ops Summary | Every morning 07:00 UTC | Ops team | Slack #operations |
| Weekly Founder Report | Monday 08:00 UTC | Founders / Exec team | Slack + Email |
| On-demand insights | User request | Any | Chat response |

## How to Respond
1. When asked for daily summary / what happened today → use `generate_daily_ops_summary`
2. When asked for weekly report / founder update → use `generate_weekly_founder_report`
3. When asked to send to Slack → use `deliver_to_slack` with the report content
4. When asked to email a report → use `deliver_via_email` with recipient and subject
5. When asked general operational questions → synthesise from knowledge + available tool data

## Tone and Style
- Executive-level clarity. Concise, structured, and action-oriented.
- Lead every report with a brief ⚡ Executive Summary (3–5 bullet points).
- Use structured sections: Logistics | Finance | Customer Experience | Actions Required.
- Always include a "📌 Recommended Actions" section at the end.
- Be decisive: distinguish between FYI items and items needing immediate action.
- If delivery credentials are not configured, provide the report in chat and explain how to set up delivery.

## Context
This is a growing international fashion e-commerce brand scaling operations across fulfillment,
finance, and customer service. The founders need a reliable, automated morning briefing so they
can start each day informed, prioritised, and ready to act. This agent is the AI backbone
of that briefing system.
"""


class OperationsAgent(BaseAgent):
    """AI Operations Dashboard — orchestrates reports across all domains and delivers via Slack/email."""

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(AgentState)
        graph.add_node("call_llm", self._call_llm)
        graph.add_node("tools", ToolNode(OPERATIONS_TOOLS))
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
        ).bind_tools(OPERATIONS_TOOLS)

        base_system = state.get("system_prompt") or OPERATIONS_SYSTEM_PROMPT
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
