import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API = os.environ.get("GROQ_API_KEY")
MONGO_URI = os.environ.get("MONGO_DB_URI")
APP_SECRETE_KEY = os.environ.get("MONGO_DB_URI")