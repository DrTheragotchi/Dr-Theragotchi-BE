from fastapi import APIRouter, HTTPException
from config.supabase_client import supabase
from config.openai_config import get_ai_response

router = APIRouter()

@router.post("/chat")
async def chat_with_pet(uuid: str, message: str):
    """
    Chat with the AI pet.
    
    Args:
        uuid (str): User's UUID
        message (str): Message to send to the pet
        
    Returns:
        dict: AI's response
    """
    try:
        # Get user data to access character type and mood
        user_data = supabase.table("User").select("*").eq("uuid", uuid).execute()
        
        if not user_data.data:
            raise HTTPException(status_code=404, detail="User not found")
            
        user = user_data.data[0]
        
        # Get AI response using the new configuration
        ai_response = get_ai_response(
            message=message,
            character_type=user["character_type"],
            current_mood=user["current_mood"]
        )
        
        # Save chat message to Chat table
        chat_data = {
            "user_uuid": uuid,
            "message": message,
            "response": ai_response
        }
        supabase.table("Chat").insert(chat_data).execute()
        
        return {"reply": ai_response}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 