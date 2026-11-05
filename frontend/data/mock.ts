// Datos de ejemplo para desarrollar y probar la interfaz mientras la API no esté disponible.
// Se activan con NEXT_PUBLIC_USE_MOCK=true (ver .env.example). Las métricas no son reales.
import type {
  ChatResponse,
  CompareResponse,
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
  { id: 1, name: "keycloak", full_name: "keycloak/keycloak", description_es: "Gestión de identidades y accesos con inicio de sesión único (SSO), OIDC y SAML.", language: "Java", license: "Apache-2.0", stars: 25000, forks: 7000, topics: ["sso", "oidc", "authentication"], last_commit_at: "2026-10-22T09:00:00Z", category: cat("Autenticación"), metrics: { health_score: 95, health_status: "Activo" } },
  { id: 104, name: "supabase", full_name: "supabase/supabase", description_es: "Postgres con API automática, autenticación, almacenamiento y pgvector listos para usar.", language: "TypeScript", license: "Apache-2.0", stars: 80000, forks: 8000, topics: ["postgres", "backend", "realtime"], last_commit_at: "2026-10-22T15:00:00Z", category: cat("Base de Datos y Backend"), metrics: { health_score: 97, health_status: "Activo" } },
  { id: 105, name: "meilisearch", full_name: "meilisearch/meilisearch", description_es: "Motor de búsqueda rápido con tolerancia a errores de escritura.", language: "Rust", license: "MIT", stars: 50000, forks: 1900, topics: ["search-engine", "full-text-search"], last_commit_at: "2026-10-20T10:00:00Z", category: cat("Búsqueda"), metrics: { health_score: 93, health_status: "Activo" } },
  { id: 106, name: "ollama", full_name: "ollama/ollama", description_es: "Ejecuta modelos de lenguaje abiertos en tu propia máquina o servidor.", language: "Go", license: "MIT", stars: 100000, forks: 8500, topics: ["llm", "llama", "local-ai"], last_commit_at: "2026-10-22T18:00:00Z", category: cat("IA y LLM"), metrics: { health_score: 95, health_status: "Activo" } },
  { id: 107, name: "langchain", full_name: "langchain-ai/langchain", description_es: "Framework para encadenar modelos, herramientas y recuperación de datos.", language: "Python", license: "MIT", stars: 100000, forks: 16000, topics: ["llm", "rag", "agents"], last_commit_at: "2026-10-22T11:00:00Z", category: cat("IA y LLM"), metrics: { health_score: 92, health_status: "Activo" } },
  { id: 108, name: "medusa", full_name: "medusajs/medusa", description_es: "Backend de comercio electrónico modular con pagos, carritos y pedidos.", language: "TypeScript", license: "MIT", stars: 28000, forks: 2900, topics: ["ecommerce", "headless", "payments"], last_commit_at: "2026-10-19T12:00:00Z", category: cat("Pagos y Comercio"), metrics: { health_score: 90, health_status: "Activo" } },
  { id: 109, name: "plausible", full_name: "plausible/analytics", description_es: "Analítica web ligera y respetuosa con la privacidad.", language: "Elixir", license: "AGPL-3.0", stars: 20000, forks: 1100, topics: ["analytics", "privacy"], last_commit_at: "2026-10-14T12:00:00Z", category: cat("Analítica"), metrics: { health_score: 79, health_status: "Activo" } },
  { id: 75, name: "novu", full_name: "novuhq/novu", description_es: "Infraestructura de notificaciones por correo, SMS, push y chat con una sola API.", language: "TypeScript", license: "MIT", stars: 35000, forks: 3500, topics: ["notifications", "email", "sms"], last_commit_at: "2026-10-21T08:00:00Z", category: cat("Notificaciones y Comunicación"), metrics: { health_score: 90, health_status: "Activo" } },
  { id: 111, name: "ejemplo-en-riesgo", full_name: "openbridge/ejemplo-en-riesgo", description_es: "Repositorio ficticio para mostrar el estado En riesgo.", language: "TypeScript", license: "MIT", stars: 1200, forks: 90, topics: ["ejemplo"], last_commit_at: "2026-06-15T12:00:00Z", category: cat("UI y Componentes"), metrics: { health_score: 48, health_status: "En riesgo" } },
  { id: 112, name: "ejemplo-sin-datos", full_name: "openbridge/ejemplo-sin-datos", description: "Fictional repository to show the unknown state.", description_es: null, language: "Go", license: null, stars: 3100, forks: 210, topics: [], last_commit_at: null, category: cat("Despliegue (PaaS)"), metrics: { health_score: 40, health_status: null } },
  { id: 2, name: "next-auth", full_name: "nextauthjs/next-auth", description_es: "Autenticación para Next.js y otros frameworks, con decenas de proveedores.", language: "TypeScript", license: "ISC", stars: 25000, forks: 3600, topics: ["nextjs", "oauth", "authentication"], last_commit_at: "2026-10-19T10:00:00Z", category: cat("Autenticación"), metrics: { health_score: 88, health_status: "Activo" } },
  { id: 114, name: "typesense", full_name: "typesense/typesense", description_es: "Búsqueda instantánea con filtros y facetas, pensada para catálogos.", language: "C++", license: "GPL-3.0", stars: 22000, forks: 700, topics: ["search", "facets", "instant-search"], last_commit_at: "2026-10-18T10:00:00Z", category: cat("Búsqueda"), metrics: { health_score: 87, health_status: "Activo" } },
  { id: 115, name: "lago", full_name: "getlago/lago", description_es: "Facturación por consumo y suscripciones para productos B2B.", language: "Ruby", license: "AGPL-3.0", stars: 8000, forks: 400, topics: ["billing", "usage-based", "subscriptions"], last_commit_at: "2026-10-16T10:00:00Z", category: cat("Pagos y Comercio"), metrics: { health_score: 82, health_status: "Activo" } },
  { id: 116, name: "umami", full_name: "umami-software/umami", description_es: "Analítica simple y autoalojada con panel propio.", language: "TypeScript", license: "MIT", stars: 30000, forks: 5000, topics: ["analytics", "self-hosted", "privacy"], last_commit_at: "2026-10-01T10:00:00Z", category: cat("Analítica"), metrics: { health_score: 66, health_status: "Activo" } },
  { id: 117, name: "ejemplo-archivado", full_name: "openbridge/ejemplo-archivado", description_es: "Repositorio ficticio para mostrar un proyecto archivado.", language: "Go", license: "MIT", stars: 4100, forks: 300, topics: ["ejemplo"], last_commit_at: "2025-09-30T12:00:00Z", category: cat("Despliegue (PaaS)"), metrics: { health_score: 0, health_status: "Abandonado" } },
  // Herramientas de los ejemplos del asistente (casos 1 y 2 del inventario), con su id real del catálogo.
  { id: 35, name: "saleor", full_name: "saleor/saleor", description_es: "Plataforma de e-commerce headless con API GraphQL.", language: "Python", license: "BSD-3-Clause", stars: 22000, forks: 5500, topics: ["ecommerce", "graphql", "headless"], last_commit_at: "2026-10-21T12:00:00Z", category: cat("Pagos y Comercio"), metrics: { health_score: 92, health_status: "Activo" } },
  { id: 87, name: "trigger.dev", full_name: "triggerdotdev/trigger.dev", description_es: "Tareas en segundo plano y flujos para TypeScript.", language: "TypeScript", license: "Apache-2.0", stars: 12000, forks: 800, topics: ["background-jobs", "workflows"], last_commit_at: "2026-10-22T12:00:00Z", category: cat("Automatización y Workflows"), metrics: { health_score: 90, health_status: "Activo" } },
  { id: 241, name: "osrm-backend", full_name: "Project-OSRM/osrm-backend", description_es: "Motor de cálculo de rutas sobre datos de OpenStreetMap.", language: "C++", license: "BSD-2-Clause", stars: 7000, forks: 3500, topics: ["routing", "openstreetmap"], last_commit_at: "2026-10-15T12:00:00Z", category: cat("Geolocalización y Logística"), metrics: { health_score: 84, health_status: "Activo" } },
  { id: 247, name: "traccar", full_name: "traccar/traccar", description_es: "Seguimiento GPS de vehículos y flotas.", language: "Java", license: "Apache-2.0", stars: 6000, forks: 2700, topics: ["gps", "fleet-tracking"], last_commit_at: "2026-10-20T12:00:00Z", category: cat("Geolocalización y Logística"), metrics: { health_score: 86, health_status: "Activo" } },
  { id: 224, name: "ToolJet", full_name: "ToolJet/ToolJet", description_es: "Plataforma low-code para aplicaciones internas.", language: "JavaScript", license: "AGPL-3.0", stars: 35000, forks: 4800, topics: ["low-code", "internal-tools"], last_commit_at: "2026-10-22T12:00:00Z", category: cat("Paneles Internos y Low-code"), metrics: { health_score: 91, health_status: "Activo" } },
  { id: 218, name: "cal.diy", full_name: "calcom/cal.diy", description_es: "Agendamiento de reuniones, alternativa a Calendly.", language: "TypeScript", license: "MIT", stars: 38000, forks: 9000, topics: ["scheduling", "calendar"], last_commit_at: "2026-10-22T12:00:00Z", category: cat("Herramientas de Negocio"), metrics: { health_score: 93, health_status: "Activo" } },
  { id: 12, name: "postgres", full_name: "postgres/postgres", description_es: "Base de datos relacional PostgreSQL (mirror oficial).", language: "C", license: "PostgreSQL", stars: 18000, forks: 5000, topics: ["database", "sql"], last_commit_at: "2026-10-22T12:00:00Z", category: cat("Base de Datos y Backend"), metrics: { health_score: 94, health_status: "Activo" } },
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
  documentation_url: "https://docs.langchain.com/oss/python/integrations/vectorstores/qdrant ; https://qdrant.tech/documentation/",
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

/** Respuesta de ejemplo del asistente, para trabajar sin la API (NEXT_PUBLIC_USE_MOCK=true). */
// Respuestas de ejemplo del asistente, armadas solo con herramientas del catálogo y con las ideas de
// integración aprobadas de los casos de negocio 1 (B2B de logística) y 2 (clínicas) del inventario.
const src = (repository_id: number, full_name: string, relevance_score: number) => ({
  repository_id,
  name: full_name.split("/")[1],
  full_name,
  url: `https://github.com/${full_name}`,
  relevance_score,
});
const agpl = (license: string) => ({
  type: "license",
  title: `Licencia ${license}`,
  message: `Licencia ${license}: si la ofreces como servicio (SaaS) con cambios, debes publicar el código modificado.`,
});

const CASE_LOGISTICS: ChatResponse = {
  answer:
    "Para tu e-commerce B2B de logística te propongo seis piezas del catálogo: **Keycloak** para que cada empresa inicie sesión, **Saleor** como tienda (catálogo, pedidos y pagos), **Trigger.dev** para procesar cada pedido en segundo plano, **OSRM** para planificar las rutas de reparto, **Traccar** para seguir la flota y **ToolJet** para el panel de bodega. Ojo: ToolJet tiene licencia AGPL-3.0.",
  sources: [src(35, "saleor/saleor", 0.91), src(1, "keycloak/keycloak", 0.87), src(241, "Project-OSRM/osrm-backend", 0.84), src(247, "traccar/traccar", 0.81), src(87, "triggerdotdev/trigger.dev", 0.78)],
  suggested_questions: ["¿Cómo proceso cada pedido de Saleor en segundo plano?", "¿Qué implica la licencia AGPL-3.0 de ToolJet?"],
  architecture: {
    components: [
      { key: "auth", repository_id: 1, full_name: "keycloak/keycloak", role: "Inicio de sesión y cuentas de cada empresa", license: "Apache-2.0", health_status: "Activo", justification: "SSO con OIDC y SAML, con roles por empresa cliente.", alerts: [] },
      { key: "tienda", repository_id: 35, full_name: "saleor/saleor", role: "Tienda B2B: catálogo, pedidos y pagos", license: "BSD-3-Clause", health_status: "Activo", justification: "E-commerce headless con API GraphQL y webhooks por cada pedido.", alerts: [] },
      { key: "procesos", repository_id: 87, full_name: "triggerdotdev/trigger.dev", role: "Procesa cada pedido en segundo plano", license: "Apache-2.0", health_status: "Activo", justification: "Reserva stock, emite la factura y avisa al cliente sin frenar la tienda.", alerts: [] },
      { key: "rutas", repository_id: 241, full_name: "Project-OSRM/osrm-backend", role: "Planifica las rutas de reparto", license: "BSD-2-Clause", health_status: "Activo", justification: "Calcula rutas y tiempos reales de calle sobre OpenStreetMap.", alerts: [] },
      { key: "flota", repository_id: 247, full_name: "traccar/traccar", role: "Seguimiento GPS de la flota", license: "Apache-2.0", health_status: "Activo", justification: "Recibe la ubicación de cada vehículo y emite eventos en tiempo real.", alerts: [] },
      { key: "panel", repository_id: 224, full_name: "ToolJet/ToolJet", role: "Panel de bodega con despachos pendientes", license: "AGPL-3.0", health_status: "Activo", justification: "Arma el panel interno en horas, conectado a la API de la tienda.", alerts: [agpl("AGPL-3.0")] },
    ],
    connections: [
      { from: "auth", to: "tienda", label: "Valida la sesión de cada empresa con OIDC antes de comprar", verified: false, integration_code: null },
      { from: "tienda", to: "procesos", label: "Envía cada pedido nuevo para reservar stock, facturar y avisar al cliente", verified: true, integration_code: "INT-051" },
      { from: "procesos", to: "rutas", label: "Agrupa los pedidos del día y pide las rutas de reparto", verified: false, integration_code: null },
      { from: "rutas", to: "flota", label: "Asigna cada ruta a un vehículo y sigue su avance", verified: false, integration_code: null },
      { from: "tienda", to: "panel", label: "Muestra a bodega los despachos pendientes y el stock crítico", verified: false, integration_code: null },
    ],
  },
};

const CASE_CLINICS: ChatResponse = {
  answer:
    "Para que las clínicas agenden citas te propongo **Cal.diy** para la agenda, **Novu** para los recordatorios, **Auth.js** con **Keycloak** para las cuentas de pacientes y **PostgreSQL** como base de datos. Para el pago en línea, el catálogo todavía no tiene una idea de integración revisada para este caso: conviene evaluarlo aparte.",
  sources: [src(218, "calcom/cal.diy", 0.9), src(75, "novuhq/novu", 0.86), src(1, "keycloak/keycloak", 0.83), src(2, "nextauthjs/next-auth", 0.8), src(12, "postgres/postgres", 0.74)],
  suggested_questions: ["¿Cómo envío recordatorios de citas con Novu?", "¿Cómo agrego el inicio de sesión con Keycloak?"],
  architecture: {
    components: [
      { key: "login", repository_id: 2, full_name: "nextauthjs/next-auth", role: "Inicio de sesión en la app Next.js", license: "ISC", health_status: "Activo", justification: "Conecta la app con Keycloak en pocas líneas.", alerts: [] },
      { key: "auth", repository_id: 1, full_name: "keycloak/keycloak", role: "Cuentas de pacientes y del personal", license: "Apache-2.0", health_status: "Activo", justification: "SSO con roles para pacientes, recepción y médicos.", alerts: [] },
      { key: "agenda", repository_id: 218, full_name: "calcom/cal.diy", role: "Agenda de citas de cada clínica", license: "MIT", health_status: "Activo", justification: "Agendamiento autoalojado, alternativa a Calendly.", alerts: [] },
      { key: "avisos", repository_id: 75, full_name: "novuhq/novu", role: "Recordatorios por correo, SMS o push", license: "MIT", health_status: "Activo", justification: "Una sola API para todos los canales de aviso.", alerts: [] },
      { key: "datos", repository_id: 12, full_name: "postgres/postgres", role: "Base de datos de citas y pacientes", license: "PostgreSQL", health_status: "Activo", justification: "Base relacional robusta y ampliamente soportada.", alerts: [] },
    ],
    connections: [
      { from: "login", to: "auth", label: "Inicia sesión con OIDC sin construir un sistema de usuarios propio", verified: true, integration_code: "INT-001" },
      { from: "login", to: "agenda", label: "Da acceso al paciente a su agenda", verified: false, integration_code: null },
      { from: "agenda", to: "avisos", label: "Envía recordatorios automáticos de cada cita", verified: true, integration_code: "INT-005" },
      { from: "agenda", to: "datos", label: "Guarda las citas y los datos de pacientes", verified: false, integration_code: null },
    ],
  },
};

const followUp = (answer: string, sources: ChatResponse["sources"]): ChatResponse => ({ answer, sources, suggested_questions: [], architecture: null });

const FOLLOW_UPS: Record<string, ChatResponse> = {
  "¿Cómo proceso cada pedido de Saleor en segundo plano?": followUp(
    "Usa la idea **INT-051** del catálogo: Saleor emite un webhook por cada pedido nuevo y **Trigger.dev** ejecuta la tarea en segundo plano (reservar stock, emitir la factura y avisar al cliente), así la tienda sigue respondiendo rápido. Revisa los pasos y el snippet en la ficha de Saleor.",
    [src(35, "saleor/saleor", 0.93), src(87, "triggerdotdev/trigger.dev", 0.9)],
  ),
  "¿Qué implica la licencia AGPL-3.0 de ToolJet?": followUp(
    "**ToolJet** usa AGPL-3.0: si lo modificas y lo ofreces como servicio (SaaS) a terceros, debes publicar el código modificado. Para un panel interno de bodega, usado solo por tu equipo, normalmente no hay obligación adicional, pero conviene que el área legal lo confirme.",
    [src(224, "ToolJet/ToolJet", 0.9)],
  ),
  "¿Cómo envío recordatorios de citas con Novu?": followUp(
    "Usa la idea **INT-005** del catálogo: **Cal.diy** avisa por webhook cada vez que se agenda o cambia una cita, y **Novu** envía el recordatorio por correo, SMS o push en el momento que definas, sin programarlo a mano.",
    [src(218, "calcom/cal.diy", 0.92), src(75, "novuhq/novu", 0.9)],
  ),
  "¿Cómo agrego el inicio de sesión con Keycloak?": followUp(
    "Usa la idea **INT-001** del catálogo: creas un realm y un cliente en **Keycloak**, registras la URL de retorno y configuras el proveedor de Keycloak en **Auth.js** dentro de la app Next.js. Los pasos y el snippet están en la ficha de Keycloak.",
    [src(1, "keycloak/keycloak", 0.94), src(2, "nextauthjs/next-auth", 0.88)],
  ),
};

/** Respuesta de ejemplo según la consulta (solo para NEXT_PUBLIC_USE_MOCK=true). */
export function mockChat(message: string): ChatResponse {
  const q = message.trim();
  if (FOLLOW_UPS[q]) return FOLLOW_UPS[q];
  if (/cl[ií]nica|cita|paciente/i.test(q)) return CASE_CLINICS;
  if (/log[ií]stica|reparto|flota|b2b/i.test(q)) return CASE_LOGISTICS;
  return followUp(
    "Estás en el modo de ejemplo: solo hay respuestas preparadas para los dos casos de ejemplo (e-commerce B2B de logística y clínicas). Prueba con uno de ellos o conecta la app a la API para consultar el catálogo completo.",
    [],
  );
}

export const MOCK_CHAT_RESPONSE: ChatResponse = CASE_LOGISTICS;

/** Comparación de ejemplo (9.5) armada con las fichas de ejemplo. */
export function compareMock(ids: number[]): CompareResponse | null {
  const repositories = ids.map((id) => getMockDetail(id));
  if (repositories.some((r) => !r)) return null;
  const list = repositories as RepositoryDetail[];
  const same = new Set(list.map((r) => r.category.id)).size === 1;
  return { repositories: list, same_category: same, category_name: same ? list[0].category.name : null };
}
