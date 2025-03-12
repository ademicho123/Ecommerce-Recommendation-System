import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

AMAZON_AFFILIATE_API_KEY = os.getenv("AMAZON_AFFILIATE_API_KEY")
BOL_PLAZA_API_KEY = os.getenv("BOL_PLAZA_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")