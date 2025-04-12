from fastapi import APIRouter, HTTPException, Body
from models.schemas import OnboardingResponse, UserResponse
from config.supabase_client import supabase
import logging
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class OnboardingRequest(BaseModel):
    uuid: str
    nickname: str

@router.post("/onboarding", response_model=OnboardingResponse)
async def create_user(request: OnboardingRequest):
    try:
        logger.info(f"Creating user with UUID: {request.uuid}")
        
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
                is_notified=user_data["is_notified"],
                created_at=user_data.get("created_at")
            )
        
        data = {
            "uuid": request.uuid,
            "nickname": request.nickname,
            "animal_type": None,  # Will be set when character is assigned
            "animal_emotion": None,    # Will be set when character is assigned
            "animal_level": 1,             # Start at level 1
            "points": 0,                # Initialize points to 0
            "is_notified": False     # Initialize to False
        }
        
        logger.info(f"Inserting data into Supabase: {data}")
        
        result = supabase.table("User").insert(data).execute()
        
        logger.info(f"Supabase response: {result}")
        
        if not result.data:
            logger.error("Failed to create user: No data returned from Supabase")
            raise HTTPException(status_code=500, detail="Failed to create user")
            
        return OnboardingResponse(uuid=request.uuid, nickname=request.nickname)
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 