from fastapi import APIRouter, HTTPException, Query
from models.schemas import ChatResponse
from config.supabase_client import supabase
import logging
from fastapi.responses import JSONResponse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_with_pet(
    message: str = Query(..., description="User message"),
    uuid: str = Query(..., description="User UUID")
):
    try:
        logger.info(f"Received chat message: {message} from user: {uuid}")
        
        # Get user data from Supabase
        user_response = supabase.table("User").select("*").eq("uuid", uuid).execute()
        if not user_response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        # For testing, just echo back the message
        return ChatResponse(response=message)
            
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 