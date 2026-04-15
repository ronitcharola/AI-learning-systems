import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-for-ai-os')
    MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
    DB_NAME = os.environ.get('DB_NAME', 'ai_productivity_os')
    
    # Model storage path
    MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ml', 'models')
