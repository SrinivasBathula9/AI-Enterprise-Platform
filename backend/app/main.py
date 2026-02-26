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
from app.routers import assistants, chat, documents, health, messages
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
app.include_router(chat.router, prefix="/api/v1")
app.include_router(messages.router, prefix="/api/v1")
app.include_router(assistants.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
