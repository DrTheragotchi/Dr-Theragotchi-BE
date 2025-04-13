from config.openai_config import get_ai_response
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_openai():
    try:
        # Test parameters
        test_message = "Hello! How's everything going?"
        test_character = "dog"
        test_mood = "happy"
        
        logger.info("Testing OpenAI API...")
        logger.info(f"Message: {test_message}")
        logger.info(f"Character: {test_character}")
        logger.info(f"Mood: {test_mood}")
        
        # Get response
        response = get_ai_response(
            message=test_message,
            character_type=test_character,
            current_mood=test_mood
        )
        
        logger.info(f"Response received: {response}")
        return True
        
    except Exception as e:
        logger.error(f"Error in test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_openai()
    if success:
        print("✅ OpenAI API test cleared!")
    else:
        print("❌ OpenAI API test failed!") 