import re
import unicodedata


class RequirementsAnalyzer:

    LANGUAGES = {
        "python": "Python",
        "javascript": "JavaScript",
        "typescript": "TypeScript",
        "java": "Java",
        "go": "Go",
        "golang": "Go",
        "rust": "Rust",
        "php": "PHP",
        "ruby": "Ruby",
        "c#": "C#",
        "c++": "C++",
    }

    TECHNOLOGIES = {
        "oauth2": ["oauth2", "oauth 2.0"],
        "sso": ["sso", "single sign-on"],
        "docker": ["docker"],
        "kubernetes": ["kubernetes", "k8s"],
        "postgresql": ["postgresql", "postgres"],
        "redis": ["redis"],
        "mongodb": ["mongodb", "mongo"],
        "supabase": ["supabase"],
        "fastapi": ["fastapi"],
        "django": ["django"],
        "react": ["react"],
        "next.js": ["next.js", "nextjs"],
        "langchain": ["langchain"],
        "qdrant": ["qdrant"],
        "chromadb": ["chromadb", "chroma"],
    }

    FUNCTIONALITIES = {
        "autenticación": [
            "autenticación",
            "authentication",
            "auth",
            "login",
            "inicio de sesión",
        ],
        "gestión de usuarios": [
            "gestión de usuarios",
            "gestionar usuarios",
            "administración de usuarios",
            "administrar usuarios",
            "user management",
            "manage users",
            "users",
        ],
        "gestión de bases de datos": [
            "gestión de bases de datos",
            "gestionar bases de datos",
            "administración de bases de datos",
            "administrar bases de datos",
            "database management",
            "database administration",
            "database management system",
            "gestión de datos",
        ],
        "desarrollo de APIs": [
            "desarrollo de apis",
            "desarrollar apis",
            "crear apis",
            "api development",
            "api creation",
            "api",
            "apis",
            "rest api",
            "restful api",
            "graphql",
            "endpoints",
        ],
        "catálogo de productos": [
            "catálogo de productos",
            "catalogo de productos",
            "catálogo",
            "catalogo",
            "product catalog",
            "product management",
            "gestión de productos",
            "gestionar productos",
            "catálogos de productos",
            "catalogos de productos",
            "catálogos",
            "catalogos",
        ],
        "gestión de pedidos": [
            "gestión de pedidos",
            "gestionar pedidos",
            "administración de pedidos",
            "administrar pedidos",
            "procesamiento de pedidos",
            "order management",
            "order processing",
            "orders",
            "pedidos",
            "gestionar pedidos",
            "administrar pedidos",
        ],
        "gestión de pagos": [
            "gestión de pagos",
            "gestionar pagos",
            "procesamiento de pagos",
            "payment processing",
            "payment management",
            "payments",
            "pasarelas de pago",
            "payment gateways",
            "pagos",
            "gestionar pagos",
            "administrar pagos",
        ],
        "notificaciones": [
            "notificaciones",
            "notificación",
            "notifications",
            "notification system",
            "email notifications",
            "sms",
            "push notifications",
        ],
        "logística y envíos": [
            "logística",
            "logistica",
            "gestión logística",
            "gestion logistica",
            "gestión de envíos",
            "gestion de envios",
            "gestionar envíos",
            "envíos",
            "envios",
            "shipping",
            "fulfillment",
            "delivery management",
        ],
        "gestión de inventario": [
            "gestión de inventario",
            "gestion de inventario",
            "gestionar inventario",
            "control de stock",
            "gestión de stock",
            "inventory management",
            "inventory",
            "stock management",
        ],
        "integración de servicios externos": [
            "integración de servicios externos",
            "integracion de servicios externos",
            "integrar servicios externos",
            "integración con servicios externos",
            "integraciones externas",
            "third-party integrations",
            "external service integration",
        ],
        "base de datos vectorial": [
            "base vectorial",
            "vector database",
            "vector store",
            "embeddings",
        ],
        "búsqueda": [
            "búsqueda",
            "search",
            "buscador",
            "retrieval",
        ],
        "procesamiento de documentos": [
            "procesamiento de documentos",
            "document processing",
            "pdf",
            "extracción de texto",
        ],
        "inteligencia artificial": [
            "inteligencia artificial",
            "artificial intelligence",
            "machine learning",
            "llm",
        ],
    }

    @staticmethod
    def _normalize(text: str) -> str:
        text = text.lower().strip()
        text = unicodedata.normalize("NFKD", text)

        text = "".join(
            char for char in text
            if not unicodedata.combining(char)
        )

        return re.sub(r"\s+", " ", text)

    @staticmethod
    def _contains_term(text: str, term: str) -> bool:
        pattern = rf"(?<!\w){re.escape(term)}(?!\w)"
        return bool(re.search(pattern, text))

    def analyze(self, query: str) -> dict:

        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        normalized_query = self._normalize(query)

        language = None

        for keyword, language_name in self.LANGUAGES.items():
            if self._contains_term(normalized_query, keyword):
                language = language_name
                break

        technologies = []

        for technology, aliases in self.TECHNOLOGIES.items():
            if any(
                self._contains_term(
                    normalized_query,
                    self._normalize(alias),
                )
                for alias in aliases
            ):
                technologies.append(technology)

        functionality = []

        for feature, aliases in self.FUNCTIONALITIES.items():
            if any(
                self._contains_term(
                    normalized_query,
                    self._normalize(alias),
                )
                for alias in aliases
            ):
                functionality.append(feature)

        return {
            "original_query": query.strip(),
            "technologies": technologies or None,
            "functionality": functionality,
            "mandatory_requirements": {
                "technologies": technologies,
                "functionality": functionality,
                "language": language,
            },
            "language": language,
            "category_slug": None,
            "license": None,
            "min_stars": None,
            "min_health_score": None,
            "exclude_archived": True,
        }
