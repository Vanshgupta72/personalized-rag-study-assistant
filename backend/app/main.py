from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Application configuration
from backend.app.core.config import settings

# Authentication routes
from backend.app.api.routes.auth import router as auth_router

# Other API routes
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


# Create the FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Personalized RAG-Based Study Assistant API",
    version="0.1.0"
)


# ---------------------------------------------------------
# CORS CONFIGURATION
# ---------------------------------------------------------
#
# Frontend currently runs on:
# http://localhost:5173
#
# We also allow 5174 because Vite may use that port
# if 5173 is already occupied.
#
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# API ROUTES
# ---------------------------------------------------------

# Authentication
# POST /auth/register
# POST /auth/login
# GET  /auth/me
app.include_router(auth_router)

# Documents
app.include_router(documents_router)

# Chat / RAG
app.include_router(chat_router)

# Subjects
app.include_router(subjects_router)

# Conversations
app.include_router(conversations_router)

# User context
app.include_router(context_router)

# Preferences
app.include_router(preferences_router)

# Topics
app.include_router(topics_router)

# Learning history
app.include_router(learning_history_router)


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------

@app.get("/")
def root():
    """
    Basic health-check endpoint.
    """

    return {
        "message": "Personalized RAG Study Assistant API is running"
    }