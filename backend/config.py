import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "ai-agent")

    # MySQL  (SQLAlchemy URI)
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('DB_USER','root')}:{os.getenv('DB_PASSWORD','')}"
        f"@{os.getenv('DB_HOST','127.0.0.1')}:{os.getenv('DB_PORT','3306')}"
        f"/{os.getenv('DB_NAME','ai_chat_agent')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Google OAuth2
    GOOGLE_CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI  = os.getenv("GOOGLE_REDIRECT_URI")

    # AI Model API  (Cerebras / GroqCloud)
    AI_API_BASE_URL = os.getenv("AI_API_BASE_URL", "https://api.cerebras.ai/v1")
    AI_API_KEY      = os.getenv("AI_API_KEY", "")
    AI_MODEL        = os.getenv("AI_MODEL", "llama3.1-70b")   # Map to GPT-OSS-120B equivalent

    # Free tier
    FREE_DAILY_LIMIT = int(os.getenv("FREE_DAILY_LIMIT", 100))