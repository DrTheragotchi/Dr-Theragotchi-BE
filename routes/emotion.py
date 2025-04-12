from fastapi import APIRouter, HTTPException, Query
from models.schemas import EmotionUpdateRequest, EmotionUpdateResponse, EmotionType
from db import supabase
from fastapi.responses import JSONResponse

router = APIRouter()

@router.patch("/emotion", response_model=EmotionUpdateResponse)
async def update_emotion(
    emotion: EmotionType = Query(..., description="New emotion"),
    user_uuid: str = Query(..., description="User UUID")
):
    try:
        # Update the user's emotion in the database
        data = {
            "current_mood": emotion
        }
        response = supabase.table("users").update(data).eq("uuid", user_uuid).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        # In a real implementation, you would also update the character's level based on emotion
        # For now, we'll just return the updated emotion
        return EmotionUpdateResponse(success=True, new_mood=emotion)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 