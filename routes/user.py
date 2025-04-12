from fastapi import APIRouter, HTTPException, Query
from models.schemas import UserResponse, OnboardingResponse, EmotionSelectionResponse, EmotionUpdateResponse, CharacterType, EmotionType
from db import supabase
from fastapi.responses import JSONResponse
from typing import List, Optional
import uuid
import random

router = APIRouter()

@router.post("/user")
async def user_operations(
    action: str = Query(..., description="Action to perform: create, update_emotion, or get"),
    nickname: Optional[str] = Query(None, description="User nickname (required for create)"),
    emotion: Optional[EmotionType] = Query(None, description="Selected emotion (required for update_emotion)"),
    uuid: Optional[str] = Query(None, description="User UUID (required for update_emotion and get)")
):
    try:
        if action == "create":
            if not nickname:
                raise HTTPException(status_code=400, detail="Nickname is required for create action")
            
            user_uuid = str(uuid.uuid4())
            data = {
                "uuid": user_uuid,
                "nickname": nickname,
                "character_type": None,
                "current_mood": None,
                "level": 1
            }
            supabase.table("users").insert(data).execute()
            return OnboardingResponse(uuid=user_uuid, nickname=nickname)
            
        elif action == "update_emotion":
            if not emotion or not uuid:
                raise HTTPException(status_code=400, detail="Emotion and UUID are required for update_emotion action")
            
            # Get the user from the database
            user_response = supabase.table("users").select("*").eq("uuid", uuid).execute()
            if not user_response.data:
                raise HTTPException(status_code=404, detail="User not found")
            
            # If character_type is None, assign a random character
            if not user_response.data[0].get("character_type"):
                character_type = random.choice(list(CharacterType))
                data = {
                    "current_mood": emotion,
                    "character_type": character_type
                }
                supabase.table("users").update(data).eq("uuid", uuid).execute()
                return EmotionSelectionResponse(
                    character_type=character_type,
                    current_mood=emotion,
                    level=1
                )
            else:
                # Just update the emotion
                data = {
                    "current_mood": emotion
                }
                supabase.table("users").update(data).eq("uuid", uuid).execute()
                return EmotionUpdateResponse(success=True, new_mood=emotion)
                
        elif action == "get":
            if not uuid:
                raise HTTPException(status_code=400, detail="UUID is required for get action")
            
            response = supabase.table("users").select("*").eq("uuid", uuid).execute()
            if not response.data:
                raise HTTPException(status_code=404, detail="User not found")
            return response.data
            
        else:
            raise HTTPException(status_code=400, detail="Invalid action. Must be create, update_emotion, or get")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 