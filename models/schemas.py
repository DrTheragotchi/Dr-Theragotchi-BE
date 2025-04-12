from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class OnboardingRequest(BaseModel):
    character_type: str

class OnboardingResponse(BaseModel):
    uuid: UUID

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

class UserResponse(BaseModel):
    uuid: UUID
    character_type: str
    created_at: str 