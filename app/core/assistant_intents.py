"""Intenciones fijas del asistente que no necesitan llamar al modelo.

- Presentación de OpenBridge y de Toby.
- Referencias sin antecedente en una conversación nueva.
- Detección de nombres de herramientas para validarlas contra el catálogo.

Todas las funciones son puras: no acceden a la base de datos ni a Gemini.
"""

import re
import unicodedata

PRODUCT_ANSWER = (
    "OpenBridge es una plataforma que ayuda a los equipos técnicos de consultoras "
    "a convertir una necesidad de negocio en un stack open source justificado. "
    "Tiene un catálogo que revisa a diario la salud y la licencia de cada "
    "herramienta, y yo, Toby, soy su asistente: solo te recomiendo herramientas "
    "de ese catálogo."
)

# Presentación del asistente cuando preguntan quién es Toby.
TOBY_ANSWER = (
    "Hola, soy Toby, tu asistente de arquitectura 👋\n\n"
    "¡Bienvenido a OpenBridge! Cuéntame, ¿qué quieres construir? Aunque no sepas "
    "qué tecnologías necesitas, te propongo un stack open source con sus "
    "conexiones, solo con herramientas de nuestro catálogo revisadas a diario."
)

# Respuesta fija a un agradecimiento suelto.
THANKS_ANSWER = (
    "¡De nada! 😊 Cuando quieras, cuéntame otro proyecto y te propongo su stack "
    "open source."
)

REFERENCE_CLARIFICATION_ANSWER = (
    "No tengo contexto suficiente para saber a qué te refieres. ¿Me dices a qué "
    "herramienta o proyecto te refieres? Si está en el catálogo de OpenBridge, "
    "puedo compararla, incluirla en un stack o mostrarte su ficha."
)


def normalize_text(value: str) -> str:
    """Minúsculas, sin acentos y con espacios colapsados."""
    text = unicodedata.normalize("NFKD", (value or "").lower().strip())
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", text)


def _plain_text(value: str) -> str:
    """Texto normalizado sin signos: '¡Hola, Toby!' -> 'hola toby'."""
    plain = re.sub(r"[^a-z0-9 ]+", " ", normalize_text(value))
    return re.sub(r"\s+", " ", plain).strip()


_PRODUCT_TERMS = re.compile(r"\b(openbridge|toby)\b")

# Saludos sueltos: no piden nada más que la presentación del asistente.
_GREETINGS = frozenset(
    {
        "toby",
        "hola",
        "hola toby",
        "buenas",
        "buenas toby",
        "buenos dias",
        "buenos dias toby",
        "buen dia",
        "buen dia toby",
        "buenas tardes",
        "buenas tardes toby",
        "buenas noches",
        "buenas noches toby",
        "hey",
        "hey toby",
        "que tal",
        "que tal toby",
    }
)

# Preguntas sobre lo que Toby puede hacer.
_CAPABILITY_PATTERNS = re.compile(
    r"("
    r"\bque\s+puedes\s+hacer\b|"
    r"\bque\s+sabes\s+hacer\b|"
    r"\ben\s+que\s+(me\s+)?puedes\s+ayudar\b|"
    r"\bcomo\s+(me\s+)?puedes\s+ayudar\b|"
    r"\bhablame\s+de\s+ti\b|"
    r"\bpara\s+que\s+sirves\b"
    r")"
)

# Agradecimientos sueltos: no piden nada más.
_THANKS = frozenset(
    {
        "gracias",
        "gracias toby",
        "muchas gracias",
        "muchas gracias toby",
        "mil gracias",
        "mil gracias toby",
        "perfecto gracias",
        "perfecto gracias toby",
        "genial gracias",
        "genial gracias toby",
        "ok gracias",
        "ok gracias toby",
        "buenisimo gracias",
        "buenisimo gracias toby",
        "excelente gracias",
        "excelente gracias toby",
    }
)

# Preguntas sobre la identidad del asistente (Toby), no sobre el producto.
_SELF_IDENTITY_PATTERNS = re.compile(
    r"("
    r"\bquien\s+(sos|eres)\b|"
    r"\bquienes\s+son\s+ustedes\b|"
    r"\bquien\s+es\s+toby\b|"
    r"\b(sos|eres)\s+toby\b|"
    r"\bcomo\s+te\s+llamas\b|"
    r"\bcual\s+es\s+tu\s+nombre\b|"
    r"\bpresentate\b|\bte\s+presentas\b|"
    r"\bque\s+eres\s*[?!.]*$|"
    r"\b(hablame|contame|cuentame|decime)\s+(de|sobre|acerca\s+de)\s+"
    r"(vos|ti|toby)\b|"
    r"\b(sobre|acerca\s+de)\s+(vos|ti)\b|"
    r"\bde\s+(vos|ti)\b|"
    r"\bque\s+sabes\s+de\s+(vos|ti)\b|"
    r"\bsobre\s+vos\b"
    r")"
)

_PRESENTATION_CUES = re.compile(
    r"("
    r"\bque\s+(es|hace|significa)\b|"
    r"\bpara\s+que\s+sirve\b|"
    r"\bhablame\b|\bcontame\b|\bcuentame\b|\bpresentate\b|"
    r"\bquien\s+(es|son)\b|"
    r"\binformacion\s+(sobre|de)\b|"
    r"\bde\s+que\s+se\s+trata\b|"
    r"\bque\s+sabes\s+de\b"
    r")"
)

# Objeto de una presentación: solo el propio asistente o el producto. Evita que
# el nombre del asistente se tome como contexto de una petición real (Bug-N3-4).
_SELF_PRESENTATION_OBJECT = re.compile(
    r"\b(hablame|contame|cuentame|decime|presentate|presentas|"
    r"informacion|info)\b[^.!?]{0,24}?"
    r"\b(de|sobre|acerca\s+de)\s+"
    r"(vos|ti|toby|openbridge|el\s+producto|la\s+plataforma|el\s+asistente)\b"
)

# Pedidos que, aunque nombren a OpenBridge, necesitan el flujo normal.
_PRESENTATION_EXCLUSIONS = re.compile(
    r"(\bcompara\w*\b|\bcomparar\b|\bvs\b|\bversus\b|\bstack\b|"
    r"\brecomiend\w*\b|\brecomend\w*\b|\bprecio\w*\b|"
    r"\brepositorios?\b|\bherramientas?\b|\bproyectos?\b|"
    r"\btecnologias?\b|\bplataformas?\b|\bservicios?\b|"
    r"\bopciones?\b|\balternativas?\b|\bsoluciones?\b|"
    r"\bevaluacion\b|\bcomparacion\b|\bbase\s+de\s+datos\b)"
)

_DEICTIC_REFERENCE = re.compile(
    r"("
    r"\baquel\b|\baquella\b|\baquello\b|"
    r"\bese\b|\besa\b|\beso\b|\besos\b|\besas\b|"
    r"\beste\b|\besta\b|\besto\b|\bestos\b|\bestas\b|"
    r"\bel anterior\b|\bla anterior\b|"
    r"\blos anteriores\b|\blas anteriores\b|"
    r"\bel primero\b|\bla primera\b|"
    r"\bel segundo\b|\bla segunda\b|"
    r"\bel tercero\b|\bla tercera\b|"
    r"\bel mismo\b|\bla misma\b|"
    r"\bdicho\b|\bdicha\b"
    r")"
)

_REFERENCE_NOUN = re.compile(
    r"("
    r"\brepositorios?\b|\bherramientas?\b|\bproyectos?\b|"
    r"\bstack\b|\btecnologias?\b|\bopciones?\b|\balternativas?\b|"
    r"\bplataformas?\b|\bservicios?\b|\bbase de datos\b|"
    r"\bsoluciones?\b|\bevaluacion\b|\bcomparacion\b"
    r")"
)

_REMOTE_PAST_REFERENCE = re.compile(
    r"("
    r"\bcomo te (dije|comente|mencione)\b|"
    r"\blo (que )?te (dije|comente|mencione)\b|"
    r"\bmencionaste\b|\bdijiste\b|"
    r"\blo de antes\b|\blo anterior\b"
    r")"
)

# Un nombre con letras, números y los separadores habituales de un proyecto.
_CANDIDATE = r"[^\W_][\w.+#-]{1,29}"

_COMPARISON_PATTERNS = (
    re.compile(
        r"\b(?:compar[aá](?:me|r|la|las|los)?|"
        r"comp[aá]ra(?:me|la|las|los)|"
        r"comparaci[oó]n(?:es)?(?:\s+(?:de|entre))?|"
        r"diferencias?\s+entre)"
        r"\s+(?:el|la|los|las)?\s*"
        rf"({_CANDIDATE})"
        r"\s+(?:con|y|vs\.?|versus)\s+(?:el|la|los|las)?\s*"
        rf"({_CANDIDATE})",
        re.IGNORECASE,
    ),
    re.compile(
        rf"\b({_CANDIDATE})\s+(?:vs\.?|versus)\s+({_CANDIDATE})\b",
        re.IGNORECASE,
    ),
)

# Palabras que nunca identifican una herramienta del catálogo.
_GENERIC_TERMS = frozenset(
    {
        "a", "al", "algo", "algun", "alguna", "algunas", "algunos", "antes",
        "asi", "aunque", "bien", "cada", "como", "con", "contra", "cual",
        "cuales", "cuando", "cuanto", "de", "del", "desde", "donde", "dos",
        "el", "ella", "ellas", "ellos", "en", "entre", "era", "es", "esa",
        "esas", "ese", "eso", "esos", "esta", "estas", "este", "esto",
        "estos", "fue", "ha", "hasta", "hay", "la", "las", "le", "les",
        "lo", "los", "mas", "me", "mi", "mis", "mucho", "muy", "nada",
        "ni", "no", "nos", "nosotros", "o", "os", "otra", "otras", "otro",
        "otros", "para", "pero", "poco", "por", "porque", "que", "quien",
        "quienes", "se", "segun", "ser", "si", "sin", "sobre", "solo",
        "son", "su", "sus", "te", "tiene", "tienen", "todo", "todos",
        "tu", "tus", "un", "una", "unas", "uno", "unos", "usted",
        "ustedes", "vos", "y", "ya", "yo",
        # Referencias y valoraciones: no son nombres de herramientas.
        "aquel", "aquella", "aquello", "mejor", "peor",
        # Términos de negocio o comparación, no productos.
        "precio", "precios", "costo", "costos", "plan", "planes",
        "licencia", "licencias", "caracteristica", "caracteristicas",
        "funcionalidad", "funcionalidades", "ventaja", "ventajas",
        "desventaja", "desventajas", "rendimiento", "seguridad", "salud",
        "popularidad", "comunidad", "soporte", "opcion", "opciones",
        "alternativa", "alternativas", "herramienta", "herramientas",
        "proyecto", "proyectos", "stack", "tecnologia", "tecnologias",
        "producto", "productos", "servicio", "servicios", "plataforma",
        "plataformas", "repositorio", "repositorios", "solucion",
        "soluciones", "comparacion", "evaluacion", "caso", "casos",
        "negocio", "negocios", "app", "aplicacion", "web", "sistema",
        "sistemas", "openbridge", "toby",
    }
)

# Tecnologías de uso general: al preguntar "qué es X" no son productos del
# catálogo, pero en una comparación explícita sí se validan contra él.
_TECHNOLOGY_TERMS = frozenset(
    {
        "docker", "kubernetes", "k8s", "python", "javascript", "typescript",
        "java", "go", "golang", "rust", "php", "ruby", "api", "apis",
        "oauth", "oauth2", "sso", "sql", "nosql", "http", "https", "json",
        "yaml", "git", "github", "linux", "postgres", "postgresql",
        "mysql", "mongodb", "redis", "nginx", "apache", "embeddings",
        "rag", "llm", "ia", "ai", "react", "vue", "angular", "nextjs",
        "next.js", "django", "flask", "fastapi", "laravel", "spring",
    }
)


def is_toby_identity_request(text: str) -> bool:
    """True si el usuario saluda a Toby, pregunta quién es o qué puede hacer."""
    normalized = normalize_text(text)

    if not normalized:
        return False

    if _PRESENTATION_EXCLUSIONS.search(normalized):
        return False

    plain = _plain_text(text)

    if not plain:
        return False

    if plain in _GREETINGS:
        return True

    if len(plain.split()) > 14:
        return False

    if _SELF_IDENTITY_PATTERNS.search(plain):
        return True

    if _CAPABILITY_PATTERNS.search(plain):
        # "¿Qué puedes hacer con Keycloak?" pide una respuesta sobre la herramienta.
        if re.search(r"\bcon\s+[a-z0-9]", plain):
            return False

        # "¿Qué puedes hacer para un CRM?" también pide una respuesta sobre el pedido.
        if re.search(
            r"\bpara\s+(?:un|una|unos|unas|el|la|los|las|mi|tu|su|mis|tus|sus)\b",
            plain,
        ):
            return False

        return True

    return bool(
        _PRODUCT_TERMS.search(normalized)
        and re.search(r"\btoby\b", plain)
        and _SELF_PRESENTATION_OBJECT.search(plain)
    )


def is_thanks(text: str) -> bool:
    """True si el mensaje es solo un agradecimiento."""
    return _plain_text(text) in _THANKS


def is_product_presentation_request(text: str) -> bool:
    """True si el usuario pide una presentación de OpenBridge."""
    if is_toby_identity_request(text):
        return False

    normalized = normalize_text(text)

    if not normalized:
        return False

    stripped = normalized.strip(" .,;:!?¿¡\"'")

    if stripped == "openbridge":
        return True

    if not _PRODUCT_TERMS.search(normalized):
        return False

    if not _PRESENTATION_CUES.search(normalized):
        return False

    if _PRESENTATION_EXCLUSIONS.search(normalized):
        return False

    return len(normalized.split()) <= 14


def has_unresolved_reference(text: str, has_history: bool) -> bool:
    """True si el mensaje depende de un antecedente que no existe."""
    if has_history:
        return False

    normalized = normalize_text(text)

    if not normalized:
        return False

    if _REMOTE_PAST_REFERENCE.search(normalized):
        return True

    return has_reference(text)


def has_reference(text: str) -> bool:
    """True si el mensaje señala una herramienta o proyecto sin nombrarlo.

    "Hablame de esta herramienta" o "cuentame de este proyecto" necesitan un
    antecedente, exista o no historial: con historial se resuelve la entidad;
    sin historial (o sin entidad reconocible) corresponde pedir aclaración.
    """
    normalized = normalize_text(text)

    if not normalized:
        return False

    return bool(
        _DEICTIC_REFERENCE.search(normalized)
        and _REFERENCE_NOUN.search(normalized)
    )


def _clean_token(token: str) -> str:
    return (token or "").strip(" .,;:!?()[]{}<>\"'`")


def _is_candidate(token: str, allow_technologies: bool = True) -> bool:
    if not token:
        return False

    normalized = normalize_text(token)

    if len(normalized) < 3:
        return False

    if normalized.isdigit():
        return False

    if normalized in _GENERIC_TERMS:
        return False

    if not allow_technologies and normalized in _TECHNOLOGY_TERMS:
        return False

    return True


def extract_tool_mentions(text: str) -> list[str]:
    """Herramientas mencionadas en una comparación explícita.

    Solo se consideran comparaciones ("X con Y", "X vs Y"). Las menciones
    sueltas ("háblame de X") siguen el flujo normal: el prompt ya cubre las
    herramientas que no están en el catálogo.
    """
    if not text or not text.strip():
        return []

    mentions: list[str] = []
    seen: set[str] = set()

    def add(token: str) -> None:
        key = normalize_text(token)
        if key not in seen:
            seen.add(key)
            mentions.append(token)

    for pattern in _COMPARISON_PATTERNS:
        for match in pattern.finditer(text):
            pair = [_clean_token(group) for group in match.groups()]

            # Una comparación con un término genérico no identifica herramientas.
            if not all(_is_candidate(token, allow_technologies=True) for token in pair):
                continue

            for token in pair:
                add(token)

    return mentions


_CANDIDATE_TOKEN_SEARCH = re.compile(r"[^\W_][\w.+#-]{2,}", re.UNICODE)


def candidate_tool_tokens(text: str) -> list[str]:
    """Posibles nombres de herramienta en un texto, sin palabras genéricas.

    Se usa para resolver referencias ("esta herramienta") contra lo que el
    usuario ya mencionó, validando cada candidato con el índice del catálogo.
    """
    tokens: list[str] = []
    seen: set[str] = set()

    for match in _CANDIDATE_TOKEN_SEARCH.finditer(text or ""):
        token = _clean_token(match.group(0))

        if not _is_candidate(token, allow_technologies=True):
            continue

        key = normalize_text(token)

        if key in seen:
            continue

        seen.add(key)
        tokens.append(token)

    return tokens


def _quoted(items: list[str]) -> str:
    if len(items) == 1:
        return f"**{items[0]}**"

    return ", ".join(f"**{item}**" for item in items[:-1]) + f" y **{items[-1]}**"


def out_of_catalog_message(
    missing: list[str],
    present: dict | None = None,
    alternatives: list[dict] | None = None,
    present_label: str | None = None,
) -> str:
    """Respuesta fija cuando una herramienta pedida no está en el catálogo."""
    missing = [item for item in missing if item]

    if not missing:
        return ""

    verb = "está" if len(missing) == 1 else "están"
    phrase = f"{_quoted(missing)} no {verb} en el catálogo de OpenBridge"

    if present is None:
        return (
            f"{phrase}. Solo recomiendo herramientas del catálogo; si me dices qué "
            "necesitas resolver (por ejemplo, autenticación, pagos o notificaciones), "
            "te propongo las que sí están."
        )

    label = (
        present_label
        or present.get("name")
        or present.get("full_name")
        or "esa herramienta"
    )

    alternatives = alternatives or []

    if not alternatives:
        return (
            f"{phrase}, así que no puedo hacer esa comparación con evidencia del "
            f"catálogo.\n\nNo tengo una alternativa equivalente a **{label}** en el "
            "catálogo. Cuéntame qué función necesitas cubrir y te propongo las "
            "herramientas disponibles."
        )

    lines = [
        f"- **{alternative.get('name')}** ({alternative.get('full_name')})"
        for alternative in alternatives
    ]

    return (
        f"{phrase}, así que no puedo hacer esa comparación con evidencia del "
        f"catálogo.\n\nDel catálogo tengo estas alternativas en la misma categoría "
        f"que **{label}**:\n"
        + "\n".join(lines)
        + f"\n\n¿Quieres que compare **{label}** con alguna de ellas?"
    )
