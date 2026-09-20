# Import BaseSettings to load configuration from environment variables
from pydantic_settings import BaseSettings, SettingsConfigDict


# Application configuration
class Settings(BaseSettings):

    # Application name
    APP_NAME: str = "Personalized RAG Study Assistant"

    # Current environment
    ENVIRONMENT: str = "development"

    # PostgreSQL database URL
    DATABASE_URL: str

    # Secret used for JWT authentication
    JWT_SECRET: str

    # Location where vector database data will be stored
    VECTOR_DB_PATH: str = "./data/vector_db"

    # LLM API key
    LLM_API_KEY: str = ""

    # Tell Pydantic Settings to read values from .env
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


# Create one settings object for the application
settings = Settings()