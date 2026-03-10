"""
explore_agents.py
-----------------
Router: GET /api/v1/explore-agents

Returns a rich catalogue of all available agents with metadata, categories,
capabilities, and configuration status — powering the frontend Explore Agents
(Discover) page.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.assistant import Assistant

router = APIRouter(prefix="/explore-agents", tags=["explore-agents"])

# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

class AgentCapability(BaseModel):
    label: str
    description: str


class ExploreAgentOut(BaseModel):
    id: str
    name: str
    description: str
    graph_type: str
    icon: str
    category: str
    category_label: str
    capabilities: list[str]
    status: str          # "available" | "coming_soon"
    badge: str | None    # Optional badge text e.g. "NEW", "LIVE", "BETA"

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Static metadata enrichment for each graph_type
# ---------------------------------------------------------------------------

_AGENT_META: dict[str, dict] = {
    # ── Core platform agents ────────────────────────────────────────────────
    "chat": {
        "category": "general",
        "category_label": "General",
        "capabilities": [
            "Conversational AI with tool use",
            "Web search via DuckDuckGo / Tavily",
            "Python code execution",
            "Multi-turn memory within session",
        ],
        "status": "available",
        "badge": None,
    },
    "rag": {
        "category": "general",
        "category_label": "General",
        "capabilities": [
            "Answer questions from your documents",
            "Semantic search over uploaded files",
            "PDF, Word, and text file support",
            "Source-grounded responses",
        ],
        "status": "available",
        "badge": None,
    },
    "code_reviewer": {
        "category": "general",
        "category_label": "General",
        "capabilities": [
            "Bug detection and code analysis",
            "Security vulnerability scanning",
            "Best-practice recommendations",
            "Refactoring suggestions with examples",
        ],
        "status": "available",
        "badge": None,
    },
    "copywriter": {
        "category": "general",
        "category_label": "General",
        "capabilities": [
            "Marketing copy and ad creatives",
            "Email campaigns and newsletters",
            "Product descriptions",
            "Brand-voice-consistent writing",
        ],
        "status": "available",
        "badge": None,
    },
    # ── Operational agents ──────────────────────────────────────────────────
    "logistics_monitor": {
        "category": "logistics",
        "category_label": "Logistics",
        "capabilities": [
            "Monitor Shopify orders (open, held, unfulfilled)",
            "Detect delayed and stuck shipments",
            "Track fulfillment partner shipment status",
            "Check courier account balance with low-balance alerts",
            "Flag shipping cost anomalies (Z-score analysis)",
            "Generate daily & weekly logistics reports",
        ],
        "status": "available",
        "badge": "NEW",
    },
    "finance_monitor": {
        "category": "finance",
        "category_label": "Finance",
        "capabilities": [
            "Scan inbox for invoices and extract structured data",
            "Track expenses and populate expense records",
            "Detect spending anomalies vs. 90-day baseline",
            "Monitor cash flow position (income vs. outgoings)",
            "Generate weekly finance digest reports",
        ],
        "status": "available",
        "badge": "NEW",
    },
    "email_manager": {
        "category": "email",
        "category_label": "Email",
        "capabilities": [
            "Monitor inbox for unread messages",
            "Classify emails: invoice, logistics, supplier, complaint, spam",
            "Priority-rank messages (1–5 scale)",
            "Surface urgent operational emails requiring action",
            "Generate categorised inbox digest",
        ],
        "status": "available",
        "badge": "NEW",
    },
    "customer_issue_monitor": {
        "category": "customer",
        "category_label": "Customer Experience",
        "capabilities": [
            "Monitor customer support inbox",
            "Classify issues: lost parcel, refund, wrong item, delay",
            "Flag critical issues with SLA targets",
            "Detect refund patterns by SKU, courier, and region",
            "Generate daily CX team briefings",
        ],
        "status": "available",
        "badge": "NEW",
    },
    "operations_dashboard": {
        "category": "operations",
        "category_label": "Operations",
        "capabilities": [
            "Generate daily operations summary (logistics + CX)",
            "Generate weekly founder / executive report",
            "Cross-domain KPI synthesis and trend analysis",
            "Deliver reports to Slack channels via webhook",
            "Send reports via email (SMTP)",
        ],
        "status": "available",
        "badge": "NEW",
    },
}

_DEFAULT_META: dict = {
    "category": "general",
    "category_label": "General",
    "capabilities": ["AI-powered assistant"],
    "status": "available",
    "badge": None,
}


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.get("", response_model=list[ExploreAgentOut])
async def list_explore_agents(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> list[ExploreAgentOut]:
    """Return all agents enriched with category, capabilities, and status metadata."""
    stmt = (
        select(Assistant)
        .where(Assistant.is_default == True)
        .order_by(Assistant.name.asc())
    )
    result = await db.execute(stmt)
    assistants = list(result.scalars().all())

    enriched: list[ExploreAgentOut] = []
    for a in assistants:
        meta = _AGENT_META.get(a.graph_type, _DEFAULT_META)
        enriched.append(
            ExploreAgentOut(
                id=str(a.id),
                name=a.name,
                description=a.description,
                graph_type=a.graph_type,
                icon=a.icon,
                category=meta["category"],
                category_label=meta["category_label"],
                capabilities=meta["capabilities"],
                status=meta["status"],
                badge=meta.get("badge"),
            )
        )
    return enriched
