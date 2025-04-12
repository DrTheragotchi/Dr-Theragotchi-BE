from fastapi import APIRouter, HTTPException
from models.schemas import OnboardingRequest, OnboardingResponse
from db import supabase
import uuid

router = APIRouter()

@router.post("/onboarding", response_model=OnboardingResponse)
async def create_user(request: OnboardingRequest):
    user_uuid = str(uuid.uuid4())
    
    try:
        data = {
            "uuid": user_uuid,
            "character_type": request.character_type
        }
        supabase.table("users").insert(data).execute()
        return OnboardingResponse(uuid=user_uuid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 