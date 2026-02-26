import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class AssistantCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(default="", max_length=1000)
    system_prompt: str = Field(default="")
    graph_type: str = Field(default="chat")
    icon: str = Field(default="bot", max_length=64)


class AssistantOut(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    name: str
    description: str
    system_prompt: str
    graph_type: str
    icon: str
    is_default: bool
    created_at: datetime

    model_config = {"from_attributes": True}
