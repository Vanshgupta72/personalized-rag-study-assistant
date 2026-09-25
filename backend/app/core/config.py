# Pydantic Settings automatically reads configuration
# values from the .env file.
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central application configuration.

    Values are loaded from environment variables and .env.
    """

    # Application information.
    APP_NAME: str = "Personalized RAG Study Assistant"
    ENVIRONMENT: str = "development"

    # PostgreSQL connection URL.
    DATABASE_URL: str

    # Secret key used to sign JWT tokens.
    JWT_SECRET: str

    # JWT access-token lifetime in minutes.
    JWT_EXPIRE_MINUTES: int = 60

    # Local path where the vector database will be stored.
    VECTOR_DB_PATH: str = "./data/vector_db"

    # API key for the future LLM integration.
    LLM_API_KEY: str = ""

    # Tell Pydantic to load values from .env.
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


# Create one settings object that can be imported
# throughout the application.
settings = Settings()