import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.assistant import Assistant
from app.models.workspace import Workspace
from app.schemas.assistant import AssistantCreate, AssistantOut

router = APIRouter(prefix="/assistants", tags=["assistants"])


async def _get_default_workspace(user_id: str, db: AsyncSession) -> Workspace:
    result = await db.execute(
        select(Workspace).where(Workspace.owner_id == user_id).limit(1)
    )
    workspace = result.scalar_one_or_none()
    if not workspace:
        workspace = Workspace(name="Default Workspace", owner_id=user_id)
        db.add(workspace)
        await db.flush()
    return workspace


@router.get("", response_model=list[AssistantOut])
async def list_assistants(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> list[Assistant]:
    workspace = await _get_default_workspace(current_user["user_id"], db)
    # Get both user-specific and system-wide default assistants
    stmt = (
        select(Assistant)
        .where((Assistant.workspace_id == workspace.id) | (Assistant.is_default == True))
        .order_by(Assistant.is_default.desc(), Assistant.name.asc())
    )
    result = await db.execute(stmt)
    assistants = list(result.scalars().all())
    print(f"Found {len(assistants)} assistants for user {current_user['user_id']}")
    return assistants


@router.post("", response_model=AssistantOut, status_code=status.HTTP_201_CREATED)
async def create_assistant(
    body: AssistantCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Assistant:
    workspace = await _get_default_workspace(current_user["user_id"], db)
    assistant = Assistant(workspace_id=workspace.id, **body.model_dump())
    db.add(assistant)
    await db.commit()
    await db.refresh(assistant)
    return assistant


@router.delete("/{assistant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assistant(
    assistant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> None:
    result = await db.execute(select(Assistant).where(Assistant.id == assistant_id))
    assistant = result.scalar_one_or_none()
    if not assistant:
        raise HTTPException(status_code=404, detail="Assistant not found")
    if assistant.is_default:
        raise HTTPException(status_code=400, detail="Cannot delete default assistants")
    await db.delete(assistant)
    await db.commit()
