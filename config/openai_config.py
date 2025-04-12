from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_ai_response(message: str, character_type: str, current_mood: str) -> str:
    """
    Get AI response based on the message, character type, and current mood.
    
    Args:
        message (str): User's message
        character_type (str): Type of character (tiger, penguin, etc.)
        current_mood (str): Current mood of the character
        
    Returns:
        str: AI's response
    """
    try:
        # Create a system message that defines the character's personality
        system_message = f"""You are a {character_type} pet in a virtual pet game. 
        Your current mood is {current_mood}. 
        Respond in a way that matches your character type and current mood.
        Keep responses short, cute, and engaging."""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error getting AI response: {str(e)}")
        return "Sorry, I'm having trouble responding right now. Please try again later." 