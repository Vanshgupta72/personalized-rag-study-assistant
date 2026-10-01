from backend.app.api.routes.chat import router as chat_router
from backend.app.api.routes.preferences import router as preferences_router
from backend.app.api.routes.documents import router as documents_router
from backend.app.api.routes.topics import router as topics_router
from backend.app.api.routes.subjects import router as subjects_router
from backend.app.api.routes.learning_history import (
    router as learning_history_router
)
from backend.app.api.routes.context import router as context_router
from backend.app.api.routes.conversations import (
    router as conversations_router,
)
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

# Document upload and management endpoints.
app.include_router(documents_router)

app.include_router(chat_router)
app.include_router(subjects_router)
app.include_router(conversations_router)
app.include_router(context_router)
app.include_router(preferences_router)
app.include_router(topics_router)
app.include_router(learning_history_router)

@app.get("/")
def root():
    """
    Basic health-check endpoint.
    """

    return {
        "message": "Personalized RAG Study Assistant API is running"
    }