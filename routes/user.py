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
    action: str = Query(..., description="Action to perform: create, update_emotion, get, or update_notification"),
    nickname: Optional[str] = Query(None, description="User nickname (required for create)"),
    emotion: Optional[EmotionType] = Query(None, description="Selected emotion (required for update_emotion)"),
    uuid: Optional[str] = Query(None, description="User UUID (required for update_emotion, get, and update_notification)"),
    is_notified: Optional[bool] = Query(None, description="Notification status (required for update_notification)")
):
    try:
        if action == "create":
            if not nickname:
                raise HTTPException(status_code=400, detail="Nickname is required for create action")
            
            user_uuid = str(uuid.uuid4())
            data = {
                "uuid": user_uuid,
                "nickname": nickname,
                "animal_type": None,
                "animal_emotion": None,
                "animal_level": 1,
                "is_notified": False
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
            
            # If animal_type is None, assign a random character
            if not user_response.data[0].get("animal_type"):
                animal_type = random.choice(list(CharacterType))
                data = {
                    "animal_emotion": emotion,
                    "animal_type": animal_type
                }
                supabase.table("users").update(data).eq("uuid", uuid).execute()
                return EmotionSelectionResponse(
                    animal_type=animal_type,
                    animal_emotion=emotion,
                    animal_level=1
                )
            else:
                data = {
                    "animal_emotion": emotion
                }
                supabase.table("users").update(data).eq("uuid", uuid).execute()
                return EmotionUpdateResponse(success=True, new_mood=emotion)
            
        elif action == "get":
            if not uuid:
                raise HTTPException(status_code=400, detail="UUID is required for get action")
            
            user_response = supabase.table("users").select("*").eq("uuid", uuid).execute()
            if not user_response.data:
                raise HTTPException(status_code=404, detail="User not found")
            
            user_data = user_response.data[0]
            return UserResponse(
                uuid=user_data["uuid"],
                nickname=user_data["nickname"],
                animal_type=user_data["animal_type"],
                animal_emotion=user_data["animal_emotion"],
                animal_level=user_data["animal_level"],
                is_notified=user_data["is_notified"],
                created_at=user_data.get("created_at")
            )
            
        elif action == "update_notification":
            if not uuid or is_notified is None:
                raise HTTPException(status_code=400, detail="UUID and is_notified are required for update_notification action")
            
            data = {
                "is_notified": is_notified
            }
            supabase.table("users").update(data).eq("uuid", uuid).execute()
            return {"success": True, "is_notified": is_notified}
            
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 