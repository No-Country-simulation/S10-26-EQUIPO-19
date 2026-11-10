# Contrato de API - OpenBridge Backend

- **Versión:** 1.0.0
- **Base URL:** `/api/v1`
  - **Producción:** `https://openbridge-rcv2.onrender.com/api/v1`
  - **Desarrollo local:** `http://localhost:8000/api/v1`
  - *(Las rutas operativas `/health` y `/github/*` se sirven desde la raíz del dominio, sin el prefijo `/api/v1`).*
- **Formato:** `application/json; charset=utf-8`
- **Autenticación en MVP:**
  - **Catálogo, Asistente y Compose:** Pública (sin autenticación).
  - **Sincronización de inventario (`POST /github/repositories/sync`):** Protegida mediante cabecera `X-API-Key`.

---

## 1. Convenciones, Códigos de Estado y Límites de Uso

### 1.1 Códigos de Estado HTTP

| Código HTTP | Significado | Descripción |
|---|---|---|
| `200 OK` | Éxito | Solicitud procesada correctamente. |
| `400 Bad Request` | Error de cliente | Parámetros inválidos en la petición (ej. cantidad de IDs en el comparador o formato inválido). |
| `401 Unauthorized` | No autorizado | Falta o es inválida la cabecera `X-API-Key` en endpoints protegidos. |
| `404 Not Found` | No encontrado | El recurso solicitado no existe. |
| `422 Unprocessable Entity` | Error de validación | El cuerpo o los parámetros de la petición no cumplen con el esquema esperado. |
| `429 Too Many Requests` | Límite excedido | Se superó el límite de solicitudes permitido en la ventana de 60 segundos (incluye cabecera `Retry-After`). |
| `500 Internal Error` | Error de servidor | Fallo inesperado en el backend. |
| `502 Bad Gateway` | Error de pasarela | Fallo al comunicarse con la API externa de GitHub. |
| `503 Service Unavailable` | Servicio no disponible | Base de datos (Supabase) o proveedor de IA (Gemini) no disponibles temporalmente, o tiempo de espera agotado. |

### 1.2 Límites de Solicitudes (Rate Limiting)

Todas las rutas públicas y de ingesta cuentan con limitación de tasa en ventana deslizante de 60 segundos (por IP de cliente y tope global de protección):

| Grupo de Endpoints | Límite por IP | Tope Global |
|---|---|---|
| Catálogo y Compose (`/api/v1/repositories*`, `/api/v1/compose`) | 60 req / 60s | 300 req / 60s |
| Asistente Consultor RAG (`/api/v1/assistant/chat`) | 10 req / 60s | 50 req / 60s |
| Consultas y Sincronización GitHub (`/github/*`) | 20 req / 60s | 100 req / 60s |

---

## 2. Endpoints del Catálogo (`/api/v1`)

### 2.1 Listar Categorías
Obtiene la taxonomía completa de categorías disponibles para filtros y navegación.

- **Método:** `GET`
- **Ruta:** `/categories`
- **Query Params:** Ninguno requerido.
- **Respuesta `200 OK`:**
```json
[
  {
    "id": 1,
    "name": "Búsqueda Vectorial",
    "repositories_count": 5
  },
  {
    "id": 2,
    "name": "IA y LLM",
    "repositories_count": 8
  },
  {
    "id": 3,
    "name": "Observabilidad y Monitoreo",
    "repositories_count": 6
  }
]
```

---

### 2.2 Listar Repositorios (Catálogo Paginado)
Devuelve la lista paginada de repositorios aprobados para el catálogo principal, incluyendo su categoría, métricas resumidas y alertas de riesgo (`alerts`) evaluadas automáticamente por licencia y estado de mantenimiento.

- **Método:** `GET`
- **Ruta:** `/repositories`
- **Query Params:**
  - `page` *(int, default: 1, min: 1)*: Número de página.
  - `page_size` *(int, default: 10, min: 1, max: 50)*: Cantidad de items por página.
  - `sort_by` *(string, default: "stars")*: Campo de ordenación (`stars`, `forks`, `last_commit_at`, `health_score`).
  - `order` *(string, default: "desc")*: Dirección (`asc` o `desc`).
- **Respuesta `200 OK`:**
```json
{
  "total": 42,
  "page": 1,
  "page_size": 2,
  "total_pages": 21,
  "items": [
    {
      "id": 101,
      "github_id": 10567832,
      "name": "qdrant",
      "full_name": "qdrant/qdrant",
      "url": "https://github.com/qdrant/qdrant",
      "description": "Vector Similarity Search Engine and Vector Database",
      "description_es": "Motor de búsqueda por similitud vectorial y base de datos vectorial para IA de alto rendimiento.",
      "language": "Rust",
      "license": "Apache-2.0",
      "stars": 19500,
      "forks": 1400,
      "topics": ["vector-search", "database", "rust", "machine-learning"],
      "last_commit_at": "2026-10-21T12:00:00Z",
      "pushed_at": "2026-10-21T18:30:00Z",
      "category": {
        "id": 1,
        "name": "Búsqueda Vectorial"
      },
      "metrics": {
        "health_score": 91,
        "health_status": "Activo"
      },
      "alerts": []
    },
    {
      "id": 102,
      "github_id": 23489110,
      "name": "chroma",
      "full_name": "chroma-core/chroma",
      "url": "https://github.com/chroma-core/chroma",
      "description": "the AI-native open-source embedding database",
      "description_es": "Base de datos de embeddings nativa para inteligencia artificial, ligera y de fácil integración.",
      "language": "Python",
      "license": "Apache-2.0",
      "stars": 14200,
      "forks": 1150,
      "topics": ["embedding", "database", "python", "ai"],
      "last_commit_at": "2026-10-20T12:00:00Z",
      "pushed_at": "2026-10-20T14:15:00Z",
      "category": {
        "id": 1,
        "name": "Búsqueda Vectorial"
      },
      "metrics": {
        "health_score": 92,
        "health_status": "Activo"
      },
      "alerts": []
    }
  ]
}
```

---

### 2.3 Búsqueda con Filtros
Permite filtrar el catálogo combinando búsqueda textual y filtros facetados.

- **Método:** `GET`
- **Ruta:** `/repositories/search`
- **Query Params:**
  - `q` *(string, opcional)*: Texto a buscar en nombre, nombre completo o descripción (en inglés y español).
  - `category_id` *(int, opcional, min: 1)*: ID de la categoría a filtrar.
  - `language` *(string, opcional)*: Lenguaje principal (ej. `"Python"`, `"Rust"`, `"TypeScript"`).
  - `min_stars` *(int, opcional, min: 0)*: Cantidad mínima de estrellas en GitHub.
  - `license` *(string, opcional)*: Licencia (ej. `"MIT"`, `"Apache-2.0"`). Se compara con `repositories.license`.
  - `health_status` *(string, opcional)*: Nivel de mantenimiento: `Activo`, `En riesgo` o `Abandonado`. Se compara con `metrics.health_status`. Los repositorios con `health_status` en `null` (fecha del último commit desconocida) no aparecen al aplicar este filtro.
  - `sort_by` *(string, default: "stars")*: Campo de ordenación: `stars`, `forks`, `last_commit_at` o `health_score`.
  - `order` *(string, default: "desc")*: Dirección de ordenación: `asc` o `desc`.
  - `page` *(int, default: 1, min: 1)*: Número de página.
  - `page_size` *(int, default: 10, min: 1, max: 50)*: Cantidad por página.
- **Ejemplo de petición con los 5 filtros:**  
  `GET /repositories/search?q=embedding&category_id=1&language=Python&license=Apache-2.0&health_status=Activo&min_stars=1000`
- **Respuesta `200 OK`:** (Estructura idéntica al listado paginado).
```json
{
  "total": 1,
  "page": 1,
  "page_size": 10,
  "total_pages": 1,
  "items": [
    {
      "id": 102,
      "github_id": 23489110,
      "name": "chroma",
      "full_name": "chroma-core/chroma",
      "url": "https://github.com/chroma-core/chroma",
      "description": "the AI-native open-source embedding database",
      "description_es": "Base de datos de embeddings nativa para inteligencia artificial, ligera y de fácil integración.",
      "language": "Python",
      "license": "Apache-2.0",
      "stars": 14200,
      "forks": 1150,
      "topics": ["embedding", "database", "python", "ai"],
      "last_commit_at": "2026-10-20T12:00:00Z",
      "pushed_at": "2026-10-20T14:15:00Z",
      "category": {
        "id": 1,
        "name": "Búsqueda Vectorial"
      },
      "metrics": {
        "health_score": 92,
        "health_status": "Activo"
      },
      "alerts": []
    }
  ]
}
```

---

### 2.4 Ficha Técnica de Repositorio (Detalle)
Devuelve la ficha completa con métricas detalladas, alertas de riesgo (`alerts`) e ideas de integración relacionadas. Incluye además `detected_stack` e `integration_methods_suggested`, que usa el asistente para recomendar y conectar herramientas. Cada idea incluye los cinco campos que pide la consigna: tipo de integración, disparadores o webhooks, snippet de ejemplo, compatibilidad de stack y nivel de dificultad.

- **Método:** `GET`
- **Ruta:** `/repositories/{id}`
- **Parámetros de ruta:**
  - `id` *(int, obligatorio)*: Identificador interno del repositorio.
- **Respuesta `200 OK`:**
```json
{
  "id": 101,
  "github_id": 10567832,
  "name": "qdrant",
  "full_name": "qdrant/qdrant",
  "url": "https://github.com/qdrant/qdrant",
  "homepage": "https://qdrant.tech",
  "description": "Vector Similarity Search Engine and Vector Database",
  "description_es": "Motor de búsqueda por similitud vectorial y base de datos vectorial para IA de alto rendimiento.",
  "license": "Apache-2.0",
  "language": "Rust",
  "topics": ["vector-search", "database", "rust", "machine-learning"],
  "detected_stack": ["Rust", "Docker", "REST API", "gRPC"],
  "integration_methods_suggested": ["API REST", "SDK / librería", "Docker"],
  "stars": 19500,
  "forks": 1400,
  "open_issues": 120,
  "has_issues": true,
  "issues_url": null,
  "archived": false,
  "maintainer_active": true,
  "last_commit_at": "2026-10-21T12:00:00Z",
  "pushed_at": "2026-10-21T18:30:00Z",
  "synced_at": "2026-10-22T08:00:00Z",
  "category": {
    "id": 1,
    "name": "Búsqueda Vectorial"
  },
  "metrics": {
    "health_score": 91,
    "health_status": "Activo",
    "health_score_details": {
      "maintenance": 30,
      "commit_activity": 21,
      "popularity": 15,
      "forks": 7
    },
    "commits_last_30_days": 42,
    "commits_last_90_days": 135,
    "commits_last_year": 580,
    "commit_activity_status": "available",
    "measured_at": "2026-10-22T08:00:00Z"
  },
  "alerts": [],
  "integrations": [
    {
      "id": 16,
      "code": "INT-016",
      "purpose": "Asistente que responde preguntas sobre documentos internos sin enviar datos a terceros.",
      "integration_type": "SDK / librería",
      "triggers_or_webhooks": "Al cargar documentos (indexación) y en cada pregunta del usuario.",
      "example_snippet": "from langchain_ollama import OllamaEmbeddings, ChatOllama\nfrom langchain_qdrant import QdrantVectorStore\n\nemb = OllamaEmbeddings(model=\"nomic-embed-text\", base_url=\"http://ollama:11434\")\nstore = QdrantVectorStore.from_documents(fragmentos, emb,\n    url=\"http://qdrant:6333\", collection_name=\"docs_internos\")\nllm = ChatOllama(model=\"llama3.1\", base_url=\"http://ollama:11434\")\n\npregunta = \"¿Cuál es la política de vacaciones?\"\ncontexto = store.similarity_search(pregunta, k=4)\nrespuesta = llm.invoke(f\"Responde solo con este contexto:\\n{contexto}\\n\\nPregunta: {pregunta}\")",
      "compatible_stack": ["Python 3.10+", "LangChain", "Ollama", "Qdrant", "Docker"],
      "main_steps": [
        "Extraer y fragmentar los documentos.",
        "Indexarlos en Qdrant con embeddings de Ollama.",
        "Recuperar los fragmentos más parecidos a la pregunta.",
        "Generar la respuesta con el modelo local usando solo ese contexto."
      ],
      "difficulty": "Media",
      "role": "Almacenamiento y búsqueda de los fragmentos de los documentos",
      "documentation_url": "https://docs.langchain.com/oss/python/integrations/vectorstores/qdrant",
      "related_repositories": [
        {
          "id": 201,
          "full_name": "langchain-ai/langchain",
          "role": "Orquestación del flujo RAG"
        },
        {
          "id": 202,
          "full_name": "ollama/ollama",
          "role": "Embeddings y respuestas con un modelo local"
        }
      ],
      "business_cases": [
        {
          "id": 13,
          "name": "Un asistente con IA que responde preguntas sobre documentos internos."
        },
        {
          "id": 12,
          "name": "Una mesa de ayuda con chat y respuestas automáticas con IA."
        }
      ]
    }
  ]
}
```
- **Nota sobre `alerts`:** cuando un repositorio presenta riesgos de licencia (ej. `AGPL-3.0`, `GPL-3.0`, `SSPL` o sin licencia) o de mantenimiento (`En riesgo`, `Abandonado` o `archived: true`), la lista `alerts` incluye objetos con la estructura:
```json
{
  "type": "license",
  "title": "Obligación de compartir mejoras",
  "message": "Usa AGPL-3.0. Si la modificas y la ofreces como servicio en la nube, debes publicar el código de esos cambios."
}
```
- **Nota sobre `documentation_url`:** en cada idea de integración puede traer varios enlaces separados por ` ; ` (normalmente uno por cada repositorio de la integración). Ejemplo: `"https://docs.paperless-ngx.com/api ; https://docs.documenso.com/docs/developers/webhooks/events"`. El frontend los separa y muestra un enlace por cada uno.
- **Respuesta `404 Not Found`:**
```json
{
  "detail": "El repositorio con id 999 no fue encontrado."
}
```

---

### 2.5 Comparar Repositorios Lado a Lado
Permite comparar de 2 a 3 herramientas lado a lado devolviendo sus fichas técnicas completas, métricas detalladas e indicando si pertenecen a la misma categoría funcional.

- **Método:** `GET`
- **Ruta:** `/repositories/compare`
- **Query Params:**
  - `ids` *(list[string] o string separado por comas, obligatorio)*: Lista de 2 o 3 IDs de repositorios a comparar. Soporta formato separado por comas (`?ids=101,102`) o parámetros repetidos (`?ids=101&ids=102`).
- **Respuesta `200 OK`:**
```json
{
  "repositories": [
    {
      "id": 101,
      "full_name": "qdrant/qdrant",
      "name": "qdrant",
      "...": "Estructura completa de RepositoryDetailResponse (igual a GET /repositories/{id})"
    },
    {
      "id": 102,
      "full_name": "chroma-core/chroma",
      "name": "chroma",
      "...": "Estructura completa de RepositoryDetailResponse (igual a GET /repositories/{id})"
    }
  ],
  "same_category": true,
  "category_name": "Búsqueda Vectorial"
}
```
- **Respuesta `400 Bad Request` (Cantidad inválida, IDs duplicados o formato no numérico):**
```json
{
  "detail": "Se requieren al menos 2 repositorios para realizar la comparación."
}
```
- **Respuesta `404 Not Found` (Uno o más repositorios no existen):**
```json
{
  "detail": "No se encontraron los siguientes repositorios: 999."
}
```

---

## 3. Asistente Consultor (RAG) y Generador Compose (`/api/v1`)

### 3.1 Consultar al Asistente
Recibe la pregunta del usuario en lenguaje natural y devuelve una respuesta con recomendaciones y fuentes citadas. Devuelve además la arquitectura recomendada en formato estructurado (componentes y conexiones) para que el frontend la dibuje con React Flow. Cada componente incluye sus alertas de riesgo (`alerts`) y puntaje de salud (`health_score`), y cada conexión indica si corresponde a una idea de integración aprobada del catálogo (`verified: true` e `integration_code`) o si es una propuesta de la IA (`verified: false`). El bloque `architecture` puede ser `null` cuando la consulta no genera una arquitectura.

- **Método:** `POST`
- **Ruta:** `/assistant/chat`
- **Validaciones del cuerpo de la petición:**
  - `message` *(string, obligatorio, entre 1 y 2000 caracteres)*: Pregunta o consulta del usuario.
  - `conversation_history` *(array, opcional, máximo 20 mensajes)*: Historial previo de la conversación. Cada mensaje requiere `role` (`"user"` o `"assistant"`) y `content` *(entre 1 y 4000 caracteres)*.
- **Cuerpo de la petición (Request Body):**
```json
{
  "message": "¿Qué base de datos vectorial de código abierto me recomiendan si mi stack principal es Python y busco simplicidad?",
  "conversation_history": [
    {
      "role": "user",
      "content": "Hola, estoy evaluando opciones para un proyecto de IA."
    },
    {
      "role": "assistant",
      "content": "¡Hola! Con gusto te ayudo a comparar y elegir herramientas open source según tus necesidades técnicas."
    }
  ]
}
```
- **Respuesta `200 OK`:**
```json
{
  "answer": "Para un entorno donde prima la simplicidad y el uso directo con Python, te recomiendo **Chroma**. Es ligera, se ejecuta en memoria o cliente/servidor y requiere una configuración mínima. Si en el futuro necesitas escalar a producción masiva con millones de vectores y alta concurrencia, **Qdrant** es una excelente alternativa en Rust con cliente oficial de Python.",
  "sources": [
    {
      "repository_id": 102,
      "name": "chroma",
      "full_name": "chroma-core/chroma",
      "url": "https://github.com/chroma-core/chroma",
      "relevance_score": 0.94
    },
    {
      "repository_id": 101,
      "name": "qdrant",
      "full_name": "qdrant/qdrant",
      "url": "https://github.com/qdrant/qdrant",
      "relevance_score": 0.88
    }
  ],
  "suggested_questions": [
    "¿Cómo integrar Chroma con LangChain?",
    "¿Cuáles son las diferencias de rendimiento entre Qdrant y Chroma?"
  ],
  "architecture": {
    "components": [
      {
        "key": "docs",
        "repository_id": 203,
        "full_name": "Unstructured-IO/unstructured",
        "role": "Extrae el texto de manuales y PDF",
        "license": "Apache-2.0",
        "health_score": 89,
        "health_status": "Activo",
        "justification": "Procesa documentos en Python sin servicios externos.",
        "alerts": []
      },
      {
        "key": "vectores",
        "repository_id": 102,
        "full_name": "chroma-core/chroma",
        "role": "Guarda los embeddings y busca fragmentos similares",
        "license": "Apache-2.0",
        "health_score": 92,
        "health_status": "Activo",
        "justification": "Base vectorial ligera, con cliente oficial de Python y configuración mínima.",
        "alerts": []
      },
      {
        "key": "orquestacion",
        "repository_id": 201,
        "full_name": "langchain-ai/langchain",
        "role": "Orquesta la búsqueda y la respuesta",
        "license": "MIT",
        "health_score": 95,
        "health_status": "Activo",
        "justification": "Integra Chroma y el modelo de lenguaje en pocas líneas.",
        "alerts": []
      }
    ],
    "connections": [
      {
        "from": "docs",
        "to": "vectores",
        "label": "Envía los fragmentos de texto para indexarlos",
        "verified": true,
        "integration_code": "INT-047"
      },
      {
        "from": "orquestacion",
        "to": "vectores",
        "label": "Consulta los fragmentos relevantes para cada pregunta",
        "verified": false,
        "integration_code": null
      }
    ]
  }
}
```
- **Respuesta `422 Unprocessable Entity` (Error de validación):**
```json
{
  "detail": [
    {
      "loc": ["body", "message"],
      "msg": "String should have at least 1 character",
      "type": "string_too_short"
    }
  ]
}
```
- **Respuesta `429 Too Many Requests` (Límite de solicitudes excedido):**
```json
{
  "detail": "Límite de solicitudes excedido (10 req/60s). Reintente en 45 segundos."
}
```
- **Respuesta `503 Service Unavailable` (Tiempo de espera agotado o servicio no disponible):**
```json
{
  "detail": "El asistente no está disponible en este momento."
}
```

---

### 3.2 Generar Docker Compose del Stack Recomendado
Genera un archivo `docker-compose.yml` funcional a partir de la lista de repositorios (`owner/repo`) de un stack recomendado, empleando únicamente imágenes oficiales con versión fija y resolviendo dependencias entre servicios del catálogo.

- **Método:** `POST`
- **Ruta:** `/compose`
- **Validaciones del cuerpo de la petición:**
  - `repositories` *(list[string], obligatorio, entre 1 y 10 elementos)*: Nombres completos de los repositorios en formato `owner/repo` (máximo 140 caracteres por elemento).
- **Cuerpo de la petición (Request Body):**
```json
{
  "repositories": [
    "qdrant/qdrant",
    "langchain-ai/langchain"
  ]
}
```
- **Respuesta `200 OK`:**
```json
{
  "filename": "docker-compose.yml",
  "content": "services:\n  qdrant:\n    image: qdrant/qdrant:v1.13.4\n    ports:\n    - 6333:6333\n    - 6334:6334\n",
  "services": [
    {
      "full_name": "qdrant/qdrant",
      "service": "qdrant",
      "image": "qdrant/qdrant:v1.13.4",
      "ports": ["6333:6333", "6334:6334"]
    }
  ],
  "skipped": [
    {
      "full_name": "langchain-ai/langchain",
      "reason": "Es una librería ejecutable en código fuente y se instala como dependencia, no como un servicio en Docker Compose."
    }
  ],
  "warnings": []
}
```
- **Respuesta `422 Unprocessable Entity`:**
```json
{
  "detail": "El formato del repositorio 'invalido' es inválido. Debe ser 'owner/repo'."
}
```

---

## 4. Estado del Servicio e Ingesta de GitHub (Rutas Raíz)

*(Nota: Estas rutas cuelgan directamente de la raíz del servidor, fuera del prefijo `/api/v1`).*

### 4.1 Estado del Servicio (Health Check)
Verifica que el backend se encuentre activo.

- **Método:** `GET`
- **Ruta:** `/health`
- **Respuesta `200 OK`:**
```json
{
  "status": "ok",
  "message": "El backend de OpenBridge está activo y funcionando"
}
```

---

### 4.2 Consultar Datos Enriquecidos de un Repositorio en GitHub
Consulta la API de GitHub y devuelve los metadatos enriquecidos y el cálculo de salud de un repositorio específico.

- **Método:** `GET`
- **Ruta:** `/github/repository/{owner}/{repo}`
- **Parámetros de ruta:**
  - `owner` *(string, obligatorio)*: Propietario u organización en GitHub (solo caracteres alfanuméricos, guiones y puntos).
  - `repo` *(string, obligatorio)*: Nombre del repositorio en GitHub.
- **Respuestas:** `200 OK` con los metadatos enriquecidos del repositorio, `400 Bad Request` si el identificador no es válido, `404 Not Found` si no existe en GitHub, `429 Too Many Requests` o `502 Bad Gateway`.

---

### 4.3 Sincronizar Inventario de Repositorios
Ejecuta el proceso de ingesta y actualización de repositorios hacia Supabase a partir del inventario curado.

- **Método:** `POST`
- **Ruta:** `/github/repositories/sync`
- **Cabeceras requeridas:**
  - `X-API-Key`: Clave secreta configurada en `SYNC_API_KEY`.
- **Query Params:**
  - `limit` *(int, opcional, min: 1)*: Cantidad máxima de repositorios a sincronizar en la ejecución.
- **Respuesta `200 OK`:**
```json
{
  "total": 3,
  "successful": 3,
  "failed": 0,
  "repositories": []
}
```
- **Respuesta `401 Unauthorized`:**
```json
{
  "detail": "No autorizado: se requiere un encabezado 'X-API-Key' válido y la clave debe estar configurada en el servidor."
}
```

- **Respuesta `429 Too Many Requests` (Límite de solicitudes excedido):**
```json
{
  "detail": "Límite de solicitudes excedido (10 req/60s). Reintente en 45 segundos."
}
```
- **Respuesta `503 Service Unavailable` (Tiempo de espera agotado o servicio no disponible):**
```json
{
  "detail": "El asistente no está disponible en este momento."
}
```

---

### 3.2 Generar Docker Compose del Stack Recomendado
Genera un archivo `docker-compose.yml` funcional a partir de la lista de repositorios (`owner/repo`) de un stack recomendado, empleando únicamente imágenes oficiales con versión fija y resolviendo dependencias entre servicios del catálogo.

- **Método:** `POST`
- **Ruta:** `/compose`
- **Validaciones del cuerpo de la petición:**
  - `repositories` *(list[string], obligatorio, entre 1 y 10 elementos)*: Nombres completos de los repositorios en formato `owner/repo` (máximo 140 caracteres por elemento).
- **Cuerpo de la petición (Request Body):**
```json
{
  "repositories": [
    "qdrant/qdrant",
    "langchain-ai/langchain"
  ]
}
```
- **Respuesta `200 OK`:**
```json
{
  "filename": "docker-compose.yml",
  "content": "services:\n  qdrant:\n    image: qdrant/qdrant:v1.13.4\n    ports:\n    - 6333:6333\n    - 6334:6334\n",
  "services": [
    {
      "full_name": "qdrant/qdrant",
      "service": "qdrant",
      "image": "qdrant/qdrant:v1.13.4",
      "ports": ["6333:6333", "6334:6334"]
    }
  ],
  "skipped": [
    {
      "full_name": "langchain-ai/langchain",
      "reason": "Es una librería ejecutable en código fuente y se instala como dependencia, no como un servicio en Docker Compose."
    }
  ],
  "warnings": []
}
```
- **Respuesta `422 Unprocessable Entity`:**
```json
{
  "detail": "El formato del repositorio 'invalido' es inválido. Debe ser 'owner/repo'."
}
```

---

## 4. Estado del Servicio e Ingesta de GitHub (Rutas Raíz)

*(Nota: Estas rutas cuelgan directamente de la raíz del servidor, fuera del prefijo `/api/v1`).*

### 4.1 Estado del Servicio (Health Check)
Verifica que el backend se encuentre activo.

- **Método:** `GET`
- **Ruta:** `/health`
- **Respuesta `200 OK`:**
```json
{
  "status": "ok",
  "message": "El backend de OpenBridge está activo y funcionando"
}
```

---

### 4.2 Consultar Datos Enriquecidos de un Repositorio en GitHub
Consulta la API de GitHub y devuelve los metadatos enriquecidos y el cálculo de salud de un repositorio específico.

- **Método:** `GET`
- **Ruta:** `/github/repository/{owner}/{repo}`
- **Parámetros de ruta:**
  - `owner` *(string, obligatorio)*: Propietario u organización en GitHub (solo caracteres alfanuméricos, guiones y puntos).
  - `repo` *(string, obligatorio)*: Nombre del repositorio en GitHub.
- **Respuestas:** `200 OK` con los metadatos enriquecidos del repositorio, `400 Bad Request` si el identificador no es válido, `404 Not Found` si no existe en GitHub, `429 Too Many Requests` o `502 Bad Gateway`.

---

### 4.3 Sincronizar Inventario de Repositorios
Ejecuta el proceso de ingesta y actualización de repositorios hacia Supabase a partir del inventario curado.

- **Método:** `POST`
- **Ruta:** `/github/repositories/sync`
- **Cabeceras requeridas:**
  - `X-API-Key`: Clave secreta configurada en `SYNC_API_KEY`.
- **Query Params:**
  - `limit` *(int, opcional, min: 1)*: Cantidad máxima de repositorios a sincronizar en la ejecución.
- **Respuesta `200 OK`:**
```json
{
  "total": 3,
  "successful": 3,
  "failed": 0,
  "repositories": []
}
```
- **Respuesta `401 Unauthorized`:**
```json
{
  "detail": "No autorizado: se requiere un encabezado 'X-API-Key' válido y la clave debe estar configurada en el servidor."
}
```