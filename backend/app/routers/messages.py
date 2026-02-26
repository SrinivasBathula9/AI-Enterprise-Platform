import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.chat_session import ChatSession
from app.models.message import Message
from app.schemas.message import MessageListOut, MessageOut

router = APIRouter(prefix="/sessions", tags=["messages"])


@router.get("/{session_id}/messages", response_model=MessageListOut)
async def get_messages(
    session_id: uuid.UUID,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> MessageListOut:
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

    count_result = await db.execute(
        select(func.count()).where(Message.session_id == session_id)
    )
    total = count_result.scalar_one()

    messages_result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at)
        .offset(offset)
        .limit(limit)
    )
    messages = list(messages_result.scalars().all())

    return MessageListOut(
        messages=[MessageOut.model_validate(m) for m in messages],
        total=total,
    )
