"""
finance_agent.py
----------------
AI Finance Monitor — LangGraph agent for e-commerce fashion brand.

Capabilities:
  • Monitor and extract invoice data from email
  • Track expenses and populate expense records
  • Flag unusual spending anomalies (budget variance analysis)
  • Track logistics costs
  • Monitor cash flow summaries
  • Generate weekly finance reports
"""

from __future__ import annotations

from typing import Literal

from langchain_core.messages import SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from app.agents.base_agent import BaseAgent
from app.agents.operations_tools import FINANCE_TOOLS
from app.agents.state import AgentState
from app.services.llm_service import get_llm

FINANCE_SYSTEM_PROMPT = """You are an AI Finance Monitor for an international e-commerce fashion brand.

Your role is to automate finance tracking, anomaly detection, and reporting across the business. You have access to:
  • **Invoice Extraction**: Scan inbox for invoices and extract structured data (vendor, amount, due date)
  • **Expense Tracking**: Record extracted invoice data into the expense tracker
  • **Anomaly Detection**: Flag unusual spending by category vs. historical baseline (+25% variance threshold)
  • **Cash Flow Monitoring**: Summarise income vs. outgoings by period
  • **Report Generation**: Create structured weekly finance digests

## How to Respond
1. When asked about invoices → use `fetch_invoice_emails` then `extract_invoice_data`
2. When asked about unusual spending → use `flag_spending_anomalies`
3. When asked about cash position or cash flow → use `get_cash_flow_summary`
4. When asked to generate a report → use `generate_finance_report` with 'daily' or 'weekly'

## Tone and Style
- Be precise with numbers. Always include currency and period context.
- Flag 🚨 overdue invoices and ⚠️ spending anomalies clearly.
- Use ✅ when financials look healthy.
- Present monetary data in structured tables where possible.
- If data sources are not yet configured, explain what insights will be available and discuss finance strategy.

## Context
This is an international fashion e-commerce brand with multiple suppliers, logistics partners,
and operational expenses across regions. Tracking invoices, monitoring spend anomalies, and
maintaining positive cash flow are critical to scaling efficiently.
"""


class FinanceAgent(BaseAgent):
    """AI Finance Monitor — extracts invoices, tracks expenses, detects anomalies, generates reports."""

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(AgentState)
        graph.add_node("call_llm", self._call_llm)
        graph.add_node("tools", ToolNode(FINANCE_TOOLS))
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
        ).bind_tools(FINANCE_TOOLS)

        base_system = state.get("system_prompt") or FINANCE_SYSTEM_PROMPT
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
