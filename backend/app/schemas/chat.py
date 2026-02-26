import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class WorkspaceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class WorkspaceOut(BaseModel):
    id: uuid.UUID
    name: str
    owner_id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SessionCreate(BaseModel):
    title: str = Field(default="New Chat", max_length=500)
    assistant_id: uuid.UUID | None = None
    provider: str = Field(default="anthropic")
    model: str = Field(default="claude-3-5-sonnet-20240620")


class SessionOut(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    user_id: str
    assistant_id: uuid.UUID | None
    title: str
    provider: str
    model: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChatRequest(BaseModel):
    content: str = Field(..., min_length=1)
    provider: str | None = None
    model: str | None = None


class TokenEvent(BaseModel):
    type: str = "token"
    content: str


class DoneEvent(BaseModel):
    type: str = "done"
    session_id: str
