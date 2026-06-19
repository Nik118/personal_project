from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Code Review Assistant"
    API_V1_STR: str = "/api/v1"
    
    # Security
    GITHUB_WEBHOOK_SECRET: str = "dummy_secret_for_local_dev"
    GITHUB_TOKEN: str = "your_github_pat_here"
    
    # LLM
    GEMINI_API_KEY: str = "your_gemini_api_key_here"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/code_reviewer"
    
    # Redis / Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()
