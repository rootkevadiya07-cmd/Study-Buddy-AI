import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

class Config:
    """Application Configuration Settings"""
    
    # AI Provider Settings
    # AI_PROVIDER options: 'ollama', 'openai_compatible', 'mock'
    AI_PROVIDER = os.getenv("AI_PROVIDER", "ollama").lower()
    
    # Ollama Settings (Local Mode)
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
    
    # Open-Weight API Settings (Production / Render Mode, e.g. Groq, OpenRouter, Together AI)
    API_KEY = os.getenv("API_KEY", "")
    API_BASE_URL = os.getenv("API_BASE_URL", "https://api.groq.com/openai/v1")
    MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.1-8b-instant")
    
    # Embedding Settings
    EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
    
    # Text Chunking Settings
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 600))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 100))
    
    # Application Settings
    APP_NAME = "StudyBuddy AI"
    APP_TAGLINE = "Your Personal AI Study Partner"

    @classmethod
    def get_provider_info(cls):
        """Returns readable provider details for UI status display"""
        if cls.AI_PROVIDER == "ollama":
            return {
                "mode": "Local (Ollama)",
                "target": f"{cls.OLLAMA_MODEL} @ {cls.OLLAMA_BASE_URL}",
                "provider": "Ollama"
            }
        elif cls.AI_PROVIDER == "openai_compatible":
            return {
                "mode": "Cloud / Render (API)",
                "target": f"{cls.MODEL_NAME} ({cls.API_BASE_URL})",
                "provider": "Open-Weight API"
            }
        else:
            return {
                "mode": "Offline / Fallback",
                "target": "Extractive Heuristic Generator",
                "provider": "Built-in Fallback"
            }
