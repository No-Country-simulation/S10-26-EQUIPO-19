// Datos de ejemplo para desarrollar la interfaz mientras la API no esté disponible.
// Se activan con NEXT_PUBLIC_USE_MOCK=true (ver .env.example).
import type { Category, PaginatedRepositories, RepositoryListItem, SearchParams } from "@/types/api";

const NAMES = [
  "Autenticación", "Base de Datos y Backend", "Búsqueda Vectorial", "Pagos y Comercio", "IA y LLM",
  "Analítica", "Búsqueda", "Almacenamiento de Archivos", "Mensajería y Colas", "Notificaciones y Comunicación",
  "Automatización y Workflows", "Observabilidad y Monitoreo", "CMS y Contenido", "Feature Flags",
  "API Gateway y Proxy", "Despliegue (PaaS)", "Herramientas para APIs", "Herramientas de Negocio",
  "Paneles Internos y Low-code", "Seguridad y Secretos", "UI y Componentes", "Geolocalización y Logística",
  "Video y Tiempo Real", "Educación (LMS)", "IoT y Series de Tiempo",
];

export const MOCK_CATEGORIES: Category[] = NAMES.map((name, i) => ({ id: i + 1, name, repositories_count: 5 }));

export const MOCK_REPOSITORIES: RepositoryListItem[] = [
  {
    id: 101, github_id: 10567832, name: "qdrant", full_name: "qdrant/qdrant", url: "https://github.com/qdrant/qdrant",
    description: "Vector Similarity Search Engine and Vector Database",
    description_es: "Motor de búsqueda por similitud vectorial y base de datos vectorial para IA de alto rendimiento.",
    language: "Rust", license: "Apache-2.0", stars: 19500, forks: 1400,
    topics: ["vector-search", "database", "rust"], last_commit_at: "2026-10-21T12:00:00Z", pushed_at: "2026-10-21T18:30:00Z",
    category: { id: 3, name: "Búsqueda Vectorial" }, metrics: { health_score: 91, health_status: "Activo" },
  },
  {
    id: 102, github_id: 23489110, name: "chroma", full_name: "chroma-core/chroma", url: "https://github.com/chroma-core/chroma",
    description: "the AI-native open-source embedding database",
    description_es: "Base de datos de embeddings nativa para inteligencia artificial, ligera y de fácil integración.",
    language: "Python", license: "Apache-2.0", stars: 14200, forks: 1150,
    topics: ["embedding", "database", "python"], last_commit_at: "2026-10-20T12:00:00Z", pushed_at: "2026-10-20T14:15:00Z",
    category: { id: 3, name: "Búsqueda Vectorial" }, metrics: { health_score: 92, health_status: "Activo" },
  },
  {
    id: 103, github_id: 4085811, name: "keycloak", full_name: "keycloak/keycloak", url: "https://github.com/keycloak/keycloak",
    description: "Open Source Identity and Access Management",
    description_es: "Gestión de identidad y acceso open source, con inicio de sesión único (SSO) y OIDC.",
    language: "Java", license: "Apache-2.0", stars: 25000, forks: 7000,
    topics: ["sso", "oidc", "authentication"], last_commit_at: "2026-10-22T09:00:00Z", pushed_at: "2026-10-22T09:00:00Z",
    category: { id: 1, name: "Autenticación" }, metrics: { health_score: 95, health_status: "Activo" },
  },
  {
    id: 104, github_id: 5000001, name: "ejemplo-en-riesgo", full_name: "openbridge/ejemplo-en-riesgo", url: "https://github.com/",
    description: "Repositorio ficticio para mostrar el estado En riesgo.",
    description_es: "Repositorio ficticio para mostrar el estado En riesgo.",
    language: "TypeScript", license: "MIT", stars: 1200, forks: 90,
    topics: ["ejemplo"], last_commit_at: "2026-06-15T12:00:00Z", pushed_at: "2026-06-15T12:00:00Z",
    category: { id: 21, name: "UI y Componentes" }, metrics: { health_score: 48, health_status: "En riesgo" },
  },
  {
    id: 105, github_id: 5000002, name: "ejemplo-sin-datos", full_name: "openbridge/ejemplo-sin-datos", url: "https://github.com/",
    description: "Repositorio ficticio para mostrar el estado Sin datos.",
    description_es: null,
    language: "Go", license: null, stars: 3100, forks: 210,
    topics: [], last_commit_at: null, pushed_at: null,
    category: { id: 16, name: "Despliegue (PaaS)" }, metrics: { health_score: 40, health_status: null },
  },
];

export function filterMock(params: SearchParams): PaginatedRepositories {
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
  const page_size = params.page_size ?? 10;
  const page = params.page ?? 1;
  return {
    total: items.length,
    page,
    page_size,
    total_pages: Math.max(1, Math.ceil(items.length / page_size)),
    items: items.slice((page - 1) * page_size, page * page_size),
  };
}
