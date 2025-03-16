import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

APIFY_API_KEY = os.getenv("APIFY_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")