# System Architecture

## Project

Personalized RAG-Based Study Assistant

## Architecture

User
↓
React Frontend
↓
FastAPI Backend
↓
Authentication / User Context
↓
Document Processing / Query Processing
↓
Embedding + Retrieval
↓
Vector Database
↓
LLM
↓
Personalized Response

## Storage Architecture

The system uses two complementary storage layers:

### PostgreSQL

Used for structured application data such as:

- Users
- Documents
- Subjects
- Topics
- Conversations
- Messages
- Learning history
- User preferences

### Vector Database

Used for semantic retrieval of document chunks.

Vector records will contain metadata such as:

- user_id
- document_id
- subject
- topic
- page number

This allows retrieval to be scoped to the authenticated user's personal knowledge base.

## Core Design Principle

The system must maintain user-level knowledge isolation.

A user's query should retrieve information only from documents and contextual information belonging to that user.

## Document Processing Flow

Document
→ Text Extraction
→ Cleaning
→ Chunking
→ Metadata
→ Embedding
→ Vector Database

## Question Answering Flow

User Query
→ User Authentication
→ Query Processing
→ Retrieval
→ Context Construction
→ LLM
→ Personalized Answer + Sources


## Configuration Management

Application configuration is managed through environment variables using Pydantic Settings.

Sensitive values such as database credentials, JWT secrets, and LLM API keys are stored in `.env`.

The `.env` file is excluded from version control through `.gitignore`.

`.env.example` is maintained as a safe template containing the required configuration variable names.