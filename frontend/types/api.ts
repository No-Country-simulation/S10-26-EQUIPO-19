// Tipos alineados con el contrato de API (docs/api-contract.md, secciones 2.1 a 2.4).

export type HealthStatus = "Activo" | "En riesgo" | "Abandonado";

export type Category = {
  id: number;
  name: string;
  repositories_count: number | null;
};

export type CategoryRef = {
  id: number;
  name: string;
};

export type RepositoryMetricsSummary = {
  health_score: number;
  /** null cuando se desconoce la fecha del último commit: la interfaz muestra "Sin datos". */
  health_status: HealthStatus | null;
};

/** Alerta de riesgo por mantenimiento o licencia (9.3). */
export type RepositoryAlert = {
  type: "maintenance" | "license" | string;
  title: string;
  message: string;
};

export type RepositoryListItem = {
  id: number;
  github_id: number;
  name: string;
  full_name: string;
  url: string;
  description: string | null;
  description_es: string | null;
  language: string | null;
  license: string | null;
  stars: number;
  forks: number;
  topics: string[];
  /** Último commit de la rama principal: es la "última actualización" que se muestra. */
  last_commit_at: string | null;
  pushed_at: string | null;
  category: CategoryRef;
  metrics: RepositoryMetricsSummary;
  /** Alertas de riesgo (9.3). Puede faltar si la API todavía no las entrega. */
  alerts?: RepositoryAlert[];
};

export type PaginatedRepositories = {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  items: RepositoryListItem[];
};

export type SortBy = "stars" | "forks" | "last_commit_at" | "health_score";
export type SortOrder = "asc" | "desc";

/** Parámetros del listado paginado (2.2). */
export type ListParams = {
  page?: number;
  page_size?: number;
  sort_by?: SortBy;
  order?: SortOrder;
};

/** Parámetros de la búsqueda con filtros (2.3): los 5 filtros de la consigna más estrellas mínimas. */
export type SearchParams = {
  q?: string;
  category_id?: number;
  language?: string;
  license?: string;
  health_status?: HealthStatus;
  min_stars?: number;
  page?: number;
  page_size?: number;
  /** Orden de los resultados. Pendiente de agregar a la búsqueda en la API (3.5); hoy solo lo usa el listado. */
  sort_by?: SortBy;
  order?: SortOrder;
};

/** Desglose del health score. Un componente que no se pudo calcular vale null. */
export type HealthScoreDetails = {
  maintenance: number | null;
  commit_activity: number | null;
  popularity: number | null;
  forks: number | null;
};

export type RepositoryMetricsDetail = RepositoryMetricsSummary & {
  health_score_details: HealthScoreDetails | null;
  commits_last_30_days: number | null;
  commits_last_90_days: number | null;
  commits_last_year: number | null;
  commit_activity_status: "available" | "unavailable" | null;
  measured_at: string | null;
};

export type RelatedRepository = {
  id: number;
  full_name: string;
  role: string | null;
};

export type BusinessCase = {
  id: number;
  name: string;
};

/** Idea de integración con los cinco campos de la consigna. */
export type Integration = {
  id: number;
  code: string;
  purpose: string;
  integration_type: string;
  triggers_or_webhooks: string | null;
  example_snippet: string | null;
  compatible_stack: string[];
  main_steps: string[];
  difficulty: string;
  role: string | null;
  documentation_url: string | null;
  related_repositories: RelatedRepository[];
  business_cases: BusinessCase[];
};

/** Ficha técnica (2.4). */
export type RepositoryDetail = Omit<RepositoryListItem, "metrics"> & {
  homepage: string | null;
  detected_stack: string[];
  integration_methods_suggested: string[];
  open_issues: number;
  has_issues: boolean;
  issues_url: string | null;
  archived: boolean;
  maintainer_active: boolean | null;
  synced_at: string | null;
  metrics: RepositoryMetricsDetail;
  integrations: Integration[];
};

/** Asistente consultor (4.4): mensaje del historial. */
export type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

export type ChatSource = {
  repository_id: number;
  name: string;
  full_name: string;
  url: string;
  relevance_score: number;
};

export type ArchitectureComponent = {
  key: string;
  repository_id: number;
  full_name: string;
  role: string;
  license: string | null;
  health_status: HealthStatus | null;
  justification: string;
  alerts?: RepositoryAlert[];
};

export type ArchitectureConnection = {
  from: string;
  to: string;
  label: string;
  verified: boolean;
  integration_code: string | null;
};

export type ChatResponse = {
  answer: string;
  sources: ChatSource[];
  suggested_questions: string[];
  architecture: { components: ArchitectureComponent[]; connections: ArchitectureConnection[] } | null;
};

/** Comparador lado a lado (9.5): fichas completas de 2 o 3 repositorios. */
export type CompareResponse = {
  repositories: RepositoryDetail[];
  same_category: boolean;
  category_name: string | null;
};

/** 9.2 · docker-compose de arranque. POST /compose con los full_name del stack recomendado. */
export type ComposeRequest = { repositories: string[] };

export type ComposeService = {
  full_name: string;
  service: string;
  image: string;
  ports: string[];
};

export type ComposeSkipped = {
  full_name: string;
  /** Motivo legible, por ejemplo: "Es una librería: se instala como dependencia". */
  reason: string;
};

export type ComposeResponse = {
  filename: string;
  /** Contenido YAML listo para guardar como docker-compose.yml. */
  content: string;
  services: ComposeService[];
  skipped: ComposeSkipped[];
  warnings: string[];
};
