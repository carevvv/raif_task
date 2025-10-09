"""
Configuration management for Checko application.
Loads settings from environment variables.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App
    APP_NAME: str = "Checko"
    DEBUG: bool = False
    SECRET_TOKEN: str = "change-me-in-production"
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    WEBAPP_URL: str = "http://localhost:3000"
    
    # OpenRouter LLM
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "mistralai/mistral-7b-instruct"
    
    # Embeddings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # Database
    DATABASE_URL: str = "sqlite:///./checko.db"
    
    # Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 10
    
    # OCR
    TESSERACT_CMD: str = ""  # Leave empty for system default
    OCR_LANGUAGES: str = "rus+eng"
    
    # API
    API_V1_PREFIX: str = "/api"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
