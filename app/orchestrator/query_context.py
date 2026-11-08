"""Contexto de búsqueda para mensajes de seguimiento.

Un mensaje corto ("¿cuál me recomiendas?") no describe una necesidad por sí
solo. Para buscar en el catálogo se antepone el último mensaje del usuario,
sin agregar llamadas al modelo.
"""

import re

from app.core.assistant_intents import normalize_text

# Marcadores que suelen depender del mensaje anterior.
_CONTEXT_MARKERS = re.compile(
    r"("
    r"\bcual\b|\bcuales\b|"
    r"\bese\b|\besa\b|\beso\b|\besos\b|\besas\b|"
    r"\baquel\b|\baquella\b|\baquello\b|"
    r"\bel anterior\b|\bla anterior\b|"
    r"\blos anteriores\b|\blas anteriores\b|"
    r"\bel primero\b|\bla primera\b|"
    r"\bel segundo\b|\bla segunda\b|"
    r"\bel tercero\b|\bla tercera\b|"
    r"\bel mismo\b|\bla misma\b|"
    r"\brecomiendame\b|\bmencionaste\b|\bdijiste\b"
    r")"
)

MAX_WORDS_WITHOUT_CONTEXT = 6
# Un mensaje largo ya describe su necesidad: no se mezcla con el anterior.
MAX_WORDS_WITH_CONTEXT = 15
MAX_PREVIOUS_CHARS = 600


def last_user_message(conversation_history: list[dict] | None) -> str | None:
    """Último mensaje del usuario en el historial, o None."""
    if not conversation_history:
        return None

    for item in reversed(conversation_history):
        if str(item.get("role", "")).lower() != "user":
            continue

        content = str(item.get("content") or "").strip()

        if content:
            return content

    return None


def is_context_dependent(message: str) -> bool:
    """True si el mensaje no se entiende sin el mensaje anterior."""
    normalized = normalize_text(message)

    if not normalized:
        return False

    words = len(normalized.split())

    if words > MAX_WORDS_WITH_CONTEXT:
        return False

    if words <= MAX_WORDS_WITHOUT_CONTEXT:
        return True

    return bool(_CONTEXT_MARKERS.search(normalized))


def build_retrieval_query(
    message: str,
    conversation_history: list[dict] | None,
) -> str:
    """Texto usado para buscar en el catálogo (no reemplaza al mensaje original)."""
    cleaned = (message or "").strip()
    previous = last_user_message(conversation_history)

    if not previous or not is_context_dependent(cleaned):
        return cleaned

    return f"{previous[:MAX_PREVIOUS_CHARS].strip()}\n{cleaned}"
