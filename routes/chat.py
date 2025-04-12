from fastapi import APIRouter, HTTPException, Query
from models.schemas import ChatResponse
from db import supabase
from utils.llm import get_llm_response
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def create_chat(
    message: str = Query(..., description="User message"),
    user_uuid: str = Query(..., description="User UUID")
):
    try:
        # Get LLM response
        reply = await get_llm_response(message)
        
        # In a real implementation, you would save the chat to Supabase here
        # data = {
        #     "user_message": message,
        #     "llm_response": reply,
        #     "user_uuid": user_uuid
        # }
        # supabase.table("chats").insert(data).execute()
        
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 