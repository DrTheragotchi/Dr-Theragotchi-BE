from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from enum import Enum

class CharacterType(str, Enum):
    TIGER = "tiger"
    PENGUIN = "penguin"
    HAMSTER = "hamster"
    PIG = "pig"
    DOG = "dog"

class EmotionType(str, Enum):
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    ANXIOUS = "anxious"
    CALM = "calm"
    EXCITED = "excited"

class OnboardingResponse(BaseModel):
    uuid: UUID
    nickname: str

class EmotionSelectionResponse(BaseModel):
    character_type: CharacterType
    current_mood: EmotionType
    level: int

class ChatResponse(BaseModel):
    reply: str

class EmotionUpdateResponse(BaseModel):
    success: bool
    new_mood: EmotionType

class UserResponse(BaseModel):
    uuid: UUID
    nickname: str
    character_type: CharacterType
    current_mood: EmotionType
    level: int
    created_at: str 