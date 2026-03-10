import json
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from app.middleware.rate_limit import limiter
from langchain_core.messages import HumanMessage
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents import get_agent
from app.agents.state import AgentState
from app.config import get_settings
from app.dependencies import get_current_user, get_db
from app.models.assistant import Assistant
from app.models.chat_session import ChatSession
from app.models.message import Message
from app.models.workspace import Workspace
from app.schemas.chat import ChatRequest, SessionCreate, SessionOut

router = APIRouter(prefix="/sessions", tags=["chat"])
settings = get_settings()


async def _get_or_create_workspace(user_id: str, db: AsyncSession) -> Workspace:
    result = await db.execute(
        select(Workspace).where(Workspace.owner_id == user_id).limit(1)
    )
    workspace = result.scalar_one_or_none()
    if not workspace:
        workspace = Workspace(name="Default Workspace", owner_id=user_id)
        db.add(workspace)
        await db.flush()
    return workspace


@router.get("", response_model=list[SessionOut])
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> list[ChatSession]:
    result = await db.execute(
        select(ChatSession)
        .where(
            ChatSession.user_id == current_user["user_id"],
            ChatSession.is_deleted == False,  # noqa: E712
        )
        .order_by(ChatSession.updated_at.desc())
        .limit(100)
    )
    return list(result.scalars().all())


@router.post("", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
async def create_session(
    body: SessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> ChatSession:
    workspace = await _get_or_create_workspace(current_user["user_id"], db)
    session = ChatSession(
        workspace_id=workspace.id,
        user_id=current_user["user_id"],
        **body.model_dump(),
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> None:
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user["user_id"],
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session.is_deleted = True
    await db.commit()


@router.post("/{session_id}/chat")
@limiter.limit("60/minute")
async def chat_stream(
    request: Request,
    session_id: uuid.UUID,
    body: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> StreamingResponse:
    # Load session
    session_result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user["user_id"],
            ChatSession.is_deleted == False,  # noqa: E712
        )
    )
    session = session_result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Load assistant config
    assistant_result = await db.execute(
        select(Assistant).where(Assistant.id == session.assistant_id)
    ) if session.assistant_id else None
    assistant = assistant_result.scalar_one_or_none() if assistant_result else None

    provider = body.provider or session.provider
    model = body.model or session.model

    graph_type = assistant.graph_type if assistant else "chat"
    system_prompt = assistant.system_prompt if assistant else ""

    # Load recent history (last 20 messages)
    history_result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at.desc())
        .limit(20)
    )
    history = list(reversed(history_result.scalars().all()))

    # Persist user message
    user_msg = Message(
        session_id=session_id, role="user", content=body.content
    )
    db.add(user_msg)
    await db.commit()

    # Build LangGraph state
    from langchain_core.messages import AIMessage
    lc_messages = []
    for m in history:
        if m.role == "user":
            lc_messages.append(HumanMessage(content=m.content))
        elif m.role == "assistant":
            lc_messages.append(AIMessage(content=m.content))
    lc_messages.append(HumanMessage(content=body.content))

    agent_state: AgentState = {
        "messages": lc_messages,
        "context": [],
        "session_id": str(session_id),
        "user_id": current_user["user_id"],
        "workspace_id": str(session.workspace_id),
        "provider": provider,
        "model": model,
        "system_prompt": system_prompt,
    }

    async def event_stream():
        full_response = []
        try:
            print(f"Starting agent: {graph_type}")
            agent = get_agent(graph_type)
            async for event in agent.astream_events(agent_state, version="v2"):
                if event["event"] == "on_chat_model_stream":
                    chunk_content = event["data"]["chunk"].content
                    if chunk_content:
                        # print(f"Token: {chunk_content}")  # high volume
                        full_response.append(chunk_content)
                        yield f"data: {json.dumps({'type': 'token', 'content': chunk_content})}\n\n"
                elif event["event"] == "on_tool_start":
                    yield f"data: {json.dumps({'type': 'tool_start', 'tool': event['name']})}\n\n"
                elif event["event"] == "on_tool_end":
                    yield f"data: {json.dumps({'type': 'tool_end', 'tool': event['name']})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
        finally:
            # Persist assistant response
            if full_response:
                async with AsyncSession(db.bind) as persist_session:
                    assistant_msg = Message(
                        session_id=session_id,
                        role="assistant",
                        content="".join(full_response),
                    )
                    persist_session.add(assistant_msg)
                    # Auto-title session from first exchange
                    if session.title == "New Chat":
                        title = body.content[:80].strip()
                        result = await persist_session.execute(
                            select(ChatSession).where(ChatSession.id == session_id)
                        )
                        s = result.scalar_one_or_none()
                        if s:
                            s.title = title
                    await persist_session.commit()

            yield f"data: {json.dumps({'type': 'done', 'session_id': str(session_id)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
