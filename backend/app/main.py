import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import get_settings
from app.middleware.rate_limit import limiter
from app.models.assistant import Assistant
from app.models.workspace import Workspace
from app.routers import assistants, chat, documents, explore_agents, health, messages
from app.routers.auth import router as auth_router
from app.services.qdrant_service import ensure_collections, get_qdrant_client

settings = get_settings()

DEFAULT_ASSISTANTS = [
    {
        "name": "General Assistant",
        "description": "A versatile AI assistant for everyday tasks.",
        "system_prompt": "You are a helpful, knowledgeable AI assistant.",
        "graph_type": "chat",
        "icon": "bot",
    },
    {
        "name": "Document Analyst",
        "description": "Answers questions using your uploaded documents.",
        "system_prompt": "You are a precise document analyst. Answer questions based on provided context.",
        "graph_type": "rag",
        "icon": "file-text",
    },
    {
        "name": "Code Reviewer",
        "description": "Reviews code, finds bugs, and suggests improvements.",
        "system_prompt": (
            "You are an expert software engineer and code reviewer. "
            "Analyze code thoroughly for bugs, security issues, and improvements. "
            "Provide clear, actionable feedback with examples."
        ),
        "graph_type": "code_reviewer",
        "icon": "code",
    },
    {
        "name": "Copywriter",
        "description": "Crafts compelling content, emails, and marketing copy.",
        "system_prompt": (
            "You are an expert copywriter with a flair for persuasive, engaging content. "
            "Write clearly, concisely, and with the user's audience in mind."
        ),
        "graph_type": "copywriter",
        "icon": "pen-line",
    },
    # ── Operational AI Agents — E-Commerce Fashion Brand ──────────────────────
    {
        "name": "AI Logistics Monitor",
        "description": (
            "Monitors Shopify orders, detects held and delayed shipments, tracks fulfillment "
            "partner status, checks courier account balances, flags shipping cost anomalies, "
            "and generates daily and weekly logistics reports."
        ),
        "system_prompt": (
            "You are an AI Logistics Operations Monitor for an international e-commerce fashion brand. "
            "You have access to Shopify orders, fulfillment partner shipment tracking, courier account "
            "balances, and shipping cost analysis. Detect anomalies, surface held shipments, flag cost "
            "spikes, and generate clear operational reports. Always cite data sources and timestamps."
        ),
        "graph_type": "logistics_monitor",
        "icon": "truck",
    },
    {
        "name": "AI Finance Monitor",
        "description": (
            "Extracts invoice data from email, tracks expenses, detects unusual spending anomalies "
            "against historical baselines, monitors cash flow position, and generates weekly finance summaries."
        ),
        "system_prompt": (
            "You are an AI Finance Monitor for an international e-commerce fashion brand. "
            "Help automate finance tracking by extracting invoices from email, recording expenses, "
            "detecting spending anomalies vs. baseline, and generating weekly finance digest reports. "
            "Be precise with numbers and always include currency and period context."
        ),
        "graph_type": "finance_monitor",
        "icon": "bar-chart-2",
    },
    {
        "name": "AI Email Manager",
        "description": (
            "Monitors the inbox, categorises and priority-ranks messages, highlights urgent operational "
            "issues, identifies invoices, logistics updates, and supplier communications, and generates "
            "a categorised inbox digest."
        ),
        "system_prompt": (
            "You are an AI Email Manager for an international e-commerce fashion brand. "
            "Monitor the inbox, classify emails into operational categories (invoice, logistics, supplier, "
            "complaint, marketing), priority-rank them 1–5, and surface messages requiring urgent attention. "
            "Generate concise, categorised inbox digests."
        ),
        "graph_type": "email_manager",
        "icon": "mail",
    },
    {
        "name": "AI Customer Issue Monitor",
        "description": (
            "Monitors customer support channels, identifies shipping complaints, lost parcel reports, "
            "and refund requests, flags urgent issues with SLA targets, detects refund patterns by SKU "
            "and courier, and generates daily CX team briefings."
        ),
        "system_prompt": (
            "You are an AI Customer Issue Monitor for an international e-commerce fashion brand. "
            "Triage support tickets, classify issue types (lost parcel, refund, wrong item, delay), "
            "assign urgency levels with SLA targets, detect refund patterns, and generate daily "
            "CX team briefings. Lead with urgency — surface the most critical issues first."
        ),
        "graph_type": "customer_issue_monitor",
        "icon": "headphones",
    },
    {
        "name": "AI Operations Dashboard",
        "description": (
            "Generates comprehensive daily operations summaries and weekly founder reports by aggregating "
            "data across logistics, finance, and customer experience. Delivers reports via Slack webhooks "
            "and email. The master operational intelligence hub."
        ),
        "system_prompt": (
            "You are an AI Operations Dashboard agent for an international e-commerce fashion brand. "
            "Synthesise data from logistics, finance, and customer experience into unified executive reports. "
            "Generate daily ops summaries and weekly founder reports. Deliver via Slack and email. "
            "Be executive-level concise — lead every report with a 3–5 bullet executive summary."
        ),
        "graph_type": "operations_dashboard",
        "icon": "layout-dashboard",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure Qdrant collections exist
    client = get_qdrant_client()
    ensure_collections(client)

    # Seed default assistants into a system workspace
    from app.database import AsyncSessionLocal
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        system_user_id = "system"
        result = await db.execute(
            select(Workspace).where(Workspace.owner_id == system_user_id).limit(1)
        )
        workspace = result.scalar_one_or_none()
        if not workspace:
            workspace = Workspace(name="System", owner_id=system_user_id)
            db.add(workspace)
            await db.flush()

        for data in DEFAULT_ASSISTANTS:
            exists = await db.execute(
                select(Assistant).where(
                    Assistant.workspace_id == workspace.id,
                    Assistant.name == data["name"],
                )
            )
            if not exists.scalar_one_or_none():
                assistant = Assistant(
                    workspace_id=workspace.id,
                    is_default=True,
                    **data,
                )
                db.add(assistant)

        await db.commit()

    yield


app = FastAPI(
    title="AI Enterprise Platform",
    description="Multi-provider AI chat platform with RAG and LangGraph agents.",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth_router)
app.include_router(chat.router, prefix="/api/v1")
app.include_router(messages.router, prefix="/api/v1")
app.include_router(assistants.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(explore_agents.router, prefix="/api/v1")
