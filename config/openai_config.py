from openai import OpenAI
import os
from dotenv import load_dotenv
from models.schemas import CharacterType, EmotionType
import logging
from openai.types.chat import ChatCompletion
import time
from typing import List, Dict, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Default therapist prompt template
DEFAULT_PROMPT = """I want to use you as my therapist right now. From this point on, you're the counselor, and your role is to understand and heal my emotions as much as possible. The emotion I'm currently feeling is {emotion}, which is one of the following: HAPPY, SAD, ANGRY, ANXIOUS, CALM, EXCITED, SLEEPY, or NEUTRAL. 
And based on the message saying "Why are you feeling {emotion}?" the user said "{message}".
Use this information to guide your responses, but don't mention what I just explained—just act like the therapist right away. And says like a human don't be repetitive."""

# Scoring prompt for determining points
SCORING_PROMPT = """User response: "{message}".

Admin instruction:
Based on the user's response, generate your own therapeutic reply. Then, evaluate the user's emotional state on a scale from 0 to 4, where 0 indicates complete emotional distress and 5 indicates emotional stability.

0 = Severely distressed / Harmful content
1 = Anxious / Worried
2 = Sad / Depressed
3 = Angry / Frustrated / Irritable 
4 = Positive / Hopeful / Grateful 

Consider factors like emotional depth, vulnerability, thoughtfulness, and engagement.

Format your output as follows: gpt: {{your_response}} points: {{int}}"""

def get_ai_response(
    message: str, 
    character_type: Optional[str] = None, 
    current_mood: Optional[str] = None, 
    is_animal_selection: bool = False, 
    is_admin_analysis: bool = False,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    admin_prompt: Optional[str] = None
) -> str:
    """
    Get AI response based on user message and pet characteristics.
    
    Args:
        message (str): User's message or prompt
        character_type (str, optional): Type of animal (e.g., "dog", "cat")
        current_mood (str, optional): Current mood of the pet
        is_animal_selection (bool): Whether this is an animal selection query
        is_admin_analysis (bool): Whether this is an admin analysis of the conversation
        conversation_history (List[Dict], optional): List of conversation messages for analysis
        admin_prompt (str, optional): Admin prompt for analysis, passed from chat.py
        
    Returns:
        str: AI's response
    """
    try:
        # Admin analysis of conversation
        if is_admin_analysis and conversation_history:
            # Use the admin prompt passed from chat.py
            system_prompt = admin_prompt
            
        # Create the system prompt based on the scenario
        elif is_animal_selection:
            system_prompt = """You are an animal matching expert. 
Based on the conversation history, you need to match the user with the most suitable animal type.
Choose from: tiger, penguin, hamster, pig, or dog.
Respond with ONLY the animal name in lowercase, nothing else."""
        else:
            # For regular conversations, use the therapist prompt with scoring
            if not current_mood:
                current_mood = "neutral"
                
            if not character_type:
                character_type = "friendly pet"
                
            # Substitute values into the default prompt and add scoring
            system_prompt = DEFAULT_PROMPT.format(
                emotion=current_mood.upper(),
                message=message
            )
            
            # Add the scoring prompt to get points in the response
            system_prompt += "\n\n" + SCORING_PROMPT.format(message=message)
            logger.info(f"Using scoring prompt to get points in the response")

        # Create the messages for the API call
        if is_admin_analysis and conversation_history:
            # Include the conversation history for analysis
            messages = [
                {"role": "system", "content": system_prompt},
                *conversation_history,
                {"role": "user", "content": message}
            ]
        else:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]

        # Call OpenAI API with timeout
        start_time = time.time()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=200 if is_admin_analysis else 150,  # Fixed the incomplete line
            temperature=0.7,
            timeout=5  # 5 second timeout
        )
        end_time = time.time()
        logger.info(f"OpenAI response time: {end_time - start_time:.2f} seconds")

        # Extract and return the response
        ai_response = response.choices[0].message.content
        logger.info(f"OpenAI response: {ai_response}")
        return ai_response

    except Exception as e:
        logger.error(f"Error getting AI response: {str(e)}")
        # Return a fallback response based on the scenario
        if is_admin_analysis:
            return "emotion: neutral, animal: dog"  # Default fallback analysis
        elif is_animal_selection:
            return "dog"  # Default fallback animalfd
        else:
            if not character_type:
                character_type = "friendly pet"
            if not current_mood:
                current_mood = "neutral"
            return f"I understand you're feeling {current_mood}. How can I help you today?"     