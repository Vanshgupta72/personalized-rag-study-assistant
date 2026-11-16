from typing import Any


def merge_preferences(
    saved_preferences: dict[str, Any],
    question: str,
) -> dict[str, Any]:
    """Merge saved preferences with request-scoped instructions."""

    profile = saved_preferences.get("learning_profile") or {}
    text = question.casefold()

    strategy = {
        "goal": profile.get("goal", "mixed"),
        "level": profile.get("level", "beginner"),
        "depth": profile.get("depth", "balanced"),
        "approach": profile.get("approach", "mixed"),
        "temporary_instruction": None,
        "scope": "persistent_preferences",
    }

    permanent_markers = (
        "from now on", "going forward", "always",
        "hamesha", "aaj se", "future mein",
    )
    temporary_markers = (
        "this time", "for this question", "just this once",
        "is baar", "sirf is question", "for now",
    )

    permanent_request = any(marker in text for marker in permanent_markers)
    temporary_request = any(marker in text for marker in temporary_markers)

    if permanent_request and not temporary_request:
        change_scope = "explicit_permanent_request"
    else:
        change_scope = "current_query"

    if any(term in text for term in (
        "short answer", "briefly", "in short", "2 marks",
        "concise", "short mein", "short me",
    )):
        strategy["depth"] = "concise"
        strategy["temporary_instruction"] = (
            "Give a concise answer focused on the requested question."
        )
        strategy["scope"] = "current_query"

    elif any(term in text for term in (
        "in detail", "detailed explanation", "step by step",
        "detail mein", "detail me",
    )):
        strategy["depth"] = "detailed"
        strategy["temporary_instruction"] = (
            "Explain the answer in detail with clear steps where useful."
        )
        strategy["scope"] = "current_query"

    language_change = None
    if permanent_request and not temporary_request:
        if "hinglish" in text:
            language_change = {"field": "preferred_language", "value": "Hinglish"}
        elif "hindi" in text:
            language_change = {"field": "preferred_language", "value": "Hindi"}
        elif "english" in text:
            language_change = {"field": "preferred_language", "value": "English"}

    depth_change = None
    if permanent_request and not temporary_request:
        if any(term in text for term in ("short answer", "briefly", "concise", "2 marks")):
            depth_change = {"field": "depth", "value": "concise"}
        elif any(term in text for term in ("in detail", "detailed", "step by step")):
            depth_change = {"field": "depth", "value": "detailed"}

    return {
        "preferred_language": saved_preferences.get("preferred_language", "English"),
        "explanation_style": saved_preferences.get("explanation_style", "simple"),
        "learning_profile": profile,
        "response_strategy": strategy,
        "preference_change_request": language_change or depth_change,
        "change_scope": change_scope,
        "learning_signal": {
            "type": "explicit_request" if permanent_request else "query_instruction",
            "confidence": 1.0 if permanent_request else 0.0,
            "persisted": False,
        },
    }
