from fastapi import APIRouter, HTTPException, Body, Request, Query
from models.schemas import ChatResponse, ChatRequest, EmotionType, CharacterType
from config.supabase_client import supabase
from config.openai_config import get_ai_response
import logging
import asyncio
from typing import Optional
import time
from datetime import datetime
import random

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Store conversation counts in memory
conversation_counts = {}
conversation_history = {}  # Store conversation history for each user

# Maximum number of exchanges before animal assignment
MAX_EXCHANGES = 5

# Admin prompt for emotion and animal type analysis
ADMIN_PROMPT = """This is the admin. Based on the conversation you just had with the user, please identify the user's true emotion by selecting one from the following categories: HAPPY, SAD, ANGRY, ANXIOUS, or NEUTRAL. Then, choose one animal that corresponds to that emotion from the following list: tiger, penguin, hamster, pig, or dog. Please respond in the following format: emotion: {emotion}, animal: {animal}."""

# Add a simple test endpoint
@router.get("/test")
async def test_endpoint():
    return {"status": "ok", "message": "Server is working!"}

@router.post("/chat", response_model=ChatResponse)
async def chat_with_pet(request: Request, chat_request: ChatRequest):
    try:
        # Get user UUID
        uuid = chat_request.uuid
        message = chat_request.message
        
        # Initialize conversation count if it doesn't exist
        if uuid not in conversation_counts:
            conversation_counts[uuid] = 0
            conversation_history[uuid] = []
        
        # Get user data from Supabase
        try:
            user_response = await asyncio.wait_for(
                asyncio.to_thread(
                    lambda: supabase.table("User").select("*").eq("uuid", uuid).execute()
                ),
                timeout=3.0
            )
        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail="Database timeout")
            
        if not user_response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = user_response.data[0]
        
        # Increment conversation count
        conversation_counts[uuid] += 1
        current_count = conversation_counts[uuid]
        
        # Log the conversation count for debugging
        logger.info(f"Conversation count for {uuid}: {current_count}/{MAX_EXCHANGES}")
        
        # Store the user message in conversation history
        conversation_history[uuid].append({"role": "user", "content": message})
        
        # Check if we should analyze emotion and assign an animal type
        if current_count >= MAX_EXCHANGES:
            # Log that we're doing animal assignment
            logger.info(f"Performing animal assignment for user {uuid} after {current_count} messages")
            
            # This is the animal and emotion assignment
            try:
                # Send the admin prompt to analyze emotion and animal type
                analysis = await asyncio.wait_for(
                    asyncio.to_thread(
                        lambda: get_ai_response(
                            message="Analyze the conversation",  # This is just a placeholder, the actual prompt is passed as admin_prompt
                            character_type=None,
                            current_mood=None,
                            is_admin_analysis=True,
                            conversation_history=conversation_history[uuid],
                            admin_prompt=ADMIN_PROMPT
                        )
                    ),
                    timeout=5.0
                )
                
                # Parse the response to extract emotion and animal type
                try:
                    # Extract emotion and animal from the response format: emotion: {emotion}, animal: {animal}
                    response_parts = analysis.lower().split(',')
                    emotion_part = response_parts[0].strip()
                    animal_part = response_parts[1].strip() if len(response_parts) > 1 else ""
                    
                    detected_emotion = emotion_part.split(':')[1].strip() if ':' in emotion_part else "neutral"
                    detected_animal = animal_part.split(':')[1].strip() if ':' in animal_part else "dog"
                    
                    # Validate emotion
                    valid_emotions = ["happy", "sad", "angry", "anxious", "neutral"]
                    if detected_emotion not in valid_emotions:
                        detected_emotion = "neutral"
                    
                    # Validate animal
                    valid_animals = ["tiger", "penguin", "hamster", "pig", "dog"]
                    if detected_animal not in valid_animals:
                        detected_animal = "dog"
                except Exception as parse_error:
                    # Default values if parsing fails
                    detected_emotion = "neutral"
                    detected_animal = "dog"
                
                # Update user with assigned animal and emotion
                await asyncio.wait_for(
                    asyncio.to_thread(
                        lambda: supabase.table("User")
                                     .update({
                                         "animal_type": detected_animal,
                                         "animal_emotion": detected_emotion
                                     })
                                     .eq("uuid", uuid)
                                     .execute()
                    ),
                    timeout=3.0
                )
                
                # Reset conversation count and history after assignment
                conversation_counts[uuid] = 0
                conversation_history[uuid] = []
                
                # Return special animal assignment message
                return ChatResponse(
                    response=f"I've been thinking about our conversation. You seem to be feeling {detected_emotion}, and I think you're a lot like a {detected_animal}! *excited*",
                    emotion=detected_emotion,
                    animal=detected_animal
                )
                
            except asyncio.TimeoutError:
                raise HTTPException(status_code=504, detail="AI service timeout")
        
        # Regular conversation flow
        try:
            # Regular response
            ai_response = await asyncio.wait_for(
                asyncio.to_thread(
                    lambda: get_ai_response(
                        message=message,
                        character_type=user_data["animal_type"],
                        current_mood=user_data["animal_emotion"]
                    )
                ),
                timeout=5.0
            )
            
            # Store the AI response in conversation history
            conversation_history[uuid].append({"role": "assistant", "content": ai_response})
            
        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail="AI service timeout")
            
        # Save chat message to Chat table
        try:
            chat_data = {
                "uuid": uuid,
                "user_input": message,
                "chat_output": ai_response
            }
            
            try:
                await asyncio.wait_for(
                    asyncio.to_thread(
                        lambda: supabase.table("Chat").insert(chat_data).execute()
                    ),
                    timeout=3.0
                )
            except Exception:
                # Continue even if saving fails
                pass
                
        except asyncio.TimeoutError:
            # Don't fail the request if saving fails
            pass
        
        # Regular chat response without emotion and animal (they will be None by default)
        return ChatResponse(
            response=ai_response
        )
            
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
    
    