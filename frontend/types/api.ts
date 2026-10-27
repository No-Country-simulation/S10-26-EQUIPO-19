// Tipos alineados con el contrato de API (docs del backend, secciones 2.1 a 2.4).

export type HealthStatus = "Activo" | "En riesgo" | "Abandonado";

export type Category = {
  id: number;
  name: string;
  repositories_count: number;
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
