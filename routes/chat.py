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
import uuid as uuid_lib

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Store conversation counts in memory
conversation_counts = {}
conversation_history = {}  # Store conversation history for each user

# Maximum number of exchanges before animal assignment
MAX_EXCHANGES = 4

# Admin prompt for emotion and animal type analysis
ADMIN_PROMPT = """This is the admin. Based on the conversation you just had with the user, please identify the user's true emotion by selecting one from the following categories: HAPPY, SAD, ANGRY, ANXIOUS, or NEUTRAL. Then, choose one animal that corresponds to that emotion from the following list: tiger, penguin, hamster, pig, or dog. Please respond in the following format: emotion: {emotion}, animal: {animal}."""

# Add a simple test endpoint
@router.get("/test")
async def test_endpoint():
    return {"status": "ok", "message": "Server is working!"}

@router.post("/chat", response_model=ChatResponse, 
             response_model_exclude_unset=False,  # Ensure all fields are in response
             response_description="Chat response with therapeutic message and points")
async def chat_with_pet(request: Request, chat_request: ChatRequest):
    try:
        # Get user UUID
        user_uuid = chat_request.uuid
        message = chat_request.message
        
        logger.info(f"Chat request from {user_uuid}: message='{message}'")
        
        # Process optional emotion field at the beginning of the function
        emotion_provided = chat_request.emotion is not None
        validated_emotion = None
        
        if emotion_provided:
            # Validate the provided emotion against valid options
            try:
                # Convert to lowercase for case-insensitive comparison
                emotion_str = chat_request.emotion.lower()
                valid_emotions = ["happy", "sad", "angry", "anxious", "neutral"]
                
                if emotion_str in valid_emotions:
                    validated_emotion = emotion_str
                else:
                    # Default to a valid emotion if the provided one isn't recognized
                    validated_emotion = "neutral"
                    logger.warning(f"Invalid emotion '{emotion_str}' provided, defaulting to 'neutral'")
            except Exception as e:
                logger.error(f"Error processing emotion: {str(e)}")
                # Continue with emotion_provided = False
                emotion_provided = False
        
        logger.info(f"Chat request from {user_uuid}: message='{message}', emotion_provided={emotion_provided}" +
                   (f", emotion='{validated_emotion}'" if emotion_provided else ""))
        
        # Initialize conversation count if it doesn't exist
        if user_uuid not in conversation_counts:
            conversation_counts[user_uuid] = 0
            conversation_history[user_uuid] = []
        
        # Get user data from Supabase
        try:
            user_response = await asyncio.wait_for(
                asyncio.to_thread(
                    lambda: supabase.table("User").select("*").eq("uuid", user_uuid).execute()
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
        conversation_counts[user_uuid] += 1
        current_count = conversation_counts[user_uuid]
        
        # Log the conversation count for debugging
        logger.info(f"Conversation count for {user_uuid}: {current_count}/{MAX_EXCHANGES}")

        # Store the user message in conversation history
        conversation_history[user_uuid].append({"role": "user", "content": message})
        
        # Check if we should analyze emotion and assign an animal type
        animal_to_return = None
        isFifth = (current_count % MAX_EXCHANGES == 0)  # Will be true at 4, 8, 12, etc. (multiples of 4)
        
        logger.info(f"Setting isFifth to {isFifth} for message {current_count}")
        
        if current_count == MAX_EXCHANGES:  # Animal assignment happens on MAX_EXCHANGES (4th message)
            # Log that we're doing animal assignment
            logger.info(f"Performing animal assignment for user {user_uuid} after {current_count} messages")
            
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
                            conversation_history=conversation_history[user_uuid],
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
                
                # Use the validated emotion from the request if provided, otherwise use the detected one
                final_emotion = validated_emotion if emotion_provided else detected_emotion
                logger.info(f"Using emotion for animal assignment: {final_emotion} (user provided: {emotion_provided})")
                
                # Generate therapeutic response and points in the new format
                from config.openai_config import SCORING_PROMPT
                chat_response = await asyncio.wait_for(
                    asyncio.to_thread(
                        lambda: get_ai_response(
                            message=message,
                            character_type=detected_animal,
                            current_mood=final_emotion  # Use the selected emotion
                        )
                    ),
                    timeout=5.0
                )
                
                # Try to extract points from the response
                points = 2  # Default only if extraction fails completely
                points_match = re.search(r'points:\s*(\d+)', chat_response, re.IGNORECASE)
                logger.info(f"Points match: {points_match}")
                if points_match:
                    points = int(points_match.group(1))
                    points = max(0, min(points, 5))  # Ensure within valid range
                    logger.info(f"Extracted points from OpenAI response: {points}")
                else:
                    logger.warning(f"Failed to extract points from OpenAI response, using default: {points}")
                
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
                                         "animal_emotion": final_emotion,  # Use the selected emotion
                                         "points": new_points
                                     })
                                     .eq("uuid", user_uuid)
                                     .execute()
                    ),
                    timeout=3.0
                )
                
                # Reset conversation history but don't reset the counter
                conversation_history[user_uuid] = []
                
                # Store the AI response in conversation history
                conversation_history[user_uuid].append({"role": "assistant", "content": response_text})
                
                # Save chat message to Chat table
                try:
                    # Use upsert (update if exists, insert if not) to avoid duplicate key violation
                    import random
                    # Generate a random ID that will be consistent for this user's messages
                    random_suffix = str(random.randint(1, 1000000))
                    chat_id = f"{user_uuid}-{random_suffix}"
                    
                    chat_data = {
                        "uuid": user_uuid,
                        "user_input": message,
                        "chat_output": response_text
                    }
                    
                    await asyncio.wait_for(
                        asyncio.to_thread(
                            lambda: supabase.table("Chat").upsert(chat_data).execute()
                        ),
                        timeout=3.0
                    )
                except Exception as chat_error:
                    logger.error(f"Error saving chat: {str(chat_error)}")
                    # Try a different approach if upsert fails
                    try:
                        await asyncio.to_thread(
                            lambda: supabase.table("Chat").delete().eq("uuid", user_uuid).execute()
                        )
                        await asyncio.to_thread(
                            lambda: supabase.table("Chat").insert(chat_data).execute()
                        )
                    except Exception as delete_error:
                        logger.error(f"Error with delete-then-insert approach: {str(delete_error)}")
                    # Continue even if saving fails
                
                # Return special animal assignment message with points
                logger.info(f"Returning animal assignment response with isFifth=True")
                
                # Only include the animal in the response if the frontend provided an emotion
                animal_to_return = detected_animal if emotion_provided else None
                
                return ChatResponse(
                    response=response_text,
                    emotion=final_emotion,  # Use the selected emotion
                    animal=animal_to_return,
                    points=points,
                    isFifth=True
                )
                
            except asyncio.TimeoutError:
                raise HTTPException(status_code=504, detail="AI service timeout")
        
        # Regular conversation flow
        try:
            # Use the validated emotion from the request if provided, otherwise use the user's stored emotion
            current_emotion_for_ai = validated_emotion if emotion_provided else user_data["animal_emotion"]
            logger.info(f"Using emotion for AI response: {current_emotion_for_ai}")
            
            # Get response and points in a single call
            combined_response = await asyncio.wait_for(
                asyncio.to_thread(
                    lambda: get_ai_response(
                        message=message,
                        character_type=user_data["animal_type"],
                        current_mood=current_emotion_for_ai  # Use the selected emotion
                    )
                ),
                timeout=5.0
            )
            
            # Try to extract points from the response
            points = 2  # Default only if extraction fails completely
            points_match = re.search(r'points:\s*(\d+)', combined_response, re.IGNORECASE)
            if points_match:
                points = int(points_match.group(1))
                points = max(0, min(points, 5))  # Ensure within valid range
                logger.info(f"Extracted points from OpenAI response: {points}")
            else:
                logger.warning(f"Failed to extract points from OpenAI response, using default: {points}")
            
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
            logger.info(f"Awarding {points} points to user {user_uuid}. New total: {new_points}")
            
            # Store the AI response in conversation history
            conversation_history[user_uuid].append({"role": "assistant", "content": ai_response})
            
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
                update_data["animal_emotion"] = current_emotion_for_ai
            
            await asyncio.wait_for(
                asyncio.to_thread(
                    lambda: supabase.table("User")
                                 .update(update_data)
                                 .eq("uuid", user_uuid)
                                 .execute()
                ),
                timeout=3.0
            )
        except Exception as update_error:
            logger.error(f"Error updating user points: {str(update_error)}")
            # Continue even if the update fails
        
        # Save chat message to Chat table
        try:
            # Use upsert (update if exists, insert if not) to avoid duplicate key violation
            import random
            # Generate a random ID that will be consistent for this user's messages
            random_suffix = str(random.randint(1, 1000000))
            chat_id = f"{user_uuid}-{random_suffix}"
            
            chat_data = {
                "uuid": user_uuid,
                "user_input": message,
                "chat_output": ai_response
            }
            
            try:
                await asyncio.wait_for(
                    asyncio.to_thread(
                        lambda: supabase.table("Chat").upsert(chat_data).execute()
                    ),
                    timeout=3.0
                )
            except Exception as e:
                # Log detailed error but continue
                logger.error(f"Error saving chat: {str(e)}")
                # Try a different approach if upsert fails
                try:
                    await asyncio.to_thread(
                        lambda: supabase.table("Chat").delete().eq("uuid", user_uuid).execute()
                    )
                    await asyncio.to_thread(
                        lambda: supabase.table("Chat").insert(chat_data).execute()
                    )
                except Exception as delete_error:
                    logger.error(f"Error with delete-then-insert approach: {str(delete_error)}")
                pass
                
        except asyncio.TimeoutError:
            # Don't fail the request if saving fails
            pass
        
        # Only include the animal in the response if the frontend provided an emotion
        animal_to_return = user_data["animal_type"] if emotion_provided and user_data["animal_type"] is not None else None
        
        # Use the validated emotion from the request if provided
        # Otherwise fall back to the user's stored emotion from DB
        response_emotion = validated_emotion if emotion_provided else user_data["animal_emotion"]
        logger.info(f"Using emotion for response: {response_emotion}")
        
        return ChatResponse(
            response=ai_response,
            emotion=response_emotion,
            animal=animal_to_return,
            points=points,
            isFifth=isFifth
        )
            
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
    
    