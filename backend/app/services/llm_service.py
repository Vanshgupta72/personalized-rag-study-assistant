from typing import List, Dict

import httpx

from backend.app.core.config import settings


def generate_answer(
    question: str,
    context: str,
    conversation_history: List[Dict[str, str]] | None = None
) -> str:
    """
    Generate an answer using the configured Hugging Face LLM.

    The model receives:
    1. Previous conversation messages.
    2. Relevant study-material context.
    3. The student's current question.

    This allows the assistant to understand follow-up questions
    instead of treating every question as completely independent.
    """

    # Make sure an API token is configured.
    if not settings.LLM_API_KEY:
        raise RuntimeError(
            "LLM API key is not configured."
        )

    # System message defines the assistant's behavior.
    system_message = """
You are a personalized study assistant.

Answer the student's question using the provided study material
and relevant conversation history.

Rules:
- Use the provided study material as the primary factual source.
- Use conversation history to understand references and follow-up questions.
- Do not invent facts that are not supported by the study material.
- If the required information cannot be found, clearly say so.
- Explain answers in a clear and student-friendly way.
"""

    messages = [
        {
            "role": "system",
            "content": system_message
        }
    ]

    # Add previous conversation messages.
    if conversation_history:
        for message in conversation_history:
            messages.append(
                {
                    "role": message["role"],
                    "content": message["content"]
                }
            )

    # Add the current question together with retrieved context.
    user_message = f"""
STUDY MATERIAL:
{context}

CURRENT STUDENT QUESTION:
{question}
"""

    messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    headers = {
        "Authorization": f"Bearer {settings.LLM_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": settings.LLM_MODEL,
        "messages": messages,
        "stream": False
    }

    response = httpx.post(
        settings.LLM_API_URL,
        headers=headers,
        json=payload,
        timeout=60.0
    )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]["message"]["content"]