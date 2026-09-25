# FastAPI application class.
from fastapi import FastAPI

# Application configuration.
from backend.app.core.config import settings

# Authentication routes.
from backend.app.api.routes.auth import router as auth_router


# Create the FastAPI application.
app = FastAPI(
    title=settings.APP_NAME,
    description="Personalized RAG-Based Study Assistant API",
    version="0.1.0"
)


# Register authentication endpoints.
#
# This makes routes such as:
# POST /auth/register
# available to the application.
app.include_router(auth_router)


@app.get("/")
def root():
    """
    Basic health-check endpoint.
    """

    return {
        "message": "Personalized RAG Study Assistant API is running"
    }