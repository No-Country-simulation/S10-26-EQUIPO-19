"""Contexto de búsqueda para mensajes de seguimiento.

Un mensaje corto ("¿cuál me recomiendas?") no describe una necesidad por sí
solo. Para buscar en el catálogo se antepone el último mensaje del usuario,
sin agregar llamadas al modelo.
"""

import re

from app.core.assistant_intents import (
    candidate_tool_tokens,
    has_reference,
    normalize_text,
)

# Marcadores que suelen depender del mensaje anterior.
_CONTEXT_MARKERS = re.compile(
    r"("
    r"\bcual\b|\bcuales\b|"
    r"\bese\b|\besa\b|\beso\b|\besos\b|\besas\b|"
    r"\beste\b|\besta\b|\besto\b|\bestos\b|\bestas\b|"
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

# La referencia ("esta herramienta") reemplaza al nombre del producto resuelto.
_REFERENCE_PHRASE = re.compile(
    r"\b(?:este|esta|estos|estas|ese|esa|esos|esas|"
    r"aquel|aquella|aquellos|aquellas)\s+"
    r"(?:repositorio|herramienta|proyecto|plataforma|tecnologia|servicio|"
    r"solucion|opcion|alternativa|producto)s?\b",
    re.IGNORECASE,
)

MAX_WORDS_WITHOUT_CONTEXT = 6
# Un mensaje largo ya describe su necesidad: no se mezcla con el anterior.
MAX_WORDS_WITH_CONTEXT = 15
MAX_PREVIOUS_CHARS = 600
MAX_RESOLUTION_MESSAGES = 6
MAX_RESOLUTION_CANDIDATES = 12


def _user_messages(conversation_history: list[dict] | None) -> list[str]:
    """Mensajes del usuario, del más antiguo al más reciente."""
    if not conversation_history:
        return []

    messages = []

    for item in conversation_history:
        if str(item.get("role", "")).lower() != "user":
            continue

        content = str(item.get("content") or "").strip()

        if content:
            messages.append(content)

    return messages



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


def resolve_reference_target(
    message: str,
    conversation_history: list[dict] | None,
    lookup,
) -> dict | None:
    """Resuelve "esta herramienta" al último producto del catálogo mencionado.

    Devuelve {"entry": <producto>, "query": <mensaje con el nombre>} o None si
    el mensaje no tiene una referencia o ningún antecedente del catálogo la
    satisface. `lookup` valida un candidato contra el catálogo.
    """
    cleaned = (message or "").strip()

    if not cleaned or not has_reference(cleaned):
        return None

    previous_messages = _user_messages(conversation_history)[
        -MAX_RESOLUTION_MESSAGES:
    ]

    for previous in reversed(previous_messages):
        candidates = candidate_tool_tokens(previous)[:MAX_RESOLUTION_CANDIDATES]

        for candidate in candidates:
            try:
                entry = lookup(candidate)
            except Exception:
                entry = None

            if not entry:
                continue

            target = entry.get("name") or entry.get("full_name") or candidate
            resolved = _REFERENCE_PHRASE.sub(target, cleaned, count=1)

            if resolved == cleaned:
                resolved = f"{target} {cleaned}"

            return {"entry": entry, "query": resolved}

    return None
