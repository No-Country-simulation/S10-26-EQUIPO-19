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
};

export type PaginatedRepositories = {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  items: RepositoryListItem[];
};

/** Parámetros del listado paginado (2.2). */
export type ListParams = {
  page?: number;
  page_size?: number;
  sort_by?: "stars" | "forks" | "last_commit_at" | "health_score";
  order?: "asc" | "desc";
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
