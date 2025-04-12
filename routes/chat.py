from fastapi import APIRouter, HTTPException, Body
from models.schemas import ChatResponse, ChatRequest
from config.supabase_client import supabase
from config.openai_config import get_ai_response
import logging
from fastapi.responses import JSONResponse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_with_pet(request: ChatRequest):
    try:
        logger.info(f"Received chat message: {request.message} from user: {request.uuid}")
        
        # Get user data from Supabase
        user_response = supabase.table("User").select("*").eq("uuid", request.uuid).execute()
        if not user_response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = user_response.data[0]
        logger.info(f"User data: {user_data}")
        
        # Get AI response
        ai_response = get_ai_response(
            message=request.message,
            character_type=user_data["animal_type"],
            current_mood=user_data["animal_emotion"]
        )
        logger.info(f"AI response: {ai_response}")
        
        # Save chat message to Chat table
        chat_data = {
            "user_uuid": request.uuid,
            "message": request.message,
            "response": ai_response
        }
        logger.info(f"Saving chat data: {chat_data}")
        
        result = supabase.table("Chat").insert(chat_data).execute()
        logger.info(f"Chat saved to Supabase: {result}")
        
        return ChatResponse(response=ai_response)
            
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 