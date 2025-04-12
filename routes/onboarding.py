from fastapi import APIRouter, HTTPException, Query
from models.schemas import OnboardingResponse
from db import supabase
import uuid
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/onboarding", response_model=OnboardingResponse)
async def create_user(nickname: str = Query(..., description="User nickname")):
    user_uuid = str(uuid.uuid4())
    
    try:
        data = {
            "uuid": user_uuid,
            "nickname": nickname,
            # Character type and mood will be set later
            "animal_type": None,
            "animal_emotion": None,
            "animal_level": 1,  # Start at level 1
            "is_notified": False  # Initialize to False
        }
        supabase.table("users").insert(data).execute()
        return OnboardingResponse(uuid=user_uuid, nickname=nickname)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 