from pydantic import BaseModel, validator
from typing import Optional, List
from uuid import UUID
from enum import Enum
from datetime import datetime, date

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
    NEUTRAL = "neutral"

class OnboardingResponse(BaseModel):
    uuid: UUID
    nickname: str

class EmotionSelectionResponse(BaseModel):
    animal_type: CharacterType
    animal_emotion: EmotionType
    animal_level: int
    points: Optional[int] = 0

class ChatRequest(BaseModel):
    message: str
    uuid: str
    emotion: Optional[str] = None
    
    @validator('emotion')
    def validate_emotion(cls, v):
        if v == "":
            return None
        return v

class ChatResponse(BaseModel):
    response: str
    emotion: Optional[EmotionType] = None
    animal: Optional[CharacterType] = None
    points: Optional[int] = None
    isFifth: bool = False

class EmotionUpdateResponse(BaseModel):
    success: bool
    new_mood: EmotionType

class UserResponse(BaseModel):
    uuid: UUID
    nickname: str
    animal_type: Optional[CharacterType] = None
    animal_emotion: Optional[EmotionType] = None
    animal_level: int
    points: Optional[int] = 0
    is_notified: bool
    created_at: Optional[datetime] = None

# Diary related models
class DiaryEntry(BaseModel):
    date: date
    summary: str
    emotion: str
    
class DiaryGenerateResponse(BaseModel):
    message: str
    date: date
    summary: str
    emotion: str

class DiaryDateEntry(BaseModel):
    date: date
    emotion: str
    summary: Optional[str] = None 