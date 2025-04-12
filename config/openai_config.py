from openai import OpenAI
import os
from dotenv import load_dotenv
from models.schemas import CharacterType, EmotionType
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_ai_response(message: str, character_type: str, current_mood: str) -> str:
    """
    Get AI response based on user message and pet characteristics.
    
    Args:
        message (str): User's message
        character_type (str): Type of animal (e.g., "dog", "cat")
        current_mood (str): Current mood of the pet
        
    Returns:
        str: AI's response
    """
    try:
        # Create the system prompt
        system_prompt = f"""You are a cute {character_type} pet in a virtual pet game. 
Your current mood is {current_mood}.
You should respond in a way that matches your animal type and current mood.
Keep responses short, cute, and playful (max 2-3 sentences).
Use simple language and occasionally add animal sounds or actions.
If you're happy, be excited and playful.
If you're sad, be gentle and comforting.
If you're angry, be grumpy but still cute.
If you're sleepy, be tired but still responsive.
If you're excited, be very energetic and bouncy.
If you're neutral, be calm and friendly.
Always stay in character as a {character_type}."""

        # Create the messages for the API call
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=100,
            temperature=0.7
        )

        # Extract and return the response
        ai_response = response.choices[0].message.content
        logger.info(f"OpenAI response: {ai_response}")
        return ai_response

    except Exception as e:
        logger.error(f"Error getting AI response: {str(e)}")
        # Return a fallback response if OpenAI fails
        return f"*{character_type} sound* Hi! I'm feeling {current_mood} right now. What's up?" 