export type Category = {
  id: number;
  name: string;
  repositories_count: number;
};

export type RepositoryListItem = {
  id: number;
  github_id: number;
  name: string;
  full_name: string;
  url: string;
  description: string;
  description_es: string | null;
  language: string | null;
  license: string | null;
  stars: number;
  forks: number;
  topics: string[];
  pushed_at: string;
  category: { id: number; name: string };
  metrics: { health_score: number; health_status: string };
};

export type PaginatedRepositories = {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  items: RepositoryListItem[];
};

export type RepositoryDetail = RepositoryListItem & {
  health_score_details: Record<string, number>;
};
