from fastapi import APIRouter, HTTPException, Query, Body
from models.schemas import UserResponse, OnboardingResponse, EmotionSelectionResponse, EmotionUpdateResponse, CharacterType, EmotionType
from config.supabase_client import supabase
from fastapi.responses import JSONResponse
from typing import List, Optional
import uuid
import random
from pydantic import BaseModel

router = APIRouter()

class OnboardingRequest(BaseModel):
    uuid: str
    nickname: str

@router.post("/onboarding")
async def create_user(request: OnboardingRequest):
    try:
        if not request.nickname:
            raise HTTPException(status_code=400, detail="Nickname is required")
        
        if not request.uuid:
            raise HTTPException(status_code=400, detail="UUID is required")
        
        # Check if user already exists
        existing_user = supabase.table("User").select("*").eq("uuid", request.uuid).execute()
        if existing_user.data:
            # User already exists, return their info
            user_data = existing_user.data[0]
            return UserResponse(
                uuid=user_data["uuid"],
                nickname=user_data["nickname"],
                animal_type=user_data["animal_type"],
                animal_emotion=user_data["animal_emotion"],
                animal_level=user_data["animal_level"],
                points=user_data.get("points", 0),
                is_notified=user_data["is_notified"],
                created_at=user_data.get("created_at")
            )
        
        # Create new user
        data = {
            "uuid": request.uuid,
            "nickname": request.nickname,
            "animal_type": None,
            "animal_emotion": None,
            "animal_level": 1,
            "points": 0,
            "is_notified": False
        }
        supabase.table("User").insert(data).execute()
        return OnboardingResponse(uuid=request.uuid, nickname=request.nickname)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/character")
async def assign_character(
    emotion: EmotionType = Query(..., description="Selected emotion"),
    user_uuid: str = Query(..., description="User UUID")
):
    try:
        if not emotion or not user_uuid:
            raise HTTPException(status_code=400, detail="Emotion and UUID are required")
        
        # Get the user from the database
        user_response = supabase.table("User").select("*").eq("uuid", user_uuid).execute()
        if not user_response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        # If animal_type is None, assign a random character
        if not user_response.data[0].get("animal_type"):
            animal_type = random.choice(list(CharacterType))
            data = {
                "animal_emotion": emotion,
                "animal_type": animal_type
            }
            supabase.table("User").update(data).eq("uuid", user_uuid).execute()
            return EmotionSelectionResponse(
                animal_type=animal_type,
                animal_emotion=emotion,
                animal_level=1,
                points=user_response.data[0].get("points", 0)
            )
        else:
            data = {
                "animal_emotion": emotion
            }
            supabase.table("User").update(data).eq("uuid", user_uuid).execute()
            return EmotionUpdateResponse(success=True, new_mood=emotion)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{uuid}")
async def get_user(uuid: str):
    try:
        user_response = supabase.table("User").select("*").eq("uuid", uuid).execute()
        if not user_response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = user_response.data[0]
        return UserResponse(
            uuid=user_data["uuid"],
            nickname=user_data["nickname"],
            animal_type=user_data["animal_type"],
            animal_emotion=user_data["animal_emotion"],
            animal_level=user_data["animal_level"],
            points=user_data.get("points", 0),
            is_notified=user_data["is_notified"],
            created_at=user_data.get("created_at")
        )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/emotion")
async def update_emotion(
    emotion: EmotionType = Query(..., description="New emotion"),
    user_uuid: str = Query(..., description="User UUID")
):
    try:
        if not emotion or not user_uuid:
            raise HTTPException(status_code=400, detail="Emotion and UUID are required")
        
        # Get the user from the database
        user_response = supabase.table("User").select("*").eq("uuid", user_uuid).execute()
        if not user_response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update the emotion
        data = {
            "animal_emotion": emotion
        }
        supabase.table("User").update(data).eq("uuid", user_uuid).execute()
        
        return EmotionUpdateResponse(success=True, new_mood=emotion)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/user/{uuid}")
async def delete_user(uuid: str):
    try:
        # Delete the user
        supabase.table("User").delete().eq("uuid", uuid).execute()
        
        # Delete associated chat messages
        supabase.table("Chat").delete().eq("uuid", uuid).execute()
        
        return {"message": "User deleted successfully"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 