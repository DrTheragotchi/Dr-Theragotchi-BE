from fastapi import APIRouter, HTTPException
from models.schemas import ChatRequest, ChatResponse
from db import supabase
from utils.llm import get_llm_response

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def create_chat(request: ChatRequest):
    try:
        # Get LLM response
        reply = await get_llm_response(request.message)
        
        # In a real implementation, you would save the chat to Supabase here
        # data = {
        #     "user_message": request.message,
        #     "llm_response": reply,
        #     "user_uuid": user_uuid
        # }
        # supabase.table("chats").insert(data).execute()
        
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 