// Datos de ejemplo para desarrollar y probar la interfaz mientras la API no esté disponible.
// Se activan con NEXT_PUBLIC_USE_MOCK=true (ver .env.example). Las métricas no son reales.
import type {
  Category,
  Integration,
  ListParams,
  PaginatedRepositories,
  RepositoryDetail,
  RepositoryListItem,
  SearchParams,
} from "@/types/api";

// Taxonomía oficial, en el mismo orden e id que la lista de respaldo del backend (app/routers/categories.py).
const NAMES = [
  "Autenticación", "Base de Datos y Backend", "Pagos y Comercio", "IA y LLM", "Geolocalización y Logística",
  "Analítica", "Notificaciones y Comunicación", "Herramientas de Negocio", "Seguridad y Secretos", "Búsqueda",
  "Observabilidad y Monitoreo", "Despliegue (PaaS)", "Video y Tiempo Real", "IoT y Series de Tiempo", "Búsqueda Vectorial",
  "Almacenamiento de Archivos", "Mensajería y Colas", "Automatización y Workflows", "CMS y Contenido", "Feature Flags",
  "API Gateway y Proxy", "Herramientas para APIs", "Paneles Internos y Low-code", "UI y Componentes", "Educación (LMS)",
];
const cat = (name: string) => ({ id: NAMES.indexOf(name) + 1, name });

type Seed = Omit<RepositoryListItem, "github_id" | "url" | "pushed_at" | "description"> & { description?: string | null };

const SEEDS: Seed[] = [
  { id: 101, name: "qdrant", full_name: "qdrant/qdrant", description_es: "Motor de búsqueda por similitud vectorial y base de datos vectorial para IA de alto rendimiento.", language: "Rust", license: "Apache-2.0", stars: 19500, forks: 1400, topics: ["vector-search", "database", "rust"], last_commit_at: "2026-10-21T12:00:00Z", category: cat("Búsqueda Vectorial"), metrics: { health_score: 91, health_status: "Activo" } },
  { id: 102, name: "chroma", full_name: "chroma-core/chroma", description_es: "Base de datos de embeddings nativa para inteligencia artificial, ligera y de fácil integración.", language: "Python", license: "Apache-2.0", stars: 14200, forks: 1150, topics: ["embedding", "database", "python"], last_commit_at: "2026-10-20T12:00:00Z", category: cat("Búsqueda Vectorial"), metrics: { health_score: 92, health_status: "Activo" } },
  { id: 103, name: "keycloak", full_name: "keycloak/keycloak", description_es: "Gestión de identidades y accesos con inicio de sesión único (SSO), OIDC y SAML.", language: "Java", license: "Apache-2.0", stars: 25000, forks: 7000, topics: ["sso", "oidc", "authentication"], last_commit_at: "2026-10-22T09:00:00Z", category: cat("Autenticación"), metrics: { health_score: 95, health_status: "Activo" } },
  { id: 104, name: "supabase", full_name: "supabase/supabase", description_es: "Postgres con API automática, autenticación, almacenamiento y pgvector listos para usar.", language: "TypeScript", license: "Apache-2.0", stars: 80000, forks: 8000, topics: ["postgres", "backend", "realtime"], last_commit_at: "2026-10-22T15:00:00Z", category: cat("Base de Datos y Backend"), metrics: { health_score: 97, health_status: "Activo" } },
  { id: 105, name: "meilisearch", full_name: "meilisearch/meilisearch", description_es: "Motor de búsqueda rápido con tolerancia a errores de escritura.", language: "Rust", license: "MIT", stars: 50000, forks: 1900, topics: ["search-engine", "full-text-search"], last_commit_at: "2026-10-20T10:00:00Z", category: cat("Búsqueda"), metrics: { health_score: 93, health_status: "Activo" } },
  { id: 106, name: "ollama", full_name: "ollama/ollama", description_es: "Ejecuta modelos de lenguaje abiertos en tu propia máquina o servidor.", language: "Go", license: "MIT", stars: 100000, forks: 8500, topics: ["llm", "llama", "local-ai"], last_commit_at: "2026-10-22T18:00:00Z", category: cat("IA y LLM"), metrics: { health_score: 95, health_status: "Activo" } },
  { id: 107, name: "langchain", full_name: "langchain-ai/langchain", description_es: "Framework para encadenar modelos, herramientas y recuperación de datos.", language: "Python", license: "MIT", stars: 100000, forks: 16000, topics: ["llm", "rag", "agents"], last_commit_at: "2026-10-22T11:00:00Z", category: cat("IA y LLM"), metrics: { health_score: 92, health_status: "Activo" } },
  { id: 108, name: "medusa", full_name: "medusajs/medusa", description_es: "Backend de comercio electrónico modular con pagos, carritos y pedidos.", language: "TypeScript", license: "MIT", stars: 28000, forks: 2900, topics: ["ecommerce", "headless", "payments"], last_commit_at: "2026-10-19T12:00:00Z", category: cat("Pagos y Comercio"), metrics: { health_score: 90, health_status: "Activo" } },
  { id: 109, name: "plausible", full_name: "plausible/analytics", description_es: "Analítica web ligera y respetuosa con la privacidad.", language: "Elixir", license: "AGPL-3.0", stars: 20000, forks: 1100, topics: ["analytics", "privacy"], last_commit_at: "2026-10-14T12:00:00Z", category: cat("Analítica"), metrics: { health_score: 79, health_status: "Activo" } },
  { id: 110, name: "novu", full_name: "novuhq/novu", description_es: "Infraestructura de notificaciones por correo, SMS, push y chat con una sola API.", language: "TypeScript", license: "MIT", stars: 35000, forks: 3500, topics: ["notifications", "email", "sms"], last_commit_at: "2026-10-21T08:00:00Z", category: cat("Notificaciones y Comunicación"), metrics: { health_score: 90, health_status: "Activo" } },
  { id: 111, name: "ejemplo-en-riesgo", full_name: "openbridge/ejemplo-en-riesgo", description_es: "Repositorio ficticio para mostrar el estado En riesgo.", language: "TypeScript", license: "MIT", stars: 1200, forks: 90, topics: ["ejemplo"], last_commit_at: "2026-06-15T12:00:00Z", category: cat("UI y Componentes"), metrics: { health_score: 48, health_status: "En riesgo" } },
  { id: 112, name: "ejemplo-sin-datos", full_name: "openbridge/ejemplo-sin-datos", description: "Fictional repository to show the unknown state.", description_es: null, language: "Go", license: null, stars: 3100, forks: 210, topics: [], last_commit_at: null, category: cat("Despliegue (PaaS)"), metrics: { health_score: 40, health_status: null } },
  { id: 113, name: "next-auth", full_name: "nextauthjs/next-auth", description_es: "Autenticación para Next.js y otros frameworks, con decenas de proveedores.", language: "TypeScript", license: "ISC", stars: 25000, forks: 3600, topics: ["nextjs", "oauth", "authentication"], last_commit_at: "2026-10-19T10:00:00Z", category: cat("Autenticación"), metrics: { health_score: 88, health_status: "Activo" } },
  { id: 114, name: "typesense", full_name: "typesense/typesense", description_es: "Búsqueda instantánea con filtros y facetas, pensada para catálogos.", language: "C++", license: "GPL-3.0", stars: 22000, forks: 700, topics: ["search", "facets", "instant-search"], last_commit_at: "2026-10-18T10:00:00Z", category: cat("Búsqueda"), metrics: { health_score: 87, health_status: "Activo" } },
  { id: 115, name: "lago", full_name: "getlago/lago", description_es: "Facturación por consumo y suscripciones para productos B2B.", language: "Ruby", license: "AGPL-3.0", stars: 8000, forks: 400, topics: ["billing", "usage-based", "subscriptions"], last_commit_at: "2026-10-16T10:00:00Z", category: cat("Pagos y Comercio"), metrics: { health_score: 82, health_status: "Activo" } },
  { id: 116, name: "umami", full_name: "umami-software/umami", description_es: "Analítica simple y autoalojada con panel propio.", language: "TypeScript", license: "MIT", stars: 30000, forks: 5000, topics: ["analytics", "self-hosted", "privacy"], last_commit_at: "2026-10-01T10:00:00Z", category: cat("Analítica"), metrics: { health_score: 66, health_status: "Activo" } },
  { id: 117, name: "ejemplo-archivado", full_name: "openbridge/ejemplo-archivado", description_es: "Repositorio ficticio para mostrar un proyecto archivado.", language: "Go", license: "MIT", stars: 4100, forks: 300, topics: ["ejemplo"], last_commit_at: "2025-09-30T12:00:00Z", category: cat("Despliegue (PaaS)"), metrics: { health_score: 0, health_status: "Abandonado" } },
];

export const MOCK_REPOSITORIES: RepositoryListItem[] = SEEDS.map((s, i) => ({
  ...s,
  description: s.description ?? s.description_es,
  github_id: 1000000 + i,
  url: `https://github.com/${s.full_name}`,
  pushed_at: s.last_commit_at,
}));

export const MOCK_CATEGORIES: Category[] = NAMES.map((name, i) => ({
  id: i + 1,
  name,
  repositories_count: MOCK_REPOSITORIES.filter((r) => r.category.id === i + 1).length,
}));

function paginate(items: RepositoryListItem[], page = 1, page_size = 10): PaginatedRepositories {
  return {
    total: items.length,
    page,
    page_size,
    total_pages: Math.max(1, Math.ceil(items.length / page_size)),
    items: items.slice((page - 1) * page_size, page * page_size),
  };
}

function sortItems(items: RepositoryListItem[], params: ListParams) {
  const key = params.sort_by ?? "stars";
  const dir = params.order === "asc" ? 1 : -1;
  const value = (r: RepositoryListItem) =>
    key === "health_score" ? r.metrics.health_score : key === "last_commit_at" ? Date.parse(r.last_commit_at ?? "1970-01-01") : r[key];
  return [...items].sort((a, b) => (value(a) - value(b)) * dir);
}

export function listMock(params: ListParams): PaginatedRepositories {
  return paginate(sortItems(MOCK_REPOSITORIES, params), params.page, params.page_size);
}

export function searchMock(params: SearchParams): PaginatedRepositories {
  const q = params.q?.toLowerCase().trim();
  const items = MOCK_REPOSITORIES.filter((r) => {
    if (q && ![r.name, r.description ?? "", r.description_es ?? "", ...r.topics].some((t) => t.toLowerCase().includes(q))) return false;
    if (params.category_id && r.category.id !== params.category_id) return false;
    if (params.language && r.language !== params.language) return false;
    if (params.license && r.license !== params.license) return false;
    if (params.health_status && r.metrics.health_status !== params.health_status) return false;
    if (params.min_stars && r.stars < params.min_stars) return false;
    return true;
  });
  return paginate(sortItems(items, params), params.page, params.page_size);
}

// Idea de integración de ejemplo del contrato (INT-016), para la ficha de qdrant.
const QDRANT_IDEA: Integration = {
  id: 16,
  code: "INT-016",
  purpose: "Asistente que responde preguntas sobre documentos internos sin enviar datos a terceros.",
  integration_type: "SDK / librería",
  triggers_or_webhooks: "Al cargar documentos (indexación) y en cada pregunta del usuario.",
  example_snippet:
    'from langchain_ollama import OllamaEmbeddings, ChatOllama\nfrom langchain_qdrant import QdrantVectorStore\n\nemb = OllamaEmbeddings(model="nomic-embed-text", base_url="http://ollama:11434")\nstore = QdrantVectorStore.from_documents(fragmentos, emb,\n    url="http://qdrant:6333", collection_name="docs_internos")\nllm = ChatOllama(model="llama3.1", base_url="http://ollama:11434")',
  compatible_stack: ["Python 3.10+", "LangChain", "Ollama", "Qdrant", "Docker"],
  main_steps: [
    "Extraer y fragmentar los documentos.",
    "Indexarlos en Qdrant con embeddings de Ollama.",
    "Recuperar los fragmentos más parecidos a la pregunta.",
    "Generar la respuesta con el modelo local usando solo ese contexto.",
  ],
  difficulty: "Media",
  role: "Almacenamiento y búsqueda de los fragmentos de los documentos",
  documentation_url: "https://docs.langchain.com/oss/python/integrations/vectorstores/qdrant",
  related_repositories: [
    { id: 107, full_name: "langchain-ai/langchain", role: "Orquestación del flujo RAG" },
    { id: 106, full_name: "ollama/ollama", role: "Embeddings y respuestas con un modelo local" },
  ],
  business_cases: [
    { id: 13, name: "Un asistente con IA que responde preguntas sobre documentos internos." },
    { id: 12, name: "Una mesa de ayuda con chat y respuestas automáticas con IA." },
  ],
};

const DOCKER_IDEA = (repo: RepositoryListItem): Integration => ({
  id: repo.id * 10,
  code: `INT-${repo.id}`,
  purpose: `Levantar ${repo.name} como servicio del stack y conectarlo desde el backend.`,
  integration_type: "Docker",
  triggers_or_webhooks: "Al iniciar el servicio y en cada llamada del backend.",
  example_snippet: `docker compose up -d ${repo.name}`,
  compatible_stack: ["Docker", "Next.js", "FastAPI"],
  main_steps: ["Agregar el servicio al docker-compose.", "Configurar las variables de entorno.", "Conectar el backend al servicio."],
  difficulty: "Baja",
  role: null,
  documentation_url: `https://github.com/${repo.full_name}#readme`,
  related_repositories: [],
  business_cases: [],
});

export function getMockDetail(id: number): RepositoryDetail | null {
  const repo = MOCK_REPOSITORIES.find((r) => r.id === id);
  if (!repo) return null;
  const unknown = repo.metrics.health_status === null;
  return {
    ...repo,
    homepage: repo.id === 101 ? "https://qdrant.tech" : null,
    detected_stack: [repo.language ?? "Sin datos", "Docker", "REST API"],
    integration_methods_suggested: ["API REST", "Docker"],
    open_issues: Math.round(repo.stars / 150),
    has_issues: true,
    issues_url: null,
    archived: repo.id === 117,
    maintainer_active: unknown ? null : repo.id !== 117 && repo.id !== 111,
    synced_at: "2026-10-22T08:00:00Z",
    metrics: {
      ...repo.metrics,
      health_score_details: repo.id === 117
        ? { maintenance: 0, commit_activity: 0, popularity: 0, forks: 0 }
        : unknown
        ? { maintenance: 5, commit_activity: null, popularity: 12, forks: 5 }
        : { maintenance: 30, commit_activity: 21, popularity: 15, forks: 7 },
      commits_last_30_days: unknown ? null : 42,
      commits_last_90_days: unknown ? null : 135,
      commits_last_year: unknown ? null : 580,
      commit_activity_status: unknown ? "unavailable" : "available",
      measured_at: "2026-10-22T08:00:00Z",
    },
    integrations: repo.id === 101 ? [QDRANT_IDEA] : [DOCKER_IDEA(repo)],
  };
}
