from fastapi import APIRouter, HTTPException, Query
from models.schemas import EmotionSelectionResponse, CharacterType, EmotionType
from db import supabase
from fastapi.responses import JSONResponse
import random

router = APIRouter()

@router.post("/character", response_model=EmotionSelectionResponse)
async def select_emotion_and_assign_character(
    emotion: EmotionType = Query(..., description="Selected emotion"),
    user_uuid: str = Query(..., description="User UUID")
):
    try:
        # Get the user from the database
        user_response = supabase.table("users").select("*").eq("uuid", user_uuid).execute()
        
        if not user_response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Assign a random character type based on emotion
        # In a real implementation, this would use a more sophisticated algorithm
        character_type = random.choice(list(CharacterType))
        
        # Update the user with the emotion and character type
        data = {
            "current_mood": emotion,
            "character_type": character_type
        }
        supabase.table("users").update(data).eq("uuid", user_uuid).execute()
        
        return EmotionSelectionResponse(
            character_type=character_type,
            current_mood=emotion,
            level=1
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 