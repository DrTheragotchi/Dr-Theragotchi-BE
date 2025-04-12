from supabase import create_client
import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Log environment variables (without exposing sensitive data)
logger.info("Supabase URL: %s", os.getenv("SUPABASE_URL"))
logger.info("Supabase Key exists: %s", bool(os.getenv("SUPABASE_KEY")))

# Initialize Supabase client
try:
    supabase = create_client(
        supabase_url=os.getenv("SUPABASE_URL"),
        supabase_key=os.getenv("SUPABASE_KEY")
    )
    logger.info("Supabase client initialized successfully")
except Exception as e:
    logger.error("Failed to initialize Supabase client: %s", str(e))
    raise 