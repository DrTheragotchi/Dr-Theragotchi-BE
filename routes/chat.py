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
import re

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
        
        # Get current points (default to 0 if not set)
        current_points = user_data.get("points", 0) or 0
        
        # Increment conversation count
        conversation_counts[uuid] += 1
        current_count = conversation_counts[uuid]
        
        # Log the conversation count for debugging
        logger.info(f"Conversation count for {uuid}: {current_count}/{MAX_EXCHANGES}")
        
        # Store the user message in conversation history
        conversation_history[uuid].append({"role": "user", "content": message})
        
        # Check if we should analyze emotion and assign an animal type
        animal_to_return = None
        if current_count == MAX_EXCHANGES:  # Changed from >= to == to only send animal once
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
                
                # Generate therapeutic response and points in the new format
                from config.openai_config import SCORING_PROMPT
                chat_response = await asyncio.wait_for(
                    asyncio.to_thread(
                        lambda: get_ai_response(
                            message=message,
                            character_type=detected_animal,
                            current_mood=detected_emotion
                        )
                    ),
                    timeout=5.0
                )
                
                # Try to extract points from the response
                points = 2  # Default
                points_match = re.search(r'points:\s*(\d+)', chat_response, re.IGNORECASE)
                if points_match:
                    points = int(points_match.group(1))
                    points = max(0, min(points, 5))  # Ensure within valid range
                
                # Extract the actual response (everything before "points:")
                response_text = chat_response
                response_parts = chat_response.split("points:", 1)
                if len(response_parts) > 1:
                    response_text = response_parts[0].strip()
                
                # If the response starts with "gpt:", remove it
                if response_text.lower().startswith("gpt:"):
                    response_text = response_text[4:].strip()
                
                # Update total points for the user
                new_points = current_points + points
                
                # Update user with assigned animal, emotion, and points
                await asyncio.wait_for(
                    asyncio.to_thread(
                        lambda: supabase.table("User")
                                     .update({
                                         "animal_type": detected_animal,
                                         "animal_emotion": detected_emotion,
                                         "points": new_points
                                     })
                                     .eq("uuid", uuid)
                                     .execute()
                    ),
                    timeout=3.0
                )
                
                # Reset conversation history but don't reset the counter - we want to continue counting
                conversation_history[uuid] = []
                
                # Store the AI response in conversation history
                conversation_history[uuid].append({"role": "assistant", "content": response_text})
                
                # Save chat message to Chat table
                try:
                    chat_data = {
                        "uuid": uuid,
                        "user_input": message,
                        "chat_output": response_text,
                        "points": points
                    }
                    
                    await asyncio.wait_for(
                        asyncio.to_thread(
                            lambda: supabase.table("Chat").insert(chat_data).execute()
                        ),
                        timeout=3.0
                    )
                except Exception as chat_error:
                    logger.error(f"Error saving chat: {str(chat_error)}")
                    # Continue even if saving fails
                
                # Return special animal assignment message with points
                return ChatResponse(
                    response=response_text,
                    emotion=detected_emotion,
                    animal=detected_animal,
                    points=points
                )
                
            except asyncio.TimeoutError:
                raise HTTPException(status_code=504, detail="AI service timeout")
        
        # Regular conversation flow
        try:
            # Get response and points in a single call
            combined_response = await asyncio.wait_for(
                asyncio.to_thread(
                    lambda: get_ai_response(
                        message=message,
                        character_type=user_data["animal_type"],
                        current_mood=user_data["animal_emotion"]
                    )
                ),
                timeout=5.0
            )
            
            # Try to extract points from the response
            points = 2  # Default
            points_match = re.search(r'points:\s*(\d+)', combined_response, re.IGNORECASE)
            if points_match:
                points = int(points_match.group(1))
                points = max(0, min(points, 5))  # Ensure within valid range
            
            # Extract the actual response (everything before "points:")
            ai_response = combined_response
            response_parts = combined_response.split("points:", 1)
            if len(response_parts) > 1:
                ai_response = response_parts[0].strip()
            
            # If the response starts with "gpt:", remove it
            if ai_response.lower().startswith("gpt:"):
                ai_response = ai_response[4:].strip()
                
            # Update total points for the user
            new_points = current_points + points
            logger.info(f"Awarding {points} points to user {uuid}. New total: {new_points}")
            
            # Store the AI response in conversation history
            conversation_history[uuid].append({"role": "assistant", "content": ai_response})
            
        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail="AI service timeout")
        
        # Update user's points and emotion in Supabase
        try:
            # Only update the emotion after animal assignment (animal_type is not None)
            update_data = {"points": new_points}
            
            # If the animal has been assigned, also update the emotion
            if user_data["animal_type"] is not None:
                # For simplicity, we'll keep using the existing emotion
                # In a real app, you might analyze the user's message to determine a new emotion
                update_data["animal_emotion"] = user_data["animal_emotion"]
            
            await asyncio.wait_for(
                asyncio.to_thread(
                    lambda: supabase.table("User")
                                 .update(update_data)
                                 .eq("uuid", uuid)
                                 .execute()
                ),
                timeout=3.0
            )
        except Exception as update_error:
            logger.error(f"Error updating user points: {str(update_error)}")
            # Continue even if the update fails
        
        # Save chat message to Chat table
        try:
            chat_data = {
                "uuid": uuid,
                "user_input": message,
                "chat_output": ai_response,
                "points": points
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
        
        # Return chat response with points and emotion (if animal has been assigned)
        return ChatResponse(
            response=ai_response,
            emotion=user_data["animal_emotion"] if user_data["animal_type"] is not None else None,
            points=points
        )
            
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
    
    