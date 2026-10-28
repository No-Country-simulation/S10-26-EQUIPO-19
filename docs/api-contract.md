# Contrato de API - OpenBridge Backend

- **Versión:** 1.0.0
- **Base URL:** `/api/v1` (Desarrollo local: `http://localhost:8000/api/v1`)
- **Formato:** `application/json; charset=utf-8`
- **Autenticación en MVP:** Ninguna (Catálogo público)

---

## 1. Convenciones y Códigos de Estado

| Código HTTP | Significado | Descripción |
|---|---|---|
| `200 OK` | Éxito | Solicitud procesada correctamente. |
| `400 Bad Request` | Error de cliente | Parámetros inválidos en la petición. |
| `404 Not Found` | No encontrado | El recurso solicitado no existe. |
| `422 Unprocessable Entity` | Error de validación | El cuerpo del request no cumple con el esquema esperado. |
| `500 Internal Error` | Error de servidor | Fallo inesperado en el backend o conexión con Supabase. |

---

## 2. Endpoints del Catálogo

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
Devuelve la lista paginada de repositorios aprobados para el catálogo principal.

- **Método:** `GET`
- **Ruta:** `/repositories`
- **Query Params:**
  - `page` *(int, default: 1)*: Número de página.
  - `page_size` *(int, default: 10, max: 50)*: Cantidad de items por página.
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
      }
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
      }
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
  - `q` *(string, opcional)*: Texto a buscar en nombre, descripción o tópicos.
  - `category_id` *(int, opcional)*: ID de la categoría a filtrar.
  - `language` *(string, opcional)*: Lenguaje principal (ej. `"Python"`, `"Rust"`, `"TypeScript"`).
  - `min_stars` *(int, opcional)*: Cantidad mínima de estrellas en GitHub.
  - `license` *(string, opcional)*: Licencia (ej. `"MIT"`, `"Apache-2.0"`). Se compara con `repositories.license`.
  - `health_status` *(string, opcional)*: Nivel de mantenimiento: `Activo`, `En riesgo` o `Abandonado`. Se compara con `metrics.health_status`. Los repositorios con `health_status` en `null` (fecha del último commit desconocida) no aparecen al aplicar este filtro.
  - `page` *(int, default: 1)*: Número de página.
  - `page_size` *(int, default: 10)*: Cantidad por página.
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
      }
    }
  ]
}
```

---

### 2.4 Ficha Técnica de Repositorio (Detalle)
Devuelve la ficha completa con métricas detalladas e ideas de integración relacionadas. Cada idea incluye los cinco campos que pide la consigna: tipo de integración, disparadores o webhooks, snippet de ejemplo, compatibilidad de stack y nivel de dificultad.

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
- **Respuesta `404 Not Found`:**
```json
{
  "detail": "El repositorio con id 999 no fue encontrado."
}
```

---

## 3. Asistente Consultor (RAG)

### 3.1 Consultar al Asistente
Recibe la pregunta del usuario en lenguaje natural y devuelve una respuesta con recomendaciones, fuentes citadas y la arquitectura recomendada en formato estructurado (componentes y conexiones) para que el frontend la dibuje con React Flow.

- **Método:** `POST`
- **Ruta:** `/assistant/chat`
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
        "health_status": "Activo",
        "justification": "Procesa documentos en Python sin servicios externos."
      },
      {
        "key": "vectores",
        "repository_id": 102,
        "full_name": "chroma-core/chroma",
        "role": "Guarda los embeddings y busca fragmentos similares",
        "license": "Apache-2.0",
        "health_status": "Activo",
        "justification": "Base vectorial ligera, con cliente oficial de Python y configuración mínima."
      },
      {
        "key": "orquestacion",
        "repository_id": 201,
        "full_name": "langchain-ai/langchain",
        "role": "Orquesta la búsqueda y la respuesta",
        "license": "MIT",
        "health_status": "Activo",
        "justification": "Integra Chroma y el modelo de lenguaje en pocas líneas."
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
      "msg": "El campo 'message' es obligatorio y no puede estar vacío.",
      "type": "value_error.missing"
    }
  ]
}
```