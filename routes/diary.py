from fastapi import APIRouter, HTTPException, Path
from typing import List
from datetime import date, datetime, timedelta
import logging
from config.supabase_client import supabase
from models.schemas import DiaryGenerateResponse, DiaryDateEntry
from config.openai_config import client as openai_client
import asyncio
import os
from supabase import create_client

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize a separate Supabase client with service role
try:
    service_key = os.getenv("SUPABASE_SERVICE_KEY")
    if service_key:
        admin_supabase = create_client(
            supabase_url=os.getenv("SUPABASE_URL"),
            supabase_key=service_key
        )
        logger.info("Admin Supabase client initialized with service role key")
    else:
        logger.warning("SUPABASE_SERVICE_KEY not found, falling back to regular key")
        admin_supabase = supabase
except Exception as e:
    logger.error(f"Failed to initialize admin Supabase client: {str(e)}")
    # Fall back to regular client
    admin_supabase = supabase

router = APIRouter(tags=["Diary"], prefix="/diary")

async def generate_diary(chat_log: str) -> tuple[str, str]:
    """
    Generate a diary summary and emotion from chat logs.
    This function will be replaced with actual implementation by the team.
    
    Args:
        chat_log: The chat logs for the day
        
    Returns:
        A tuple of (summary, emotion)
    """
    try:
        # Placeholder for the actual implementation
        # Your teammate will provide the specific prompt
        response = await asyncio.to_thread(
            lambda: openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a diary summarizer for a mental health app."},
                    {"role": "user", "content": f"Summarize these chats into a diary entry and determine the overall emotion: {chat_log}"}
                ],
                max_tokens=500,
                temperature=0.7
            )
        )
        
        # Extract summary and emotion (in real implementation, you'd parse this properly)
        ai_response = response.choices[0].message.content
        
        # Placeholder parsing - this should be improved based on the actual prompt template
        # Assuming format: "Summary: ... \nEmotion: ..."
        parts = ai_response.split("\n")
        summary = parts[0]
        emotion = "neutral"  # Default
        
        # Try to extract emotion from response
        for part in parts:
            if part.lower().startswith("emotion:"):
                emotion = part.split(":", 1)[1].strip().lower()
                break
                
        return summary, emotion
        
    except Exception as e:
        logger.error(f"Error generating diary: {str(e)}")
        return "Failed to generate diary summary.", "neutral"


@router.post("/generate/{uuid}", response_model=DiaryGenerateResponse)
async def create_diary_entry(uuid: str = Path(..., description="User UUID")):
    """
    Generate a diary entry for today based on the user's chat messages.
    """
    try:
        logger.info(f"Starting diary generation for user {uuid}")
        # First, check if the user exists (try both User and users tables)
        try:
            user_response = await asyncio.to_thread(
                lambda: admin_supabase.table("User").select("*").eq("uuid", uuid).execute()
            )
            if not user_response.data:
                user_response = await asyncio.to_thread(
                    lambda: admin_supabase.table("users").select("*").eq("uuid", uuid).execute()
                )
            logger.info(f"User lookup successful: {user_response.data is not None and len(user_response.data) > 0}")
        except Exception as e:
            logger.warning(f"Error with User table, trying users: {e}")
            user_response = await asyncio.to_thread(
                lambda: admin_supabase.table("users").select("*").eq("uuid", uuid).execute()
            )
        
        if not user_response.data:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Get today's date in local timezone
        today = date.today()
        logger.info(f"Generating diary for date: {today.isoformat()}")
        
        # Fetch all chat messages for this user (no date filtering since there's no created_at column)
        try:
            logger.info("Attempting to query Chat table")
            chat_response = await asyncio.to_thread(
                lambda: admin_supabase.table("Chat")
                    .select("uuid, user_input, chat_output")
                    .eq("uuid", uuid)
                    .execute()
            )
            logger.info(f"Chat query successful, found {len(chat_response.data)} messages")
        except Exception as e:
            logger.error(f"Error querying Chat table: {e}")
            # Create a default empty response
            chat_response = type('obj', (object,), {'data': []})
        
        if not chat_response.data:
            # Instead of raising an error, just generate a generic diary entry
            logger.warning(f"No chat messages found for user {uuid}, creating generic diary")
            chat_log = "No chat messages found for today."
        else:
            # Format chat logs for summarization
            chat_log = ""
            for msg in chat_response.data:
                chat_log += f"User: {msg['user_input']}\nAI: {msg['chat_output']}\n\n"
            
        logger.info("Generating diary summary")
        # Generate diary entry
        summary, emotion = await generate_diary(chat_log)
        logger.info(f"Generated summary with emotion: {emotion}")
        
        # Upsert result to the Diary table (update if exists, insert if not)
        diary_data = {
            "uuid": uuid,
            "date": today.isoformat(),
            "summary": summary,
            "emotion": emotion
        }
        
        logger.info(f"Saving diary entry to database: {diary_data}")
        await asyncio.to_thread(
            lambda: admin_supabase.table("Diary").upsert(diary_data).execute()
        )
        logger.info("Diary entry saved successfully")
        
        return DiaryGenerateResponse(
            message="Diary generated",
            date=today,
            summary=summary,
            emotion=emotion
        )
        
    except HTTPException as he:
        # Re-raise HTTP exceptions
        raise he
    except Exception as e:
        logger.error(f"Error creating diary entry: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create diary entry: {str(e)}")


@router.post("/generate2/{uuid}", response_model=DiaryGenerateResponse)
async def create_diary_entry_alt(uuid: str = Path(..., description="User UUID")):
    """
    Alternative method to generate a diary entry for today (without date filtering)
    """
    try:
        # First, check if the user exists (try both User and users tables)
        try:
            user_response = await asyncio.to_thread(
                lambda: admin_supabase.table("User").select("*").eq("uuid", uuid).execute()
            )
            if not user_response.data:
                user_response = await asyncio.to_thread(
                    lambda: admin_supabase.table("users").select("*").eq("uuid", uuid).execute()
                )
        except Exception as e:
            logger.warning(f"Error with User table, trying users: {e}")
            user_response = await asyncio.to_thread(
                lambda: admin_supabase.table("users").select("*").eq("uuid", uuid).execute()
            )
        
        if not user_response.data:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Get today's date in local timezone
        today = date.today()
        
        # Create a generic diary even without chat messages
        chat_log = "This is a demo diary entry."
        
        # Generate diary entry
        summary, emotion = await generate_diary(chat_log)
        
        # Upsert result to the Diary table (update if exists, insert if not)
        diary_data = {
            "uuid": uuid,
            "date": today.isoformat(),
            "summary": summary,
            "emotion": emotion
        }
        
        await asyncio.to_thread(
            lambda: admin_supabase.table("Diary").upsert(diary_data).execute()
        )
        
        return DiaryGenerateResponse(
            message="Diary generated",
            date=today,
            summary=summary,
            emotion=emotion
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error creating diary entry: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create diary entry: {str(e)}")


@router.get("/dates/{uuid}", response_model=List[DiaryDateEntry])
async def get_diary_dates(uuid: str = Path(..., description="User UUID")):
    """
    Get all diary dates for a user.
    """
    try:
        # First, check if the user exists (try both User and users tables)
        try:
            user_response = await asyncio.to_thread(
                lambda: admin_supabase.table("User").select("*").eq("uuid", uuid).execute()
            )
            if not user_response.data:
                user_response = await asyncio.to_thread(
                    lambda: admin_supabase.table("users").select("*").eq("uuid", uuid).execute()
                )
        except Exception as e:
            logger.warning(f"Error with User table, trying users: {e}")
            user_response = await asyncio.to_thread(
                lambda: admin_supabase.table("users").select("*").eq("uuid", uuid).execute()
            )
        
        if not user_response.data:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Fetch all diary entries for this user
        diary_response = await asyncio.to_thread(
            lambda: admin_supabase.table("Diary")
                .select("date, emotion")
                .eq("uuid", uuid)
                .order("date", desc=True)
                .execute()
        )
        
        # Convert to list of DiaryDateEntry
        diary_dates = []
        for entry in diary_response.data:
            # Parse the date string to a date object
            entry_date = date.fromisoformat(entry["date"])
            diary_dates.append(DiaryDateEntry(
                date=entry_date,
                emotion=entry["emotion"]
            ))
            
        return diary_dates
        
    except HTTPException as he:
        # Re-raise HTTP exceptions
        raise he
    except Exception as e:
        logger.error(f"Error fetching diary dates: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch diary dates: {str(e)}")


@router.get("/test")
async def test_diary_api():
    """
    Test endpoint to check if diary API routes are working
    """
    try:
        # Test Chat table structure
        chat_test = await asyncio.to_thread(
            lambda: admin_supabase.table("Chat").select("*").limit(1).execute()
        )
        
        if chat_test.data:
            available_keys = chat_test.data[0].keys()
            return {"status": "OK", "message": "Diary API is up", "chat_fields": list(available_keys)}
        else:
            # Try with users table for comparison
            user_test = await asyncio.to_thread(
                lambda: admin_supabase.table("User").select("*").limit(1).execute()
            )
            return {"status": "OK", "message": "Diary API is up", "no_chat_data": True, "user_fields": list(user_test.data[0].keys()) if user_test.data else []}
            
    except Exception as e:
        return {"status": "Error", "message": str(e)}


@router.post("/simple/{uuid}")
async def create_simple_diary(uuid: str = Path(..., description="User UUID")):
    """
    Create a simple diary entry with minimal data for testing
    """
    try:
        today = date.today()
        diary_data = {
            "uuid": uuid,
            "date": today.isoformat(),
            "summary": "This is a test diary entry.",
            "emotion": "neutral"
        }
        
        # Try raw SQL insert
        try:
            result = await asyncio.to_thread(
                lambda: admin_supabase.table("Diary").insert(diary_data, returning="minimal").execute()
            )
            return {"message": "Diary entry created", "result": result}
        except Exception as e:
            return {"error": str(e)}
            
    except Exception as e:
        return {"error": str(e)} 